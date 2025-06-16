from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the CartAI oversight agent."""

    OPENAI_API_KEY: str = ""

    MODEL_NAME: str = "gpt-4o-mini"

    MLFLOW_SERVER_SCRIPT: str = "http://127.0.0.1:9000/mcp/mlflow/mcp"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


# Create settings instance
settings = Settings()
