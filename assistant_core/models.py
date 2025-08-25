from langchain_openai import ChatOpenAI

from assistant_core.settings import OPENAI_API_KEY

GPT_4O_MINI = "gpt-4o-mini"
GPT_41_MINI = "gpt-4.1-mini"
GPT_5_NANO = "gpt-5-nano"
GPT_5_MINI = "gpt-5-mini"

DEFAULT_MODEL = GPT_5_NANO


def load_openai_model(model_name: str = DEFAULT_MODEL):
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set.")

    return ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=model_name,
        verbosity="low",
    )
