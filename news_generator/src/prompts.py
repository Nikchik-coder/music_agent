from datetime import datetime

# Get current date in a readable format


def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


query_writer_instructions = """
<GOAL>
Your goal is to generate a targeted web search query and research topic for the generation of a news article.
</GOAL>

<CONTEXT>
Current date: {current_date}
Current topic: {current_topic}

Please ensure your queries account for the most current information available as of this date.
You need to generate a creative and innovative research topic and query based on the current topic, incorporating current data to ensure up-to-date results.
</CONTEXT>

<STRUCTURE>
Format your response as a JSON object with ALL three of these exact keys:
- "query": The actual search query string
- "research_topic": A clear, concise research topic that describes what you're investigating
- "rationale": A brief explanation of why this query and topic are relevant

Ensure that any double quotes within the JSON values are properly escaped (e.g., \"text with quotes\").
</STRUCTURE>

<EXAMPLE>
{{
    "query": "machine learning transformer architecture explained",
    "research_topic": "Understanding Transformer Models in AI",
    "rationale": "Understanding the fundamental structure of transformer models for current AI developments"
}}
</EXAMPLE>

Provide your response in JSON format:"""

summarise_web_research_results_instructions = """
<GOAL>
Generate a structured final research report based on the provided web research {web_research_results} and the research topic {current_topic}.
</GOAL>

<STRUCTURE>
Output ONLY a valid JSON object with these exact keys:
- "title": A concise, engaging title for the report (string).
- "executive_summary": A brief overview of the key findings (string, 2-3 paragraphs, no repetitions).

Do NOT include a sources section; it will be added separately.
Do NOT output any text before or after the JSON object.
Ensure that any double quotes within the JSON values are properly escaped (e.g., \"text with quotes\").
</STRUCTURE>

<REQUIREMENTS>
- Ensure the content is professional, clear, and free of repetitions or errors.
- Base it strictly on the provided web research results, synthesizing information coherently.
- Avoid hallucinations; stick to the facts from the summary.
</REQUIREMENTS>

<EXAMPLE>
{{
  "title": "Sample Report",
  "executive_summary": "Paragraph 1... Paragraph 2..."
}}
</EXAMPLE>

<TASK>
Using the existing summary, output ONLY the JSON report following the structure above. No other text.
</TASK>
"""

news_article_instructions = """
<GOAL>
You are a news anchor for a TV show, and your goal is to create an engaging and informative news article for your YouTube stream.
</GOAL>

<CONTEXT>
- Current date: {current_date}
- Current time: {current_time}
- Show name: {show_name}
- Agent name: {agent_name}
- Your personality: {agent_personality}
- Previous article titles: {news_memory}
- Final report: {final_report}
- Topics to cover: {topics}
- Article length: {current_article_len}
- Recommendations for article creation: {recommendations} (this might be an empty string). If it is not empty follow the advice from the recommendations.
- Current article version: {current_article_version} This might be an empty string. If not this is your previous article version. You need to enhance its quality to meet the recommendations provided. Do not create new one of this string is not empty. Improve the article to meet the recommendations provided.
- if recommendations are not empty you need to focus on improving the article to meet the recommendations provided.
</CONTEXT>

<REQUIREMENTS>
- Generate a news article based on the final report and your personality.
- The article should be creative, innovative, and written in the style of a TV news episode.
- Greet the users and make the episode engaging and informative.
- Ensure a smooth and natural transition between the different topics from the final report.
- The final report should cover each topic mentioned.
- The article must be less than 3000 words (Article length: {current_article_len} < 3000).
- The article should not contain any information about the scene. This should be the script for the agent to speak.
- The text should start with greetings as usual tv or radio show.
</REQUIREMENTS>

<STRUCTURE>
Please provide your response in a JSON format with the following keys:
{{
    "title": "A concise, engaging title for the report",
    "content": "The content of the article"
}}

Ensure that any double quotes within the JSON values are properly escaped (e.g., \"text with quotes\").
</STRUCTURE>
"""

validate_news_article_instructions = """
<GOAL>
You are a news anchor for a TV show, and your goal is to validate a news article.
</GOAL>

<CONTEXT>
- Your personality: {agent_personality}
- Agent name: {agent_name}
- News article to validate: {news_article}
- Topics to cover: {topics}
- Final report: {final_report}
- Previous article titles: {news_memory}
</CONTEXT>

<REQUIREMENTS>
- Ensure the news article is based on the final report.
- Verify that the article covers all topics from the final report and the provided topics list.
- Check that the article is written in the style of the agent's personality.
- Make sure the article is different from the previous articles in news_memory
</REQUIREMENTS>

<STRUCTURE>
Please provide your response in a JSON format with the following keys:
{{
    "validated": true,
    "recommendations": "Recommendations of how to improve the article if validated is false, otherwise an empty string"
}}

Ensure that any double quotes within the JSON values are properly escaped (e.g., \"text with quotes\").
</STRUCTURE>
"""
