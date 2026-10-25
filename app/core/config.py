"""Application configuration loaded from environment / .env."""


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ENVIRONMENT: str = "dev"

    # LLM provider credentials
    GROQ_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None

    # Model ids per provider (primary / fallback). Override via env vars.
    MODEL_PRIMARY_GROQ: str = "openai/gpt-oss-120b"
    MODEL_FALLBACK_GROQ: str = ""
    MODEL_PRIMARY_OPENAI: str = "gpt-4o-mini"
    MODEL_FALLBACK_OPENAI: str = ""

    # Example for a future provider (Anthropic) - uncomment and add a factory branch:
    # ANTHROPIC_API_KEY: Optional[str] = None
    # MODEL_PRIMARY_ANTHROPIC: str = "claude-3-5-sonnet-latest"
    # MODEL_FALLBACK_ANTHROPIC: str = ""

    DATABASE_URL: str = "sqlite:///./hrm.db"
    LOG_LEVEL: str = "INFO"

    # LangSmith observability
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_PROJECT: str = "hrm-automation-ai"
    LANGSMITH_TRACING: bool = False
    LANGSMITH_ENDPOINT: str | None = None
    LANGCHAIN_TRACING_V2: bool = False

    # Model config shape: primary/fallback pairs per environment.
    # Adding a provider = new factory branch in app/core/models.py + 2 env vars above.


settings = Settings()


def get_model_pair_config(env: str) -> dict:
    """Return {primary, fallback} model ids for the given environment."""
    env = (env or "dev").lower()
    if env in ("production", "prod"):
        return {
            "primary": settings.MODEL_PRIMARY_OPENAI,
            "fallback": settings.MODEL_FALLBACK_OPENAI,
        }
    # dev (and any unknown) defaults to Groq
    return {
        "primary": settings.MODEL_PRIMARY_GROQ,
        "fallback": settings.MODEL_FALLBACK_GROQ,
    }


# Commented example for extending with another provider:
# elif env == "anthropic":
#     return {"primary": settings.MODEL_PRIMARY_ANTHROPIC, "fallback": settings.MODEL_FALLBACK_ANTHROPIC}
