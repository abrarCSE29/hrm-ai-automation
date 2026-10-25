from unittest.mock import patch

from app.core.config import settings
from app.core.models import get_chat_model, run_with_fallback


def test_factory_returns_groq_in_dev(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "dev")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "test")
    model = get_chat_model("dev")
    assert type(model).__name__ == "Groq"
    assert type(model).__module__.endswith("groq")


def test_factory_returns_openai_in_production(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "test")
    model = get_chat_model("production")
    assert type(model).__name__ == "OpenAIChat"


def test_fallback_hook_retries_with_fallback(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "dev")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "test")
    monkeypatch.setattr(settings, "MODEL_PRIMARY_GROQ", "primary-model")
    monkeypatch.setattr(settings, "MODEL_FALLBACK_GROQ", "fallback-model")

    calls = {"n": 0}

    def fake_get_chat_model(env=None, fallback=False):
        class M:
            def __init__(self, name):
                self.name = name

        mid = "fallback-model" if fallback else "primary-model"
        return M(mid)

    # make primary operation fail once
    def operation(model):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("primary failed")
        return f"ok-with-{model.name}"

    with patch("app.core.models.get_chat_model", side_effect=fake_get_chat_model):
        result = run_with_fallback(operation, env="dev")
    assert result == "ok-with-fallback-model"
    assert calls["n"] == 2


def test_fallback_hook_no_fallback_raises(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "dev")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "test")
    monkeypatch.setattr(settings, "MODEL_FALLBACK_GROQ", "")

    def fake_get_chat_model(env=None, fallback=False):
        class M:
            name = "primary"

        return M()

    def operation(model):
        raise RuntimeError("boom")

    with patch("app.core.models.get_chat_model", side_effect=fake_get_chat_model):
        try:
            run_with_fallback(operation, env="dev")
        except RuntimeError as exc:
            assert "boom" in str(exc)
        else:
            raise AssertionError("expected RuntimeError")
