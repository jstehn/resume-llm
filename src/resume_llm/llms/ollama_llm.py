from typing import Optional

from langchain_community.llms import Ollama


def get_llm(model: str = "llama2", base_url: Optional[str] = None, **kwargs):
    """
    Returns a LangChain Ollama LLM instance.
    Args:
        model (str): Model name, e.g. 'llama2'.
        base_url (str, optional): Ollama server URL. If None, uses default.
        **kwargs: Additional args for Ollama.
    """
    return Ollama(model=model, base_url=base_url, **kwargs)
