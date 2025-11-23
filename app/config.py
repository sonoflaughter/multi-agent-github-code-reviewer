try:
    # pydantic v2 splits BaseSettings into pydantic-settings
    from pydantic_settings import BaseSettings
except Exception:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    github_token: str
    github_repo: str
    host: str = "0.0.0.0"
    port: int = 8000
    vector_db_url: str | None = None
    ci_runner_url: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
