from langchain_openai import ChatOpenAI

GPT_5_NANO = "gpt-5-nano"
GPT_5_MINI = "gpt-5-mini"
GPT_5 = "gpt-5"

DEFAULT_MODEL = GPT_5_NANO


def load_openai_model(
    openai_api_key: str,
    model_name: str = DEFAULT_MODEL,
    use_responses_api: bool = False,
    verbosity: str = "low",
    **kwargs,
) -> ChatOpenAI:
    return ChatOpenAI(
        api_key=openai_api_key,
        model=model_name,
        verbosity=verbosity,
        use_responses_api=use_responses_api,
        **kwargs,
    )
