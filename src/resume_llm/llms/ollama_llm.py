from langchain_ollama import ChatOllama


def get_llm(model: str = "qwen3.6:35b-a3b", base_url: str | None = None, **kwargs):
    """
    Returns a LangChain Ollama chat model instance.
    Args:
        model (str): Model name, e.g. 'qwen3.6:35b-a3b'.
        base_url (str, optional): Ollama server URL. If None, uses default.
        **kwargs: Additional args for ChatOllama.
    """
    return ChatOllama(model=model, base_url=base_url, **kwargs)
