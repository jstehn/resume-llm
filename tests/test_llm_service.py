"""Unit tests for LLM service with Gemini support."""

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from resume_llm.config.settings import settings
from resume_llm.services.llm import GeminiProvider, LLMService, OpenAIProvider


class TestLLMProviders:
    """Test individual LLM providers."""

    def test_openai_provider_availability(self):
        """Test OpenAI provider availability check."""
        provider = OpenAIProvider()

        # Test with no API key
        with patch.object(settings, "openai_api_key", None):
            assert not provider.is_available()

        # Test with API key
        with patch.object(settings, "openai_api_key", "test-key"):
            assert provider.is_available()

    def test_gemini_provider_availability(self):
        """Test Gemini provider availability check."""
        provider = GeminiProvider()

        # Test with no API key
        with patch.object(settings, "google_api_key", None):
            assert not provider.is_available()

        # Test with API key
        with patch.object(settings, "google_api_key", "test-key"):
            assert provider.is_available()

    def test_gemini_model_creation(self):
        """Test Gemini model creation."""
        provider = GeminiProvider()

        with patch.object(settings, "google_api_key", "test-key"):
            with patch("resume_llm.services.llm.ChatGoogleGenerativeAI") as mock_model:
                mock_instance = Mock()
                mock_model.return_value = mock_instance

                model = provider.get_model(model="gemini-2.0-flash-lite")

                mock_model.assert_called_once_with(
                    model="gemini-2.0-flash-lite",
                    temperature=0.7,
                )
                assert model == mock_instance


class TestLLMService:
    """Test the main LLM service."""

    def test_service_initialization(self):
        """Test LLM service initialization."""
        service = LLMService()

        # Should always have OpenAI and Gemini
        assert "openai" in service.providers
        assert "gemini" in service.providers

    def test_get_available_providers(self):
        """Test getting available providers."""
        service = LLMService()

        # Mock all providers as unavailable
        for provider in service.providers.values():
            provider.is_available = Mock(return_value=False)

        assert service.get_available_providers() == []

        # Mock Gemini as available
        service.providers["gemini"].is_available = Mock(return_value=True)
        assert service.get_available_providers() == ["gemini"]

    def test_get_default_provider(self):
        """Test default provider selection."""
        service = LLMService()

        # Mock providers availability
        service.providers["openai"].is_available = Mock(return_value=True)
        service.providers["gemini"].is_available = Mock(return_value=True)

        # Should prefer OpenAI
        assert service.get_default_provider() == "openai"

        # If OpenAI not available, should use first available
        service.providers["openai"].is_available = Mock(return_value=False)
        assert service.get_default_provider() == "gemini"

    def test_get_model_with_specific_provider(self):
        """Test getting model with specific provider."""
        service = LLMService()

        # Mock Gemini provider
        mock_model = Mock()
        service.providers["gemini"].is_available = Mock(return_value=True)
        service.providers["gemini"].get_model = Mock(return_value=mock_model)

        model = service.get_model(provider="gemini", model="gemini-2.0-flash-lite")

        service.providers["gemini"].get_model.assert_called_once_with(
            model="gemini-2.0-flash-lite"
        )
        assert model == mock_model

    def test_get_model_with_unavailable_provider(self):
        """Test getting model with unavailable provider."""
        service = LLMService()

        service.providers["gemini"].is_available = Mock(return_value=False)

        with pytest.raises(RuntimeError, match="Provider gemini is not available"):
            service.get_model(provider="gemini")

    def test_get_model_with_unknown_provider(self):
        """Test getting model with unknown provider."""
        service = LLMService()

        with pytest.raises(ValueError, match="Unknown provider: unknown"):
            service.get_model(provider="unknown")

    @pytest.mark.asyncio
    async def test_generate_response(self):
        """Test response generation."""
        service = LLMService()

        # Mock model and response
        mock_model = AsyncMock()
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_model.ainvoke.return_value = mock_response

        service.providers["gemini"].is_available = Mock(return_value=True)
        service.providers["gemini"].get_model = Mock(return_value=mock_model)

        response = await service.generate_response(
            messages=["Test message"], provider="gemini"
        )

        assert response == "Test response"
        mock_model.ainvoke.assert_called_once()

    def test_get_provider_info(self):
        """Test getting provider information."""
        service = LLMService()

        # Mock provider availability
        service.providers["openai"].is_available = Mock(return_value=True)
        service.providers["gemini"].is_available = Mock(return_value=True)

        info = service.get_provider_info()

        assert info["openai"]["available"] is True
        assert info["openai"]["is_default"] is True  # OpenAI is preferred
        assert info["gemini"]["available"] is True
        assert info["gemini"]["is_default"] is False


class TestGeminiIntegration:
    """Integration tests specifically for Gemini."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="No Google API key")
    async def test_gemini_real_api_call(self):
        """Test real API call to Gemini (requires API key)."""
        service = LLMService()

        if "gemini" not in service.get_available_providers():
            pytest.skip("Gemini not available")

        response = await service.generate_response(
            messages=["Say hello in exactly 5 words."],
            provider="gemini",
            model="gemini-2.0-flash-lite",
        )

        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="No Google API key")
    async def test_gemini_resume_task(self):
        """Test Gemini with resume-related task."""
        service = LLMService()

        if "gemini" not in service.get_available_providers():
            pytest.skip("Gemini not available")

        prompt = "List 3 important skills for a Python developer resume. Be concise."

        response = await service.generate_response(
            messages=[prompt], provider="gemini", model="gemini-2.0-flash-lite"
        )

        assert isinstance(response, str)
        assert len(response) > 0
        # Should contain relevant programming terms
        assert any(
            term in response.lower()
            for term in ["python", "programming", "software", "development"]
        )


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
