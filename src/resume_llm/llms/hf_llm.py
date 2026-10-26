from typing import Any

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint


def get_llm(
    model: str = "HuggingFaceH4/zephyr-7b-beta",
    api_key: str | None = None,
    endpoint_url: str | None = None,
    **kwargs,
):
    """
    Returns a LangChain HuggingFace chat model instance.
    Args:
        model (str): Model name, e.g. 'HuggingFaceH4/zephyr-7b-beta'.
        api_key (str, optional): HF API token. If None, uses env var.
        endpoint_url (str, optional): Custom endpoint URL for inference API.
        **kwargs: Additional args for HuggingFaceEndpoint.
    """
    # HuggingFaceEndpoint rejects repo_id and endpoint_url together
    endpoint_args: dict[str, Any] = (
        {"endpoint_url": endpoint_url} if endpoint_url else {"repo_id": model}
    )
    llm = HuggingFaceEndpoint(
        huggingfacehub_api_token=api_key,
        **endpoint_args,
        **kwargs,
    )
    return ChatHuggingFace(llm=llm)
