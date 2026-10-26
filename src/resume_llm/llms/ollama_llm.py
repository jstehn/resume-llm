from typing import Optional

from langchain_ollama import ChatOllama


def get_llm(model: str = "llama3.2", base_url: Optional[str] = None, **kwargs):
    """
    Returns a LangChain Ollama chat model instance.
    Args:
        model (str): Model name, e.g. 'llama3.2'.
        base_url (str, optional): Ollama server URL. If None, uses default.
        **kwargs: Additional args for ChatOllama.
    """
    return ChatOllama(model=model, base_url=base_url, **kwargs)
