import warnings

from langchain_openai import ChatOpenAI

GPT_5_NANO = "gpt-5-nano"
GPT_5_MINI = "gpt-5-mini"
GPT_5 = "gpt-5"

DEFAULT_MODEL = GPT_5_NANO


def load_openai_model(
    openai_api_key: str, model_name: str = DEFAULT_MODEL
) -> ChatOpenAI:
    warnings.warn(
        "load_openai_model is deprecated and will be removed in a future version. "
        "Please use load_default_model instead "
        "or create ChatOpenAI instances directly.",
        DeprecationWarning,
        stacklevel=2,
    )
    return ChatOpenAI(
        api_key=openai_api_key,
        model=model_name,
        verbosity="low",
    )


def load_default_model(
    openai_api_key: str,
) -> ChatOpenAI:
    return ChatOpenAI(
        api_key=openai_api_key,
        model=DEFAULT_MODEL,
        verbosity="low",
        use_previous_response_id=True,
    )
