from typing import Optional

from langchain_openai import ChatOpenAI


def get_llm(
    model: str = "gpt-5.6-luna",
    api_key: Optional[str] = None,
    **kwargs,
):
    """
    Returns a LangChain OpenAI LLM instance.
    Args:
        model (str): Model name, e.g. 'gpt-5.6-luna'.
        api_key (str, optional): OpenAI API key. If None, uses env var.
        **kwargs: Additional args for ChatOpenAI.
    """
    return ChatOpenAI(model=model, openai_api_key=api_key, **kwargs)
