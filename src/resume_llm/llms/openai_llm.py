from typing import Optional

from langchain_openai import ChatOpenAI


def get_llm(
    model: str = "gpt-4.1-nano-2025-04-14",
    api_key: Optional[str] = None,
    **kwargs,
):
    """
    Returns a LangChain OpenAI LLM instance.
    Args:
        model (str): Model name, e.g. 'gpt-4.1-nano-2025-04-14'.
        api_key (str, optional): OpenAI API key. If None, uses env var.
        **kwargs: Additional args for ChatOpenAI.
    """
    return ChatOpenAI(model=model, openai_api_key=api_key, **kwargs)
