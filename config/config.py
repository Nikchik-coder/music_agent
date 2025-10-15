from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Dict, Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dataclasses import field
from dotenv import find_dotenv

logger = logging.getLogger(__name__)


class YouTubeSettings(BaseSettings):
    CLIENT_SECRETS_FILE: str = Field(
        default=str(Path(__file__).with_name("client_secrets.json"))
    )
    SCOPES: list[str] = Field(
        default=["https://www.googleapis.com/auth/youtube.force-ssl"]
    )
    API_SERVICE_NAME: str = Field(default="youtube")
    API_VERSION: str = Field(default="v3")
    YOUTUBE_ENABLED: bool = Field(default=True, env="YOUTUBE_ENABLED")

    STREAM_ID: str | None = Field(default=None, env="STREAM_ID")
    CLIENT_SECRET_FILE_PATH: str | None = Field(
        default=None, env="CLIENT_SECRET_FILE_PATH"
    )
    TOKEN_FILE_PATH: str | None = Field(default=None, env="TOKEN_FILE_PATH")
    MEMORY_FILE_PATH: str | None = Field(default=None, env="MEMORY_FILE_PATH")
    OAUTH_CLIENT_ID: str | None = Field(default=None, env="OAUTH_CLIENT_ID")
    OAUTH_CLIENT_SECRET: str | None = Field(default=None, env="OAUTH_CLIENT_SECRET")
    OAUTH_REFRESH_TOKEN: str | None = Field(default=None, env="OAUTH_REFRESH_TOKEN")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


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


class SearchMCP_Config(BaseSettings):
    MCP_TAVILY_URL: Optional[str] = Field(default=None, env="MCP_TAVILY_URL")
    MCP_YOUTUBE_URL: Optional[str] = Field(default=None, env="MCP_YOUTUBE_URL")
    MCP_ARXIV_URL: Optional[str] = Field(default=None, env="MCP_ARXIV_URL")
    MCP_DEEP_RESEARCHER_URL: Optional[str] = Field(
        default=None, env="MCP_DEEP_RESEARCHER_URL"
    )
    APIFY_TOKEN: Optional[str] = Field(default=None, env="APIFY_TOKEN")
    MCP_TWITTER_URL: Optional[str] = Field(default=None, env="MCP_TWITTER_URL")
    MCP_APIFY_URL: Optional[str] = Field(default=None, env="MCP_APIFY_URL")
    MCP_IMAGE_GENERATION: Optional[str] = Field(
        default=None, env="MCP_IMAGE_GENERATION"
    )
    APIFY_TWEET_MAX_AGE_DAYS: int = Field(default=3, env="APIFY_TWEET_MAX_AGE_DAYS")
    MCP_TELEGRAM_PARSER_URL: Optional[str] = Field(
        default=None, env="MCP_TELEGRAM_PARSER_URL"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class AudioSettings(BaseSettings):
    BACKGROUND_MUSIC_VOLUME_NORMAL: float = Field(
        default=0.3, env="BACKGROUND_MUSIC_VOLUME_NORMAL"
    )
    BACKGROUND_MUSIC_VOLUME_DUCKED: float = Field(
        default=0.1, env="BACKGROUND_MUSIC_VOLUME_DUCKED"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class OBSSettings(BaseSettings):
    OBS_HOST: str = Field(default="", env="OBS_HOST")
    OBS_PORT: int = Field(default=0, env="OBS_PORT")
    OBS_PASSWORD: str = Field(default="", env="OBS_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class SoundcloudSettings(BaseSettings):
    SOUNDCLOUD_CLIENT_ID: str = Field(default="", env="SOUNDCLOUD_CLIENT_ID")
    SOUNDCLOUD_CLIENT_SECRET: str = Field(default="", env="SOUNDCLOUD_CLIENT_SECRET")
    SOUNDCLOUD_CLIENT_CODE: str = Field(default="", env="SOUNDCLOUD_CLIENT_CODE")
    SOUNDCLOUD_ACCESS_TOKEN: str = Field(default="", env="SOUNDCLOUD_ACCESS_TOKEN")
    SOUNDCLOUD_REFRESH_TOKEN: str = Field(default="", env="SOUNDCLOUD_REFRESH_TOKEN")
    SOUNDCLOUD_PLAYLIST_NAME: str = Field(default="", env="SOUNDCLOUD_PLAYLIST_NAME")
    SOUNDCLOUD_PLAYLIST_URL: list[str] = Field(
        default=["https://soundcloud.com/xylumi/sets/my-stream"],
        env="SOUNDCLOUD_PLAYLIST_URL",
    )
    # Use absolute path for new unified media structure
    OUTPUT_FOLDER: str = Field(
        default="/app/media/music/soundcloud_songs", env="SOUNDCLOUD_OUTPUT_DIR"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


soundcloud_settings = SoundcloudSettings()


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


class ElevenLabsSettings(BaseSettings):
    ELEVENLABS_API_KEY: Optional[str] = Field(default=None, env="ELEVENLABS_API_KEY")
    ELEVENLABS_VOICE_ID: Optional[str] = Field(default=None, env="ELEVENLABS_VOICE_ID")
    ELEVENLABS_MODEL_ID: Optional[str] = Field(default=None, env="ELEVENLABS_MODEL_ID")
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
    NEWS_OUTPUT_DIR: str = Field(default="/app/media/news", env="NEWS_OUTPUT_DIR")
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
    APIFY_TOKEN: str | None = Field(default=None, env="APIFY_TOKEN")
    CARTESIA_API_KEY: str | None = Field(default=None, env="CARTESIA_API_KEY")

    youtube: YouTubeSettings = YouTubeSettings()
    llm: LLMSettings = LLMSettings()
    audio: AudioSettings = AudioSettings()
    obs: OBSSettings = OBSSettings()
    soundcloud: SoundcloudSettings = SoundcloudSettings()
    elevenlabs: ElevenLabsSettings = ElevenLabsSettings()
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class MediaPaths(BaseSettings):
    VOICE_OUTPUT_DIR: str = Field(
        default="/app/media/voice/generated_audio", env="VOICE_OUTPUT_DIR"
    )
    NEWS_OUTPUT_DIR: str = Field(default="/app/media/news", env="NEWS_OUTPUT_DIR")
    STATE_OUTPUT_DIR: str = Field(default="/app/media/state", env="STATE_OUTPUT_DIR")
    MEMORY_OUTPUT_DIR: str = Field(default="/app/media/memory", env="MEMORY_OUTPUT_DIR")
    VIDEOS_OUTPUT_DIR: str = Field(default="/app/media/videos", env="VIDEOS_OUTPUT_DIR")
    MUSIC_OUTPUT_DIR: str = Field(
        default="/app/media/music/google_drive_songs", env="GOOGLE_DRIVE_MUSIC_DIR"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Resolve environment variable expansion for local development
        self._resolve_paths()

    def _resolve_paths(self):
        """Resolve environment variable expansion in paths for local development."""
        import os

        # Get the media host directory from environment
        media_host_dir = os.getenv("MEDIA_HOST_DIR")
        media_container_dir = os.getenv("MEDIA_CONTAINER_DIR", "/app/media")

        if media_host_dir:
            # If we're running locally (not in container), use host paths
            if not os.path.exists("/app"):
                # Convert container paths to host paths
                if self.VOICE_OUTPUT_DIR.startswith(media_container_dir):
                    self.VOICE_OUTPUT_DIR = self.VOICE_OUTPUT_DIR.replace(
                        media_container_dir, media_host_dir
                    )
                if self.NEWS_OUTPUT_DIR.startswith(media_container_dir):
                    self.NEWS_OUTPUT_DIR = self.NEWS_OUTPUT_DIR.replace(
                        media_container_dir, media_host_dir
                    )
                if self.STATE_OUTPUT_DIR.startswith(media_container_dir):
                    self.STATE_OUTPUT_DIR = self.STATE_OUTPUT_DIR.replace(
                        media_container_dir, media_host_dir
                    )
                if self.MEMORY_OUTPUT_DIR.startswith(media_container_dir):
                    self.MEMORY_OUTPUT_DIR = self.MEMORY_OUTPUT_DIR.replace(
                        media_container_dir, media_host_dir
                    )
                if self.VIDEOS_OUTPUT_DIR.startswith(media_container_dir):
                    self.VIDEOS_OUTPUT_DIR = self.VIDEOS_OUTPUT_DIR.replace(
                        media_container_dir, media_host_dir
                    )
                if self.MUSIC_OUTPUT_DIR.startswith(media_container_dir):
                    self.MUSIC_OUTPUT_DIR = self.MUSIC_OUTPUT_DIR.replace(
                        media_container_dir, media_host_dir
                    )

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


class StreamConfig(BaseSettings):
    """A simple container for the stream ID."""

    STREAM_ID: str | None = None
    DEBUG: bool = False
    MEMORY_FILE_PATH: str = "state/memory.json"
    # model_config = DEFAULT_CONFIG


stream_config = StreamConfig()
logger.info(f"Stream config: {str(stream_config)}")

# Global settings instance
settings = Settings()


# --- Path conversion helpers ---


def to_system_path(container_path: str) -> str:
    """
    Convert a container path under MEDIA_CONTAINER_DIR into a host path under MEDIA_HOST_DIR.
    If mapping not configured, return original.
    """
    host_root = settings.MEDIA_HOST_DIR
    container_root = settings.MEDIA_CONTAINER_DIR
    if host_root and container_root:
        p = str(container_path)
        if p.startswith(container_root):
            return host_root + p[len(container_root) :]  # noqa
    return container_path


def to_container_path(system_or_rel_path: str) -> str:
    """
    Best-effort: if given an absolute host path under MEDIA_HOST_DIR, map to MEDIA_CONTAINER_DIR.
    Otherwise return unchanged.
    """
    host_root = settings.MEDIA_HOST_DIR
    container_root = settings.MEDIA_CONTAINER_DIR
    if host_root and container_root:
        p = str(system_or_rel_path)
        if p.startswith(host_root):
            return container_root + p[len(host_root):]
    return system_or_rel_path


# ---- Backward-compat constants (legacy imports) --------------------------- # TODO: this should be removed in the future
# Many modules used to import constants directly from radio.config.
# Keep these aliases so old code keeps working during the transition.

# General API Keys
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
TAVILY_API_KEY = settings.TAVILY_API_KEY
MISTRAL_API_KEY = settings.MISTRAL_API_KEY
TOGETHER_API_KEY = settings.TOGETHER_API_KEY
APIFY_TOKEN = settings.APIFY_TOKEN
CARTESIA_API_KEY = settings.CARTESIA_API_KEY

# YouTube
CLIENT_SECRETS_FILE = settings.youtube.CLIENT_SECRETS_FILE
SCOPES = settings.youtube.SCOPES
API_SERVICE_NAME = settings.youtube.API_SERVICE_NAME
API_VERSION = settings.youtube.API_VERSION
YOUTUBE_ENABLED = settings.youtube.YOUTUBE_ENABLED

STREAM_ID = settings.youtube.STREAM_ID
CLIENT_SECRET_FILE_PATH = settings.youtube.CLIENT_SECRET_FILE_PATH
TOKEN_FILE_PATH = settings.youtube.TOKEN_FILE_PATH
MEMORY_FILE_PATH = settings.youtube.MEMORY_FILE_PATH
OAUTH_CLIENT_ID = settings.youtube.OAUTH_CLIENT_ID
OAUTH_CLIENT_SECRET = settings.youtube.OAUTH_CLIENT_SECRET
OAUTH_REFRESH_TOKEN = settings.youtube.OAUTH_REFRESH_TOKEN

# LLM
MODEL_PROVIDER = settings.llm.MODEL_PROVIDER
MODEL_NAME = settings.llm.MODEL_NAME
MODEL_VALIDATION_PROVIDER = settings.llm.MODEL_VALIDATION_PROVIDER
MODEL_VALIDATION_NAME = settings.llm.MODEL_VALIDATION_NAME
MODEL_PROVIDER_SPARE = settings.llm.MODEL_PROVIDER_SPARE
MODEL_NAME_SPARE = settings.llm.MODEL_NAME_SPARE

# Audio
BACKGROUND_MUSIC_VOLUME_NORMAL = settings.audio.BACKGROUND_MUSIC_VOLUME_NORMAL
BACKGROUND_MUSIC_VOLUME_DUCKED = settings.audio.BACKGROUND_MUSIC_VOLUME_DUCKED

# OBS
OBS_HOST = settings.obs.OBS_HOST
OBS_PORT = settings.obs.OBS_PORT
OBS_PASSWORD = settings.obs.OBS_PASSWORD

# ElevenLabs
ELEVENLABS_API_KEY = settings.elevenlabs.ELEVENLABS_API_KEY
ELEVENLABS_VOICE_ID = settings.elevenlabs.ELEVENLABS_VOICE_ID
ELEVENLABS_MODEL_ID = settings.elevenlabs.ELEVENLABS_MODEL_ID
