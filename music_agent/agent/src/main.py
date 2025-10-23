import asyncio
import sys

from config.config import (
    LLMSettings,
    SunoSettings,
    AgentConfig,
)
from music_agent.agent.graph.music_graph import MusicGeneration
from utils.utils import (
    load_agent_personality,
    load_json,
)
from music_agent.agent.graph.state import MusicGenerationState
from app_logging.logger import logger

from music_agent.utils.llm_utils import initialize_llms, initialize_llm_from_config



# Load the configuration
logger.info("Loading configuration...")
try:
    llm_config = LLMSettings()
    agent_config = AgentConfig()
    suno_settings = SunoSettings()
    agent_personality = agent_config.agent_personality_path
    logger.info("Configuration loaded.")
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    sys.exit(1)
# Initialize LLMs with the provided configuration
logger.info("Initializing LLMs...")
LLM, LLM_THINKING, LLM_VALIDATION = initialize_llms(llm_config)
if not all([LLM, LLM_THINKING, LLM_VALIDATION]):
    logger.critical(
        f"Failed to initialize LLMs. Aborting simulation."
    )
    sys.exit(1)
logger.info("LLMs initialized successfully.")

async def main():
    # Loading files
    try:
        agent_personality = load_agent_personality(agent_config.agent_personality_path)
        music_memory = load_json(suno_settings.MUSIC_MEMORY_PATH)
        album_style = load_json(suno_settings.ALBUM_STYLE_PATH)
        if music_memory is None:
            music_memory = {}
        music_memory = music_memory.get("music_generation_history", [])[-5:]
        music_memory_file_path = suno_settings.MUSIC_MEMORY_PATH
        music_folder = suno_settings.MUSIC_OUTPUT_DIR or "songs"
        agent_name = agent_personality["agent"]["name"]
        music_style = agent_personality["music_style"]
        call_back_url = suno_settings.SUNO_CALLBACK_URL
        logger.info("Agent personality was loaded")
        logger.info(f"Agent personality: {agent_personality}")
        logger.info(f"Music memory: {music_memory}")
        logger.info(f"Agent name: {agent_name}")
        logger.info(f"Music style: {music_style}")
    except Exception as e:
        logger.error(f"Error loading files: {e}")
        sys.exit(1)
    # -----------------------------------------------------------#

    # Initialize the agent
    agent = MusicGeneration(
        LLM,
        LLM_THINKING,
        music_memory=music_memory,
        music_memory_file_path=music_memory_file_path,
        music_folder=music_folder,
        music_style=agent_personality["music_style"],
        agent_personality=agent_personality,
        album_style=album_style,
        agent_name=agent_name,
        call_back_url=call_back_url,
    )
    logger.info("Agent instance created.")
    result = await agent.graph.ainvoke(MusicGenerationState())
    return result


async def generate_music(number_of_songs: int):
    """
    Runs the complete music generation and audio synthesis process.
    """
    logger.info(f"Starting music generation for {number_of_songs} songs...")
    for _ in range(number_of_songs):
        logger.info(f"Generating song {_ + 1} of {number_of_songs}")
        await main()
    logger.info(f"Music generation completed for {number_of_songs} songs")


if __name__ == "__main__":
    number_of_songs = 1
    logger.info(f"Starting music generation for {number_of_songs} songs...")
    asyncio.run(generate_music(number_of_songs))
