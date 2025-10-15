import asyncio
import logging
import sys

from config.config import (
    LLMSettings,
    SunoSettings,
    SoundcloudSettings,
    AgentConfig,
    MediaPaths,
)
from music_generator.suno_pipeline.music_graph import MusicGeneration
from news_generator.src.utils import (
    load_agent_personality,
    load_json,
    initialize_llm,
)
from music_generator.suno_pipeline.state import MusicGenerationState


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
    agent_config = AgentConfig()
    media_paths = MediaPaths()
    suno_settings = SunoSettings()
    soundcloud_settings = SoundcloudSettings()
    agent_personality = agent_config.agent_personality_path
    logger.info("Configuration loaded.")
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    sys.exit(1)

# Initialize the Main LLM, with fallback to Spare on failure
#Initializing the Main LLM before the cycle so we do not reainitialize it 
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



async def main():
    # Loading files
    try:
        agent_personality = load_agent_personality(agent_config.agent_personality_path)
        music_memory = load_json(suno_settings.MUSIC_MEMORY_PATH)
        if music_memory is None:
            music_memory = {}
        music_memory = music_memory.get("music_generation_history", [])[-5:]
        music_memory_file_path = suno_settings.MUSIC_MEMORY_PATH
        music_folder = suno_settings.MUSIC_OUTPUT_DIR
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
    number_of_songs = 5
    logger.info(f"Starting music generation for {number_of_songs} songs...")
    asyncio.run(generate_music(number_of_songs))
