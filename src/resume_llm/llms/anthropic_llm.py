from langchain_anthropic import ChatAnthropic
from pydantic import SecretStr


def get_llm(
    model: str = "claude-sonnet-5-5",
    api_key: str | None = None,
    **kwargs,
):
    """
    Returns a LangChain Anthropic LLM instance.
    Args:
        model (str): Model name, e.g. 'claude-sonnet-5-5'.
        api_key (str, optional): Anthropic API key. If None, uses env var.
        **kwargs: Additional args for ChatAnthropic.
    """
    if api_key is not None:
        kwargs["api_key"] = SecretStr(api_key)
    return ChatAnthropic(model_name=model, **kwargs)
