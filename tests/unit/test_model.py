from assistant_core.models import load_default_model

OPENAI_API_KEY = "test_key"


def test_default_model():
    model = load_default_model(openai_api_key=OPENAI_API_KEY)
    assert model
