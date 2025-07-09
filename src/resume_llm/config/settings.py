"""Configuration management for Resume LLM."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # Database
    database_url: str = Field(default="sqlite:///./resume_llm.db")
    secret_key: str = Field(default="change-me-in-production")

    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    google_api_key: Optional[str] = Field(default=None)

    # Local LLM Configuration
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama2")

    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    debug: bool = Field(default=False)

    # PDF Configuration
    pdf_template_dir: str = Field(default="./data/templates/resume_templates")

    # Data directories
    data_dir: Path = Field(default=Path("./data"))
    schemas_dir: Path = Field(default=Path("./data/schemas"))
    examples_dir: Path = Field(default=Path("./data/examples"))

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration based on available API keys."""
        config = {}

        if self.openai_api_key:
            config["openai"] = {"api_key": self.openai_api_key, "model": "gpt-4"}

        if self.anthropic_api_key:
            config["anthropic"] = {
                "api_key": self.anthropic_api_key,
                "model": "claude-3-sonnet-20240229",
            }

        # Always include local option
        config["ollama"] = {
            "base_url": self.ollama_base_url,
            "model": self.ollama_model,
        }

        return config


# Global settings instance
settings = Settings()
