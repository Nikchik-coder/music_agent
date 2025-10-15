import operator
from dataclasses import dataclass, field

from typing_extensions import Annotated


@dataclass(kw_only=True)
class MusicGenerationState:
    song_prompt: str = field(default=None)  # Song prompt
    song_name: str = field(default=None)  # Song name
    song_prompt_validated: bool = field(
        default=None
    )  # Music generation validation results
    recommendations: str = field(default=None)  # Music generation validation results
    negativeTags: str = field(default=None)  # Music generation validation results
    vocalGender: str = field(default=None)  # Music generation validation results
    styleWeight: float = field(default=None)  # Music generation validation results
    weirdnessConstraint: float = field(
        default=None
    )  # Music generation validation results
    audioWeight: float = field(default=None)  # Music generation validation results
    generate_song_prompt_counter: int = field(
        default=0
    )  # Music generation validation counter
    song_generated: bool = field(
        default=None
    )  # Music generation variable, if False than songs wasnt generated
    song_filepath: str = field(default=None)  # Filepath of the generated song
    song_title: str = field(default=None)  # Title of the generated song
    song_sent_soundcloud: bool = field(
        default=None
    )  # This variable controls whether the song was sent to soundcloud successfully
    music_generation_results: Annotated[list, operator.add] = field(
        default_factory=list
    )  # Music generation results
