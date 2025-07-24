from typing import Optional

from langchain_community.llms import HuggingFaceEndpoint


def get_llm(
    model: str = "HuggingFaceH4/zephyr-7b-beta",
    api_key: Optional[str] = None,
    endpoint_url: Optional[str] = None,
    **kwargs,
):
    """
    Returns a LangChain HuggingFace LLM instance.
    Args:
        model (str): Model name, e.g. 'HuggingFaceH4/zephyr-7b-beta'.
        api_key (str, optional): HF API key. If None, uses env var.
        endpoint_url (str, optional): Custom endpoint URL for inference API.
        **kwargs: Additional args for HuggingFaceEndpoint.
    """
    return HuggingFaceEndpoint(
        repo_id=model,
        huggingfacehub_api_key=api_key,
        endpoint_url=endpoint_url,
        **kwargs,
    )
