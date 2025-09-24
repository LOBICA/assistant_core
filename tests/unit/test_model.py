from assistant_core.models import GPT_5, GPT_5_MINI, GPT_5_NANO, load_openai_model

OPENAI_API_KEY = "test_key"


def test_default_model():
    model = load_openai_model(openai_api_key=OPENAI_API_KEY)
    assert model is not None


def test_gpt_5_nano_model():
    model = load_openai_model(openai_api_key=OPENAI_API_KEY, model_name=GPT_5_NANO)
    assert model is not None


def test_gpt_5_mini_model():
    model = load_openai_model(openai_api_key=OPENAI_API_KEY, model_name=GPT_5_MINI)
    assert model is not None


def test_gpt_5_model():
    model = load_openai_model(openai_api_key=OPENAI_API_KEY, model_name=GPT_5)
    assert model is not None
