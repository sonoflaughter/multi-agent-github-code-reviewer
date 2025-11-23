try:
    # pydantic v2 splits BaseSettings into pydantic-settings
    from pydantic_settings import BaseSettings
except Exception:
    from pydantic import BaseSettings

try:
    # ConfigDict is available in pydantic v2
    from pydantic import ConfigDict
except Exception:
    ConfigDict = dict


class Settings(BaseSettings):
    github_token: str
    github_repo: str
    host: str = "0.0.0.0"
    port: int = 8000
    vector_db_url: str | None = None
    ci_runner_url: str | None = None

    # Allow extra env vars (tests/CI may set additional vars like S3_BUCKET)
    model_config = ConfigDict(env_file=".env", extra="allow")


settings = Settings()
