# Libraries for different LLMs
import json
from logging import LoggerAdapter
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple, Type
from functools import lru_cache
from app_logging.logger import logger
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langchain_together import ChatTogether
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.language_models import BaseChatModel
from config.config import LLMSettings, LLM_Type

@lru_cache(maxsize=8)
def initialize_llm(
    llm_type: Literal["main", "validation", "spare", "thinking"] = "main",
    raise_on_error: bool = True,
) -> BaseChatModel:
    """
    Initializes and returns a language model client based on the specified type.
    This function is cached to avoid reloading models on subsequent calls.
    """
    config = LLMSettings()
    logger.info(f"Setting up '{llm_type}' LLM...")

    model_name = None

    # 1. Define mappings to find the correct config attributes and provider details
    ATTRIBUTE_MAP: Dict[LLM_Type, Tuple[str, str]] = {
        "main": ("MODEL_PROVIDER", "MODEL_NAME"),
        "spare": ("MODEL_PROVIDER_SPARE", "MODEL_NAME_SPARE"),
        "validation": ("MODEL_VALIDATION_PROVIDER", "MODEL_VALIDATION_NAME"),
        "thinking": ("MODEL_PROVIDER_THINKING", "MODEL_NAME_THINKING"),
    }

    PROVIDER_MAP: Dict[str, Dict[str, Any]] = {
        "together": {
            "class": ChatTogether,
            "api_key_name": "TOGETHER_API_KEY",
            "init_arg": "together_api_key",
        },
        "google": {
            "class": ChatGoogleGenerativeAI,
            "api_key_name": "GOOGLE_API_KEY",
            "init_arg": "google_api_key",
        },
        "mistral": {
            "class": ChatMistralAI,
            "api_key_name": "MISTRAL_API_KEY",
            "init_arg": "api_key",
        },
    }

    # 2. Get model provider and name from config using the attribute map
    provider_attr, name_attr = ATTRIBUTE_MAP[llm_type]
    model_provider = getattr(config, provider_attr, None)
    model_name = getattr(config, name_attr, None)

    if not all([model_provider, model_name]):
        msg = f"Configuration for '{llm_type}' LLM ('{provider_attr}', '{name_attr}') is incomplete."
        logger.error(msg)@lru_cache(maxsize=8)
def initialize_llm(
    llm_type: Literal["main", "validation", "spare", "thinking"] = "main",
    raise_on_error: bool = True,
) -> BaseChatModel:
    """
    Initializes and returns a language model client based on the specified type.
    This function is cached to avoid reloading models on subsequent calls.
    """
    config = LLMSettings()
    logger.info(f"Setting up '{llm_type}' LLM...")

    model_name = None

    # 1. Define mappings to find the correct config attributes and provider details
    ATTRIBUTE_MAP: Dict[LLM_Type, Tuple[str, str]] = {
        "main": ("MODEL_PROVIDER", "MODEL_NAME"),
        "spare": ("MODEL_PROVIDER_SPARE", "MODEL_NAME_SPARE"),
        "validation": ("MODEL_VALIDATION_PROVIDER", "MODEL_VALIDATION_NAME"),
        "thinking": ("MODEL_PROVIDER_THINKING", "MODEL_NAME_THINKING"),
    }

    PROVIDER_MAP: Dict[str, Dict[str, Any]] = {
        "together": {
            "class": ChatTogether,
            "api_key_name": "TOGETHER_API_KEY",
            "init_arg": "together_api_key",
        },
        "google": {
            "class": ChatGoogleGenerativeAI,
            "api_key_name": "GOOGLE_API_KEY",
            "init_arg": "google_api_key",
        },
        "mistral": {
            "class": ChatMistralAI,
            "api_key_name": "MISTRAL_API_KEY",
            "init_arg": "api_key",
        },
    }

    # 2. Get model provider and name from config using the attribute map
    provider_attr, name_attr = ATTRIBUTE_MAP[llm_type]
    model_provider = getattr(config, provider_attr, None)
    model_name = getattr(config, name_attr, None)

    if not all([model_provider, model_name]):
        msg = f"Configuration for '{llm_type}' LLM ('{provider_attr}', '{name_attr}') is incomplete."
        logger.error(msg)
        if raise_on_error:
            raise ValueError(msg)
        return None

    # 3. Get provider-specific details from the provider map
    provider_details = PROVIDER_MAP.get(model_provider.lower())
    if not provider_details:
        msg = f"Unsupported model provider for '{llm_type}': {model_provider}"
        logger.error(msg)
        if raise_on_error:
            raise ValueError(msg)
        return None

    # 4. Check for the required API key
    api_key_name = provider_details["api_key_name"]
    api_key_value = getattr(config, api_key_name, None)
    if not api_key_value:
        msg = f"'{api_key_name}' is required for provider '{model_provider}' but is not set."
        logger.error(msg)
        if raise_on_error:
            raise ValueError(msg)
        return None

    # 5. Initialize and return the model
    try:
        ModelClass: Type[BaseChatModel] = provider_details["class"]
        init_kwargs = {
            provider_details["init_arg"]: api_key_value,
            "model": model_name,
        }
        llm_instance = ModelClass(**init_kwargs)
        logger.info(
            f"Successfully initialized '{llm_type}' LLM with provider '{model_provider}'."
        )
        return llm_instance
    except Exception as e:
        msg = f"Failed to initialize '{llm_type}' LLM from provider '{model_provider}': {e}"
        logger.error(msg, exc_info=True)
        if raise_on_error:
            raise
        return None


def clean_response(response_text: str) -> str:
    """Clean the response text by removing markdown code block markers if present."""
    try:
        # Clean response text by removing markdown code block markers if present
        cleaned_response = response_text.strip()
        if cleaned_response.startswith("```json"):
            # Remove ```json from start and ``` from end
            cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]  # Remove ```
        elif cleaned_response.startswith("```"):
            # Remove ``` from start and end (generic code block)
            cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]

        cleaned_response = cleaned_response.strip()

        return cleaned_response
    except Exception as e:
        logger.error(f"Error cleaning response: {e}")

        return None

    # 3. Get provider-specific details from the provider map
    provider_details = PROVIDER_MAP.get(model_provider.lower())
    if not provider_details:
        msg = f"Unsupported model provider for '{llm_type}': {model_provider}"
        logger.error(msg)
        if raise_on_error:
            raise ValueError(msg)
        return None

    # 4. Check for the required API key
    api_key_name = provider_details["api_key_name"]
    api_key_value = getattr(config, api_key_name, None)
    if not api_key_value:
        msg = f"'{api_key_name}' is required for provider '{model_provider}' but is not set."
        logger.error(msg)
        if raise_on_error:
            raise ValueError(msg)
        return None

    # 5. Initialize and return the model
    try:
        ModelClass: Type[BaseChatModel] = provider_details["class"]
        init_kwargs = {
            provider_details["init_arg"]: api_key_value,
            "model": model_name,
        }
        llm_instance = ModelClass(**init_kwargs)
        logger.info(
            f"Successfully initialized '{llm_type}' LLM with provider '{model_provider}'."
        )
        return llm_instance
    except Exception as e:
        msg = f"Failed to initialize '{llm_type}' LLM from provider '{model_provider}': {e}"
        logger.error(msg, exc_info=True)
        if raise_on_error:
            raise
        return None


def clean_response(response_text: str) -> str:
    """Clean the response text by removing markdown code block markers if present."""
    try:
        # Clean response text by removing markdown code block markers if present
        cleaned_response = response_text.strip()
        if cleaned_response.startswith("```json"):
            # Remove ```json from start and ``` from end
            cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]  # Remove ```
        elif cleaned_response.startswith("```"):
            # Remove ``` from start and end (generic code block)
            cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]

        cleaned_response = cleaned_response.strip()

        return cleaned_response
    except Exception as e:
        logger.error(f"Error cleaning response: {e}")



def load_agent_personality(file_path: str):
    with open(file_path) as f:
        data = json.load(f)
    return data


def load_json(file_path, create_file=False):
    """Loads JSON file."""
    try:
        logger.info(f"Attempting to load file from: {file_path}")
        if not os.path.exists(file_path):
            logger.warning(
                f"File does not exist at path. Creating new file: {file_path}"
            )
            if create_file:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({}, f)
                return {}
            return {}

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            if not content:
                logger.warning(
                    f"File is empty: {file_path}. Returning empty dictionary."
                )
                return {}
            data = json.loads(content)
            logger.info(f"Successfully loaded JSON data from {file_path}")
            return data

    except json.JSONDecodeError as je:
        logger.error(
            f"JSON parsing error in {file_path}: {je}. Returning empty dictionary."
        )
        return {}

    except Exception as e:
        logger.error(f"Error loading file {file_path}: {e}")
        return {}
