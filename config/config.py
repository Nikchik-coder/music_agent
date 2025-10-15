from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app_logging.logger import logger


LLM_Type = Literal["main", "validation", "spare", "thinking"]


class LLMSettings(BaseSettings):
    MODEL_PROVIDER: str = Field(default="together", env="MODEL_PROVIDER")
    MODEL_NAME: str = Field(default="deepseek-ai/DeepSeek-V3", env="MODEL_NAME")
    MODEL_VALIDATION_PROVIDER: str = Field(
        default="together", env="MODEL_VALIDATION_PROVIDER"
    )
    MODEL_VALIDATION_NAME: str = Field(
        default="meta-llama/Llama-3.3-70B-Instruct-Turbo", env="MODEL_VALIDATION_NAME"
    )
    MODEL_PROVIDER_SPARE: str = Field(default="together", env="MODEL_PROVIDER_SPARE")
    MODEL_NAME_SPARE: str = Field(
        default="deepseek-ai/DeepSeek-V3", env="MODEL_NAME_SPARE"
    )

    MODEL_PROVIDER_THINKING: str = Field(
        default="google", env="MODEL_PROVIDER_THINKING"
    )
    MODEL_NAME_THINKING: str = Field(
        default="gemini-2.5-pro", env="MODEL_NAME_THINKING"
    )
    GOOGLE_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    TOGETHER_API_KEY: Optional[str] = Field(default=None, env="TOGETHER_API_KEY")
    MISTRAL_API_KEY: Optional[str] = Field(default=None, env="MISTRAL_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )





class SunoSettings(BaseSettings):
    SUNO_API_KEY: Optional[str] = Field(default=None, env="SUNO_API_KEY")
    MUSIC_STYLE_PATH: Optional[str] = Field(default=None, env="MUSIC_STYLE_PATH")
    MUSIC_MEMORY_PATH: Optional[str] = Field(default=None, env="MUSIC_MEMORY_PATH")
    SUNO_CALLBACK_URL: Optional[str] = Field(default=None, env="SUNO_CALLBACK_URL")
    MUSIC_HISTORY_PATH: Optional[str] = Field(default=None, env="MUSIC_HISTORY_PATH")
    MUSIC_OUTPUT_DIR: Optional[str] = Field(default=None, env="MUSIC_OUTPUT_DIR")
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )



class Settings(BaseSettings):
    AGENT_VOICE_SYSTEM_PATH: str | None = Field(default=None, env="AGENT_VOICE_PATH")

    # NEW: unified media structure
    MEDIA_HOST_DIR: Optional[str] = Field(default=None, env="MEDIA_HOST_DIR")
    MEDIA_CONTAINER_DIR: str = Field(default="/app/media", env="MEDIA_CONTAINER_DIR")

    # NEW: all media output folders (container-side)
    VOICE_OUTPUT_DIR: str = Field(
        default="/app/media/voice/generated_audio", env="VOICE_OUTPUT_DIR"
    )
    STATE_OUTPUT_DIR: str = Field(default="/app/media/state", env="STATE_OUTPUT_DIR")
    MEMORY_OUTPUT_DIR: str = Field(default="/app/media/memory", env="MEMORY_OUTPUT_DIR")
    VIDEOS_OUTPUT_DIR: str = Field(default="/app/media/videos", env="VIDEOS_OUTPUT_DIR")
    MUSIC_OUTPUT_DIR: str = Field(
        default="/app/media/music/google_drive_songs", env="GOOGLE_DRIVE_MUSIC_DIR"
    )

    # Legacy memory file path (now under media)
    MEMORY_FILE: Path = Field(
        default=Path("/app/media/memory/memory.json"), env="MEMORY_FILE"
    )

    # General API Keys
    GOOGLE_API_KEY: str | None = Field(default=None, env="GOOGLE_API_KEY")
    TAVILY_API_KEY: str | None = Field(default=None, env="TAVILY_API_KEY")
    MISTRAL_API_KEY: str | None = Field(default=None, env="MISTRAL_API_KEY")
    TOGETHER_API_KEY: str | None = Field(default=None, env="TOGETHER_API_KEY")

    llm: LLMSettings = LLMSettings()
    suno: SunoSettings = SunoSettings()
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

class AgentConfig(BaseSettings):
    agent_personality_path: Optional[str] = Field(
        default=None, env="AGENT_PERSONALITY_PATH"
    )
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

# Global settings instance
settings = Settings()



# General API Keys
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
TAVILY_API_KEY = settings.TAVILY_API_KEY
MISTRAL_API_KEY = settings.MISTRAL_API_KEY
TOGETHER_API_KEY = settings.TOGETHER_API_KEY



# LLM
MODEL_PROVIDER = settings.llm.MODEL_PROVIDER
MODEL_NAME = settings.llm.MODEL_NAME
MODEL_VALIDATION_PROVIDER = settings.llm.MODEL_VALIDATION_PROVIDER
MODEL_VALIDATION_NAME = settings.llm.MODEL_VALIDATION_NAME
MODEL_PROVIDER_SPARE = settings.llm.MODEL_PROVIDER_SPARE
MODEL_NAME_SPARE = settings.llm.MODEL_NAME_SPARE
SUNO_API_KEY = settings.suno.SUNO_API_KEY
MUSIC_STYLE_PATH = settings.suno.MUSIC_STYLE_PATH
MUSIC_MEMORY_PATH = settings.suno.MUSIC_MEMORY_PATH
SUNO_CALLBACK_URL = settings.suno.SUNO_CALLBACK_URL
MUSIC_HISTORY_PATH = settings.suno.MUSIC_HISTORY_PATH
MUSIC_OUTPUT_DIR = settings.suno.MUSIC_OUTPUT_DIR
