import asyncio
import logging
import sys
import os

# Removed unused typing imports

from langchain_mcp_adapters.client import MultiServerMCPClient


from config.config import (
    LLMSettings,
    SearchMCP_Config,
    ElevenLabsSettings,
    AgentConfig,
    MediaPaths,
)
from news_generator.src.graph import NewsGenerator
from news_generator.src.utils import (
    load_agent_personality,
    load_mcp_servers_config,
    load_news_memory,
    save_news_memory,
    load_json,
    initialize_llm,
)


from voice.generate import generate_voice

# Configure logging here (before any logger usage)
logging.basicConfig(
    level=logging.INFO,  # Or DEBUG for more detail
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  # Output to console
        logging.FileHandler(
            "researcher.log", encoding="utf-8"
        ),  # Optional: Output to a file
    ],
)

logger = logging.getLogger(__name__)


# Load the configuration
logger.info("Loading configuration...")
try:
    llm_config = LLMSettings()
    search_mcp_config = SearchMCP_Config()
    elevenlabs_config = ElevenLabsSettings()
    agent_config = AgentConfig()
    media_paths = MediaPaths()
    agent_personality = agent_config.agent_personality_path
    logger.info("Configuration loaded.")
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    sys.exit(1)


async def main(topic: str):
    # Initialize the Main LLM, with fallback to Spare on failure
    LLM = None
    try:
        LLM = initialize_llm(llm_config, llm_type="main", raise_on_error=True)
        if LLM:
            logger.info(f"Main LLM initialized: {type(LLM).__name__}")
    except Exception as e:
        logger.warning(f"Failed to initialize main LLM: {e}")
        logger.warning("Attempting to use spare LLM as main.")

    # Initialize the Spare LLM (only if main LLM failed or to set as fallback)
    LLM_SPARE = initialize_llm(llm_config, llm_type="spare", raise_on_error=False)
    if LLM_SPARE:
        logger.info(f"Spare LLM initialized: {type(LLM_SPARE).__name__}")

    # If main LLM failed, use spare as main
    if not LLM and LLM_SPARE:
        LLM = LLM_SPARE
        logger.info("Using spare LLM as the main LLM.")
    # If main LLM succeeded, add spare as fallback
    elif LLM and LLM_SPARE:
        LLM = LLM.with_fallbacks([LLM_SPARE])
        logger.info("Main LLM with fallbacks is ready.")

    # If still no LLM, we can't continue
    if not LLM:
        logger.critical("Could not initialize any LLM. Exiting.")
        sys.exit(1)

    # Initialize the Thinking LLM (returns None on failure)
    LLM_THINKING = initialize_llm(llm_config, llm_type="thinking", raise_on_error=False)
    if LLM_THINKING:
        logger.info(f"Thinking LLM initialized: {type(LLM_THINKING).__name__}")
        # Optionally, give the thinking LLM a fallback as well
        if LLM_SPARE:
            LLM_THINKING = LLM_THINKING.with_fallbacks([LLM_SPARE])
            logger.info("Thinking LLM with fallbacks is ready.")
    else:
        logger.warning("Thinking LLM could not be initialized. Continuing without it.")

    # Initialize the Validation LLM (returns None on failure)
    LLM_VALIDATION = initialize_llm(
        llm_config, llm_type="validation", raise_on_error=False
    )
    if LLM_VALIDATION:
        logger.info(f"Validation LLM initialized: {type(LLM_VALIDATION).__name__}")
    else:
        logger.warning(
            "Validation LLM could not be initialized. Continuing without it."
        )

    # Initialize the tools for data feeds
    # This block is dedicated to load the mcp servers and configure them
    # -----------------------------------------------------------#
    # -----------------------------------------------------------#
    # -----------------------------------------------------------#
    MCP_SERVERS_CONFIG = load_mcp_servers_config(
        apify_token=search_mcp_config.APIFY_TOKEN,
        mcp_tavily_url=search_mcp_config.MCP_TAVILY_URL,
        mcp_arxiv_url=search_mcp_config.MCP_ARXIV_URL,
        apify_actors_list=["apidojo/tweet-scraper"],
        mcp_telegram_parser_url=search_mcp_config.MCP_TELEGRAM_PARSER_URL,
    )

    # Try to connect to each MCP server individually
    mcp_tools = []
    successful_connections = 0
    failed_connections = 0

    logger.info("Attempting to connect to MCP servers individually...")

    for server_name, server_config in MCP_SERVERS_CONFIG.items():
        try:
            logger.info(
                f"Connecting to {server_name} at {server_config.get('url', 'No URL')}..."
            )

            # Create a single-server client for this server
            single_server_config = {server_name: server_config}
            single_client = MultiServerMCPClient(single_server_config)

            # Try to get tools from this specific server with timeout
            server_tools = await asyncio.wait_for(
                single_client.get_tools(), timeout=30.0
            )

            if server_tools:
                mcp_tools.extend(server_tools)
                successful_connections += 1
                tool_names = [tool.name for tool in server_tools]
                logger.info(
                    f"SUCCESS: {server_name} connected successfully - tools: {tool_names}"
                )
            else:
                logger.warning(
                    f"WARNING: {server_name} connected but returned no tools"
                )
                successful_connections += 1  # Still count as successful connection

        except asyncio.TimeoutError:
            failed_connections += 1
            logger.error(f"ERROR: {server_name} connection timed out after 30 seconds")
            continue
        except Exception as e:
            failed_connections += 1
            error_message = str(e)
            # Check for ExceptionGroup and extract sub-exceptions for clearer logging
            if hasattr(e, "exceptions") and e.exceptions:
                # Extract details from the first sub-exception
                sub_exc = e.exceptions[0]
                error_message = f"{type(sub_exc).__name__}: {sub_exc}"

            logger.error(f"ERROR: Failed to connect to {server_name}: {error_message}")
            logger.debug(f"Full error for {server_name}:", exc_info=True)
            continue

    # Log summary
    logger.info(
        f"MCP Connection Summary: {successful_connections} successful, {failed_connections} failed"
    )

    if successful_connections == 0:
        logger.error("CRITICAL ERROR: No MCP servers could be initialized!")
        sys.exit(1)
    else:
        logger.info(
            f"SUCCESS: Proceeding with {len(mcp_tools)} tools from {successful_connections} working servers"
        )
        if mcp_tools:
            tool_names = [tool.name for tool in mcp_tools]
            logger.info(f"Available MCP tools: {tool_names}")

    # -----------------------------------------------------------#
    # -----------------------------------------------------------#
    # -----------------------------------------------------------#
    # -----------------------------------------------------------#
    # Agent personality load
    agent_personality = load_agent_personality(agent_config.agent_personality_path)
    agent_name = agent_personality["agent"]["name"]
    logger.info(f"Agent personality loaded: {agent_personality}")
    # -----------------------------------------------------------#

    # Load the topics
    if topic == "AI_Robotics":
        topics_file_path = "config/agent_data/AI_Robotics_topics.json"
        topics = load_json(topics_file_path)
        news_memory_file_path = (
            media_paths.NEWS_OUTPUT_DIR + "/news_memory_AI_Robotics.json"
        )
    elif topic == "Web3":
        topics_file_path = "config/agent_data/Web3_topics.json"
        topics = load_json(topics_file_path)
        news_memory_file_path = media_paths.NEWS_OUTPUT_DIR + "/news_memory_Web3.json"
    else:
        logger.error(f"Invalid topic: {topic}")
        return None
    topics = topics["topics"]
    topics_list = list(topics.keys())
    logger.info(f"Topics: {topics_list}")

    # load the news memory for the specific topic
    try:
        news_memory = load_news_memory(news_memory_file_path, limit=5, titles_only=True)
        logger.info(f"News memory loaded: {news_memory}")
    except Exception as e:
        logger.error(f"Error loading news memory: {e}")
        news_memory = []

    # Initialize the agent
    agent = NewsGenerator(
        LLM,
        LLM_THINKING,
        tools=mcp_tools,
        news_memory=news_memory,
        agent_personality=agent_personality,
        agent_name=agent_name,
        research_topics=topics_list,
        topics_file_path=topics_file_path,
    )
    logger.info("Agent instance created.")
    result = await agent.graph.ainvoke({"research_topic": topics_list})
    return result, news_memory_file_path


async def generate_news(topic: str):
    """
    Runs the complete news generation and audio synthesis process.

    Args:
        output_dir: The directory to save the generated audio file.

    Returns:
        A tuple containing the audio file path and the news article data,
        or None if the process fails.
    """

    result, news_memory_file_path = await main(topic)

    if result.get("news_article_content") == "No news article content available":
        print("News generation process failed. Not saving to memory.")
        raise ValueError("News generation failed: No news article content was created.")
    else:
        save_news_memory(result, news_memory_file_path)

        # generate audio
        print("Starting audio generation...")
        elevenlabs_config = ElevenLabsSettings()
        filename = generate_voice(
            text=result["news_article_content"],
            api_config=elevenlabs_config,
            file_path=media_paths.VOICE_OUTPUT_DIR,
            topic=topic,
        )

        # Ensure the filename is not None and construct the full path
        if filename:
            audio_path = os.path.join(media_paths.VOICE_OUTPUT_DIR, filename)
            print(f"Audio generation completed. File saved to: {audio_path}")
            return audio_path, result
        else:
            print("Audio generation failed.")
            raise IOError("Audio generation failed: The audio file was not created.")


if __name__ == "__main__":
    # Example of how to run the generator
    # The output path can be configured here
    topic = "AI_Robotics"
    asyncio.run(generate_news(topic))
