import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY") or os.getenv("MINIMAX_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL") or os.getenv("MINIMAX_BASE_URL", "")
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    github_token: str = os.getenv("GITHUB_TOKEN", "")

    model_intent: str = os.getenv("MODEL_INTENT", "gpt-4o-mini")
    model_planner: str = os.getenv("MODEL_PLANNER", "gpt-4o")
    model_generator: str = os.getenv("MODEL_GENERATOR", "gpt-4.1")

    default_language: str = os.getenv("DEFAULT_LANGUAGE", "zh")
    max_nodes: int = int(os.getenv("MAX_NODES", "6"))
    retrieval_top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))
    http_timeout_seconds: float = float(os.getenv("HTTP_TIMEOUT_SECONDS", "10"))


settings = Settings()
