import asyncio
import json
import logging
from datetime import datetime
from typing import List, Union

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import StructuredTool, Tool
from langgraph.graph import END, START, StateGraph
from typing_extensions import Literal

from news_generator.src.prompts import (
    get_current_date,
    news_article_instructions,
    query_writer_instructions,
    summarise_web_research_results_instructions,
    validate_news_article_instructions,
)
from news_generator.src.state import SummaryState, SummaryStateInput, SummaryStateOutput
from news_generator.src.utils import (
    clean_apify_tweet_data,
    clean_for_voice,
    clean_response,
    create_mcp_tasks,
    extract_source_info,
    format_sources,
    get_twitter_sources_for_topic,
    get_telegram_sources_for_topic,
)

logger = logging.getLogger(__name__)


# Nodes
class NewsGenerator:
    def __init__(
        self,
        LLM,
        LLM_THINKING,
        tools: List[Union[Tool, StructuredTool]],
        news_memory: dict,
        agent_personality: dict,
        agent_name: str,
        research_topics: list,
        topics_file_path: str,
    ):
        self.llm = LLM
        self.llm_thinking = LLM_THINKING
        self.tools = tools
        self.news_memory = news_memory
        self.graph = self._build_graph()
        self.agent_personality = agent_personality
        self.agent_name = agent_name
        self.research_topics = research_topics
        self.topics_file_path = topics_file_path
        self.research_topics_counter = 0
        self.research_topics_total = len(research_topics) if research_topics else 0
        self.final_summaries = []
        logger.info(
            f"DeepResearcher initialized with LLM: {self.llm} and {self.tools} tools"
        )
        logger.info(f"Research topics: {self.research_topics}")
        logger.info(f"Research topics counter: {self.research_topics_counter}")
        logger.info(f"Research topics total: {self.research_topics_total}")

    def _build_graph(self):
        # Add nodes and edges
        builder = StateGraph(
            SummaryState, input=SummaryStateInput, output=SummaryStateOutput
        )
        builder.add_node("generate_query", self.generate_query)
        builder.add_node("web_research", self.web_research)
        builder.add_node("summarize_web_research", self.summarize_web_research)
        builder.add_node("create_news_article", self.create_news_article)
        builder.add_node("validate_news_article", self.validate_news_article)

        # Add edges
        builder.add_edge(START, "generate_query")
        builder.add_edge("generate_query", "web_research")
        builder.add_edge("web_research", "summarize_web_research")
        builder.add_conditional_edges(
            "summarize_web_research",
            self.route_topics,
            {
                "generate_query": "generate_query",
                "create_news_article": "create_news_article",
            },
        )
        builder.add_edge("create_news_article", "validate_news_article")
        builder.add_conditional_edges(
            "validate_news_article",
            self.route_news_article_validation,
            {"create_news_article": "create_news_article", END: END},
        )

        graph = builder.compile()
        logger.info("Graph compiled successfully")

        # Script to save the graph as an image file
        # Save the graph visualization as an image file
        # logger.info("Saving graph as image")
        # try:

        #     # Get the directory of the current file
        #     output_dir = os.path.dirname(os.path.abspath(__file__))
        #     output_path = os.path.join(output_dir, "news_generator_graph.png")

        #     # Save the graph visualization as a PNG file
        #     try:
        #         # Use the appropriate method to save the graph
        #         # The get_graph() method accesses the internal graph representation
        #         graph_image = graph.get_graph().draw_mermaid_png()
        #         with open(output_path, "wb") as f:
        #             f.write(graph_image)
        #         logger.info(f"Graph saved to {output_path}")
        #     except Exception as e:
        #         logger.error(f"Error saving graph: {e}")
        # except Exception as e:
        #     logger.error(f"Error saving graph: {e}")
        return graph

    async def generate_query(self, state: SummaryState, config: RunnableConfig):
        """LangGraph node that generates a search query based on the research topic.

        Uses an LLM to create an optimized search query for web research based on
        the user's research topic. Supports both LMStudio and Ollama as LLM providers.

        Args:
            state: Current graph state containing the research topic
            config: Configuration for the runnable, including LLM provider settings

        Returns:
            Dictionary with state update, including search_query key containing the generated query
        """
        logger.info("--- Starting Generate Query Node ---")
        logger.info(f"Research topics counter: {state.research_topics_counter}")
        # logger.info(f"Research topics: {state.research_topic}")
        current_topic = state.research_topic[state.research_topics_counter]
        logger.info(f"Current topic: {current_topic}")

        # Format the prompt
        current_date = get_current_date()
        formatted_prompt = query_writer_instructions.format(
            current_date=current_date, current_topic=current_topic
        )

        # Generate a query
        result = await self.llm.ainvoke(formatted_prompt)
        # Parse response directly to dict using JsonOutputParser
        result = JsonOutputParser().parse(clean_response(result.content))

        # Get the query and research topic
        search_query = result["query"]
        research_topic = result.get("research_topic", "General News Research")

        logger.info(f"Generated query: {search_query}")
        logger.info(f"Generated research topic: {research_topic}")

        state.search_query = search_query
        state.research_topic = state.research_topic

        return state

    async def web_research(self, state: SummaryState, config: RunnableConfig):
        """
        LangGraph node that performs parallel web research using multiple MCP servers.

        Executes searches, correctly parses and aggregates the results, and formats
        them for further processing.
        """
        logger.info("--- Starting Parallel Web Research Node ---")

        current_topic = state.research_topic[state.research_topics_counter]

        # Get the twitter sources for the topic
        twitter_sources = get_twitter_sources_for_topic(
            current_topic, self.topics_file_path
        )

        # Get the telegram sources for the topic
        telegram_sources = get_telegram_sources_for_topic(
            current_topic, self.topics_file_path
        )

        state.search_query = state.search_query
        logger.info(f"Search query: {state.search_query}")

        # 1. Create and execute tasks in parallel
        tasks, task_names = create_mcp_tasks(
            self.tools,
            state.search_query,
            topic=current_topic,
            twitter_sources=twitter_sources,
            telegram_sources=telegram_sources,
        )
        # return_exceptions=True is crucial for resilience
        parallel_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 2. Process the results in a single, clean loop
        all_raw_content = []
        all_structured_sources = []

        for i, result in enumerate(parallel_results):
            task_name = task_names[i]

            if isinstance(result, Exception):
                logger.error(f"  - Task '{task_name}' FAILED with error: {result}")
                # Optionally add error to raw content for LLM to know
                all_raw_content.append(f"Note: The search for '{task_name}' failed.")
                continue

            # This handles both string and tuple `(content, None)` results
            content = result[0] if isinstance(result, tuple) else result

            # If the content is a list, join it into a single string.
            if isinstance(content, list):
                content = "\n".join(map(str, content))

            # Clean the Apify data if the source is Twitter
            if "apidojo-slash-tweet-scraper" in task_name.lower():
                # logger.info(f"Cleaning Apify data: {content}")
                # await asyncio.sleep(10)
                content = clean_apify_tweet_data(content)

            # Ensure content is a string before stripping
            content = str(content)

            if not content or not content.strip():
                logger.warning(
                    f"  - Task '{task_name}' succeeded but returned empty content."
                )
                continue

            logger.info(f"  - Task '{task_name}' completed successfully.")
            all_raw_content.append(f"Source: {task_name}\n\n{content}")

            # Use helper to get structured info for citations
            source_info = extract_source_info(content, task_name)
            all_structured_sources.append(source_info)

        # 3. Aggregate and format the final outputs
        # A single string with all the raw content for the LLM
        search_str = "\n\n---\n\n".join(all_raw_content)
        # A single, formatted string of numbered sources for citation
        formatted_sources_str = format_sources(all_structured_sources)
        logger.info(f"Formatted sources: {formatted_sources_str}")

        # await asyncio.sleep(10)

        logger.info("--- Web Research Node Finished ---")

        state.web_research_results = [search_str]

        return state

    async def summarize_web_research(self, state: SummaryState, config: RunnableConfig):
        """LangGraph node that summarizes web research results.
        This node is used to create conciese summary of the web research results for the provided topic.
        """
        logger.info("--- Starting Summarize Web Research Node ---")

        current_topic = state.research_topic[state.research_topics_counter]
        logger.info(f"Current topic: {current_topic}")

        formatted_prompt = summarise_web_research_results_instructions.format(
            web_research_results=state.web_research_results, current_topic=current_topic
        )

        result = await self.llm.ainvoke(formatted_prompt)
        cleaned_response = clean_response(result.content)

        result = JsonOutputParser().parse(cleaned_response)

        # Extract the executive summary from the result
        summary_text = result.get("executive_summary", "No summary available.")

        self.final_summaries.append(
            f"------{current_topic}------\n\n{summary_text}\n\n------\n\n"
        )

        logger.info(f"Final summaries: {self.final_summaries}")
        state.research_topics_counter += 1
        state.research_topic = []
        state.web_research_results = []
        state.search_query = None
        return state

    def route_topics(
        self, state: SummaryState
    ) -> Literal["generate_query", "create_news_article"]:
        """
        Routes the graph between topics. It can move to the next topic or
        create a news article if all topics are done.
        """
        logger.info("--- Routing topics ---")
        if state.research_topics_counter < self.research_topics_total:
            logger.info(f"Moving to next topic, index {state.research_topics_counter}")
            return "generate_query"
        else:
            logger.info("All topics researched. Creating news article.")
            return "create_news_article"

    async def create_news_article(self, state: SummaryState, config: RunnableConfig):
        """LangGraph node that creates a news article based on the final report.

        Uses an LLM to create a news article based on the final report.
        """
        logger.info("--- Starting Create News Article Node ---")
        # Format the prompt
        SHOW_NAME = "Xyber Radio"
        current_date = get_current_date()
        current_time = datetime.now().strftime("%H:%M")
        topics = state.research_topic
        final_summaries_str = "\n".join(self.final_summaries)
        logger.info(f"Current article version: {state.current_article_version}")
        current_article_len = (
            len(state.current_article_version) if state.current_article_version else 0
        )

        formatted_prompt = news_article_instructions.format(
            current_date=current_date,
            current_time=current_time,
            news_memory=self.news_memory,
            final_report=final_summaries_str,
            agent_personality=self.agent_personality,
            show_name=SHOW_NAME,
            agent_name=self.agent_name,
            topics=topics,
            recommendations=state.recommendations or "",
            current_article_version=state.current_article_version or "",
            current_article_len=current_article_len,
        )

        attempts = 5
        for attempt in range(attempts):
            # Generate a news article
            result = await self.llm_thinking.ainvoke(formatted_prompt)
            try:
                # Get the content
                content = result.content
                # Parse response directly to dict using JsonOutputParser
                cleaned_response = clean_response(content)
                result = JsonOutputParser().parse(cleaned_response)

                # Get the title
                title = result["title"]
                # Get the content
                content = result["content"]

                # Clean all content for voice generation
                title_cleaned = clean_for_voice(title)
                content_cleaned = clean_for_voice(content)

                logger.info(f"News article created successfully: {title_cleaned}")
                state.news_article_title = title_cleaned
                state.news_article_content = content_cleaned
                state.current_article_version = state.news_article_content
                return state

            except json.JSONDecodeError:
                logger.error(
                    f"Failed to parse LLM output as JSON. Attempt {attempt + 1} of {attempts}"
                )
                continue

        # If we reach here, all attempts failed
        logger.error("Failed to create news article after all attempts.")
        state.news_article_title = "Error: Failed to Generate Article"
        state.news_article_content = "No news article content available"
        state.current_article_version = state.news_article_content
        return state

    async def validate_news_article(self, state: SummaryState, config: RunnableConfig):
        """LangGraph node that validates the news article."""
        logger.info("--- Starting Validate News Article Node ---")
        state.news_article_attempt += 1
        final_summaries_str = "\n".join(self.final_summaries)
        article_len = len(state.news_article_content)
        logger.info(f"Article length: {article_len}")

        formatted_prompt = validate_news_article_instructions.format(
            news_article=state.news_article_content,
            agent_personality=self.agent_personality,
            agent_name=self.agent_name,
            final_report=final_summaries_str,
            topics=self.research_topics,
            news_memory=self.news_memory,
        )
        try:
            result = await self.llm_thinking.ainvoke(formatted_prompt)
            cleaned_response = clean_response(result.content)
            result = JsonOutputParser().parse(cleaned_response)
            state.news_article_validated = result["validated"]
            state.recommendations = result["recommendations"]
            logger.info(f"News article validated: {state.news_article_validated}")
        except Exception as e:
            logger.error(f"An error occurred during article validation: {e}")
            state.news_article_validated = False
            state.recommendations = "Validation failed due to an error, possibly context length. The article will not be saved."

        logger.info(f"Recommendations: {state.recommendations}")
        return state

    def route_news_article_validation(
        self, state: SummaryState, config: RunnableConfig
    ) -> Literal["create_news_article", END]:
        """
        Routes the agent to either create a new news article, or end the process.
        """
        if state.news_article_validated:
            logger.info("News article has been validated. Proceeding to the END.")
            return END
        elif state.news_article_attempt < 3 and not state.news_article_validated:
            logger.info(
                f"News article validation failed. Retrying creation. Attempt {state.news_article_attempt + 1} of 3."
            )
            return "create_news_article"
        else:
            logger.error(
                "News article validation failed after 3 attempts. Ending the process."
            )
            state.news_article_content = "No news article content available"
            state.news_article_title = "Error: Failed to Generate Article"
            return END
