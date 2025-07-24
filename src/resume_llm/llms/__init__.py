from typing import Optional

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
    "openai": "gpt-4.1-nano-2025-04-14",
    "anthropic": "claude-3-5-sonnet-latest",
    "ollama": "llama2",
    "google": "gemini-2.0-flash-lite",
    "huggingface": "HuggingFaceH4/zephyr-7b-beta",
}


def get_llm(
    name: str = "openai",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs,
):
    """
    Select and return an LLM instance by name.
    Args:
        name (str): One of AVAILABLE_LLMS.
        model (str, optional): Model name for the LLM.
        api_key (str, optional): API key for the LLM.
        **kwargs: Additional provider-specific arguments.
    Returns:
        LangChain LLM instance.
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
