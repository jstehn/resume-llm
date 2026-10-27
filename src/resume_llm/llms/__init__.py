from langchain_core.language_models import BaseChatModel

from .anthropic_llm import get_llm as get_anthropic_llm
from .google_llm import get_llm as get_google_llm
from .hf_llm import get_llm as get_hf_llm
from .ollama_llm import get_llm as get_ollama_llm
from .openai_llm import get_llm as get_openai_llm

AVAILABLE_LLMS = [
    "openai",
    "anthropic",
    "ollama",
    "google",
    "huggingface",
]

DEFAULT_MODELS = {
    "openai": "gpt-5.6-luna",
    "anthropic": "claude-sonnet-5-5",
    "ollama": "qwen3.6:35b-a3b",
    "google": "gemini-3.5-flash-lite",
    "huggingface": "HuggingFaceH4/zephyr-7b-beta",
}


def get_llm(
    name: str = "openai",
    model: str | None = None,
    api_key: str | None = None,
    **kwargs,
) -> BaseChatModel:
    """
    Select and return an LLM instance by name.
    Args:
        name (str): One of AVAILABLE_LLMS.
        model (str, optional): Model name for the LLM.
        api_key (str, optional): API key for the LLM.
        **kwargs: Additional provider-specific arguments.
    Returns:
        LangChain chat model instance.
    Raises:
        ValueError: If name is not recognized.
    """
    name = name.lower()
    if name not in AVAILABLE_LLMS:
        raise ValueError(f"Unknown LLM name: {name}. Available: {AVAILABLE_LLMS}")
    model = model or DEFAULT_MODELS.get(name)
    if model is None:
        raise ValueError(f"No model specified and no default for provider '{name}'")
    if name == "openai":
        return get_openai_llm(model=model, api_key=api_key, **kwargs)
    elif name == "anthropic":
        return get_anthropic_llm(model=model, api_key=api_key, **kwargs)
    elif name == "ollama":
        return get_ollama_llm(model=model, **kwargs)
    elif name == "google":
        return get_google_llm(model=model, api_key=api_key, **kwargs)
    elif name == "huggingface":
        return get_hf_llm(model=model, api_key=api_key, **kwargs)
    raise ValueError(f"No factory registered for provider '{name}'")
