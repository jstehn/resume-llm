"""Configuration management for Resume LLM."""

import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = Field(default="sqlite:///./resume_llm.db", env="DATABASE_URL")
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Local LLM Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama2", env="OLLAMA_MODEL")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # PDF Configuration
    pdf_template_dir: str = Field(default="./data/templates/resume_templates", env="PDF_TEMPLATE_DIR")
    
    # Data directories
    data_dir: Path = Field(default=Path("./data"))
    schemas_dir: Path = Field(default=Path("./data/schemas"))
    examples_dir: Path = Field(default=Path("./data/examples"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration based on available API keys."""
        config = {}
        
        if self.openai_api_key:
            config["openai"] = {
                "api_key": self.openai_api_key,
                "model": "gpt-4"
            }
        
        if self.anthropic_api_key:
            config["anthropic"] = {
                "api_key": self.anthropic_api_key,
                "model": "claude-3-sonnet-20240229"
            }
        
        # Always include local option
        config["ollama"] = {
            "base_url": self.ollama_base_url,
            "model": self.ollama_model
        }
        
        return config


# Global settings instance
settings = Settings()
