from langchain_openai import ChatOpenAI
from pydantic import SecretStr


def get_llm(
    model: str = "gpt-5.6-luna",
    api_key: str | None = None,
    **kwargs,
):
    """
    Returns a LangChain OpenAI LLM instance.
    Args:
        model (str): Model name, e.g. 'gpt-5.6-luna'.
        api_key (str, optional): OpenAI API key. If None, uses env var.
        **kwargs: Additional args for ChatOpenAI.
    """
    if api_key is not None:
        kwargs["api_key"] = SecretStr(api_key)
    return ChatOpenAI(model=model, **kwargs)
