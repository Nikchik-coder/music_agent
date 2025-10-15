from langgraph.graph import END, START, StateGraph
from music_generator.suno_pipeline.state import MusicGenerationState
import logging
from music_generator.suno_pipeline.music_generation_prompt import (
    MUSIC_GENERATION_PROMPT,
    MUSIC_VALIDATION_PROMPT,
)
from utils.utils import clean_response
from langchain_core.output_parsers import JsonOutputParser
from config.config import SunoSettings, SoundcloudSettings
from music_generator.suno_pipeline.sunoapi import generate_song_suno
from music_generator.soundcloud.soundcloud_upload import SoundCloudUploader
import json
from datetime import datetime
import os
import shutil


logger = logging.getLogger(__name__)


class MusicGeneration:
    def __init__(
        self,
        LLM,
        LLM_THINKING,
        music_memory: dict,
        music_memory_file_path: str,
        music_folder: str,
        music_style: str,
        agent_personality: dict,
        agent_name: str,
        call_back_url: str,
    ):
        self.llm = LLM
        self.llm_thinking = LLM_THINKING
        self.music_memory = music_memory
        self.music_memory_file_path = music_memory_file_path
        self.music_folder = music_folder
        self.music_style = music_style
        self.agent_personality = agent_personality
        self.agent_name = agent_name
        self.call_back_url = call_back_url
        self.music_memory_counter = 0
        self.suno_settings = SunoSettings()
        self.soundcloud_settings = SoundcloudSettings()
        self.graph = self._build_graph()

    def _build_graph(self):
        # Add nodes and edges
        builder = StateGraph(
            MusicGenerationState,
            input=MusicGenerationState,
            output=MusicGenerationState,
        )
        builder.add_node("generate_song_prompt", self.generate_song_prompt)
        builder.add_node("validate_song_prompt", self.validate_song_prompt)
        builder.add_node("generate_song", self.generate_song)

        builder.add_edge(START, "generate_song_prompt")
        builder.add_edge("generate_song_prompt", "validate_song_prompt")
        builder.add_conditional_edges(
            "validate_song_prompt",
            self.route_validate_song_prompt,
            {
                "generate_song": "generate_song",
                "generate_song_prompt": "generate_song_prompt",
                END: END,
            },
        )
        builder.add_edge("generate_song", END)

        graph = builder.compile()
        logger.info("Graph compiled successfully")

        # Script to save the graph as an image file
        # Save the graph visualization as an image file
        # logger.info("Saving graph as image")
        # try:
        #     # Get the directory of the current file
        #     output_dir = os.path.dirname(os.path.abspath(__file__))
        #     output_path = os.path.join(output_dir, "music_graph.png")

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

    async def generate_song_prompt(self, state: MusicGenerationState):
        """
        LangGraph node that generates a song prompt based on the music memory.
        """

        formated_prompt = MUSIC_GENERATION_PROMPT.format(
            music_memory=self.music_memory,
            music_style=self.music_style,
            agent_personality=self.agent_personality,
            agent_name=self.agent_name,
        )
        result = await self.llm_thinking.ainvoke(formated_prompt)
        result = JsonOutputParser().parse(clean_response(result.content))
        state.song_name = result["song_name"]
        state.song_prompt = result["song_prompt"]
        state.negativeTags = result["negativeTags"]
        state.vocalGender = result["vocalGender"]
        state.styleWeight = result["styleWeight"]
        state.weirdnessConstraint = result["weirdnessConstraint"]
        state.audioWeight = result["audioWeight"]
        logger.info(f"Song prompt {state.song_prompt}")
        logger.info(f"Full result {result}")
        return state

    async def validate_song_prompt(self, state: MusicGenerationState):
        """
        LangGraph node that validates a song prompt.
        """

        song_prompt_length = len(state.song_prompt)
        logger.info(f"Song prompt length {song_prompt_length}")
        formated_prompt = MUSIC_VALIDATION_PROMPT.format(
            song_name=state.song_name,
            song_prompt=state.song_prompt,
            song_prompt_length=song_prompt_length,
            music_memory=self.music_memory,
            music_style=self.music_style,
            agent_personality=self.agent_personality,
            agent_name=self.agent_name,
            negativeTags=state.negativeTags,
            vocalGender=state.vocalGender,
            styleWeight=state.styleWeight,
            weirdnessConstraint=state.weirdnessConstraint,
            audioWeight=state.audioWeight,
        )
        result = await self.llm.ainvoke(formated_prompt)
        result = JsonOutputParser().parse(clean_response(result.content))
        state.song_prompt_validated = result.get("song_prompt_validated", False)
        state.recommendations = result.get("recommendations")
        state.negativeTags = result.get("negativeTags")
        state.vocalGender = result.get("vocalGender")
        logger.info(f"Song prompt validated {state.song_prompt_validated}")
        logger.info(f"Recommendations {state.recommendations}")
        return state

    async def route_validate_song_prompt(self, state: MusicGenerationState):
        """
        LangGraph node that routes the validate song prompt.
        """
        if state.song_prompt_validated:
            return "generate_song"
        elif not state.song_prompt_validated and state.generate_song_prompt_counter < 3:
            state.generate_song_prompt_counter += 1
            return "generate_song_prompt"
        else:
            return END

    async def generate_song(self, state: MusicGenerationState):
        """
        LangGraph node that generates a song based on the song prompt.
        """
        try:
            song_prompt = state.song_prompt
            if state.recommendations:
                song_prompt += f"\n{state.recommendations}"

            if len(song_prompt) > 400:
                logger.warning("Prompt is too long, truncating to 400 characters.")
                song_prompt = song_prompt[:400]

            filenames, titles = generate_song_suno(
                suno_settings=self.suno_settings,
                song_prompt=song_prompt,
                negativeTags=state.negativeTags,
                vocalGender=state.vocalGender,
                styleWeight=state.styleWeight,
                weirdnessConstraint=state.weirdnessConstraint,
                audioWeight=state.audioWeight,
            )
        except Exception as e:
            logger.error(f"Error generating song: {e}")
            return END
        if filenames:
            logger.info(f"Filenames {filenames}")

            history_file_path = self.music_memory_file_path
            music_generation_history = {"music_generation_history": []}
            if os.path.exists(history_file_path) and os.path.getsize(history_file_path) > 0:
                with open(history_file_path, "r") as f:
                    try:
                        loaded_data = json.load(f)
                        if isinstance(loaded_data, dict) and "music_generation_history" in loaded_data:
                            music_generation_history = loaded_data
                    except json.JSONDecodeError:
                        logger.warning(f"{history_file_path} is corrupted. Starting a new history.")

            if music_generation_history["music_generation_history"]:
                new_id = (
                    music_generation_history["music_generation_history"][-1].get("id", 0) + 1
                )
            else:
                new_id = 1

            music_generation_history["music_generation_history"].append(
                {
                    "id": new_id,
                    "song_name": state.song_name,
                    "song_prompt": state.song_prompt,
                    "negativeTags": state.negativeTags,
                    "vocalGender": state.vocalGender,
                    "styleWeight": state.styleWeight,
                    "weirdnessConstraint": state.weirdnessConstraint,
                    "audioWeight": state.audioWeight,
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                }
            )
            with open(
                self.music_memory_file_path, "w"
            ) as f:
                json.dump(music_generation_history, f, indent=4)
            state.song_filepath = filenames[0]
            state.song_title = titles[0]
            logger.info(f"Song generated and saved to {state.song_filepath}")

            # Move the song to the desired folder
            try:
                destination_folder = self.music_folder
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)
                
                for filename in filenames:
                    shutil.move(filename, os.path.join(destination_folder, os.path.basename(filename)))
                logger.info(f"Successfully moved songs to {destination_folder}")
            except Exception as e:
                logger.error(f"Error moving song to folder: {e}")
        else:
            logger.error("Failed to generate song")
        return state

    def should_continue(self, state):
        if state.song_filepath:
            return "end"
        else:
            return "generate_song_prompt"

