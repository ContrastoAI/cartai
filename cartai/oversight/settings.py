from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Settings for the CartAI oversight agent."""

    OPENAI_API_KEY: str = Field(
        default=...,
        description="OpenAI API key for authentication",
        env="OPENAI_API_KEY",
    )

    MODEL_NAME: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model name to use",
        env="MODEL_NAME",
    )

    MLFLOW_SERVER_SCRIPT: str = Field(
        default="http://127.0.0.1:9000/mcp/mlflow/mcp",
        description="URL for the MLflow server script",
        env="MLFLOW_SERVER_SCRIPT",
    )

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


# Create settings instance
settings = Settings()
