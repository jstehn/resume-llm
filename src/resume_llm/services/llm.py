"""LLM service for handling different language models."""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Union

from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from ..config.llm_prompts import LLMPromptConfig, LLMRole
from ..config.settings import settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def get_model(self, **kwargs) -> BaseLanguageModel:
        """Get the language model instance."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""


class OpenAIProvider(LLMProvider):
    """OpenAI provider for GPT models."""

    def get_model(self, model: str = "gpt-4", **kwargs) -> ChatOpenAI:
        """Get OpenAI model."""
        if not self.is_available():
            raise RuntimeError("OpenAI API key not available")

        # Set environment variable for OpenAI
        if settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key

        return ChatOpenAI(
            model=model, temperature=kwargs.get("temperature", 0.7), **kwargs
        )

    def is_available(self) -> bool:
        """Check if OpenAI API key is available."""
        return settings.openai_api_key is not None


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""

    def get_model(
        self, model: str = "gemma-3n-e4b-it", **kwargs
    ) -> ChatGoogleGenerativeAI:
        """Get Gemini model."""
        if not self.is_available():
            raise RuntimeError(
                "Gemini API key not available or langchain-google-genai not installed"
            )

        # Set environment variable for Google API
        if settings.google_api_key:
            os.environ["GOOGLE_API_KEY"] = settings.google_api_key

        return ChatGoogleGenerativeAI(
            model=model,
            temperature=kwargs.get("temperature", 0.7),
            convert_system_message_to_human=True,  # Gemini doesn't support system messages
            **kwargs,
        )

    def is_available(self) -> bool:
        """Check if Gemini API key is available and package is installed."""
        return (
            hasattr(settings, "google_api_key") and settings.google_api_key is not None
        )


class LLMService:
    """Service for managing LLM interactions."""

    def __init__(self):
        self.providers = {
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider(),
        }
        self._default_provider = None

    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return [
            name for name, provider in self.providers.items() if provider.is_available()
        ]

    def get_default_provider(self) -> str:
        """Get the default provider name."""
        available = self.get_available_providers()
        if not available:
            raise RuntimeError("No LLM providers are available")

        # Prefer OpenAI if available, otherwise use first available
        if "openai" in available:
            return "openai"
        else:
            return available[0]

    def get_model(
        self, provider: Optional[str] = None, role: Optional[LLMRole] = None, **kwargs
    ) -> BaseLanguageModel:
        """Get a language model instance with optional role-based configuration."""
        provider_name = provider or self.get_default_provider()

        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")

        provider_instance = self.providers[provider_name]
        if not provider_instance.is_available():
            raise RuntimeError(f"Provider {provider_name} is not available")

        # Merge role-based config with kwargs
        if role:
            role_config = LLMPromptConfig.get_model_config(role, provider_name)
            # kwargs take precedence over role config
            merged_kwargs = {**role_config, **kwargs}
        else:
            merged_kwargs = kwargs

        return provider_instance.get_model(**merged_kwargs)

    async def generate_response(
        self,
        messages: Sequence[Union[str, BaseMessage]],
        provider: Optional[str] = None,
        role: Optional[LLMRole] = None,
        **kwargs,
    ) -> str:
        """Generate a response from the LLM with optional role-based system prompt."""
        model = self.get_model(provider=provider, role=role, **kwargs)

        # Convert string messages to BaseMessage instances
        formatted_messages = []

        # Add system message if role is specified
        if role:
            system_prompt = LLMPromptConfig.get_system_prompt(role)
            formatted_messages.append(SystemMessage(content=system_prompt))

        for msg in messages:
            if isinstance(msg, str):
                formatted_messages.append(HumanMessage(content=msg))
            else:
                formatted_messages.append(msg)

        response = await model.ainvoke(formatted_messages)
        return response.content

    def create_role_based_llm(
        self, role: LLMRole, provider: Optional[str] = None, **kwargs
    ) -> BaseLanguageModel:
        """Create an LLM instance configured for a specific role."""
        return self.get_model(provider=provider, role=role, **kwargs)

    async def generate_role_based_response(
        self, role: LLMRole, user_message: str, provider: Optional[str] = None, **kwargs
    ) -> str:
        """Generate a response using a specific role configuration."""
        return await self.generate_response(
            messages=[user_message], provider=provider, role=role, **kwargs
        )

    def get_role_info(self) -> Dict[str, Any]:
        """Get information about available roles and their configurations."""
        info = {}
        for role in LLMRole:
            template = LLMPromptConfig.get_prompt_template(role)
            info[role.value] = {
                "temperature": template.temperature,
                "max_tokens": template.max_tokens,
                "model_preferences": template.model_preferences,
                "system_prompt_preview": (
                    template.system_prompt[:200] + "..."
                    if len(template.system_prompt) > 200
                    else template.system_prompt
                ),
            }
        return info

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about available providers."""
        info = {}
        for name, provider in self.providers.items():
            info[name] = {
                "available": provider.is_available(),
                "is_default": (
                    name == self.get_default_provider()
                    if self.get_available_providers()
                    else False
                ),
            }
        return info


# Global LLM service instance
llm_service = LLMService()
