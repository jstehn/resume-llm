from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm(
    model: str = "gemini-3.5-flash-lite",
    api_key: str | None = None,
    **kwargs,
):
    """
    Returns a LangChain Google Gemini LLM instance.
    Args:
        model (str): Model name, e.g. 'gemini-3.5-flash-lite'.
        api_key (str, optional): Google API key. If None, uses env var.
        **kwargs: Additional args for ChatGoogleGenerativeAI.
    """
    return ChatGoogleGenerativeAI(model=model, google_api_key=api_key, **kwargs)
