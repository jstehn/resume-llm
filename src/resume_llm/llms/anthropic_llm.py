from typing import Optional

from langchain_anthropic import ChatAnthropic


def get_llm(
    model: str = "claude-3-5-sonnet-latest",
    api_key: Optional[str] = None,
    **kwargs,
):
    """
    Returns a LangChain Anthropic LLM instance.
    Args:
        model (str): Model name, e.g. 'claude-3-5-sonnet-latest'.
        api_key (str, optional): Anthropic API key. If None, uses env var.
        **kwargs: Additional args for ChatAnthropic.
    """
    return ChatAnthropic(model=model, anthropic_api_key=api_key, **kwargs)
