import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class PathGenSettings:
    """path_gen 模块的配置"""
    openai_api_key: str = os.getenv("OPENAI_API_KEY") or os.getenv("MINIMAX_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL") or os.getenv("MINIMAX_BASE_URL", "")
    model: str = os.getenv("MODEL_PATH_GEN", "abab6.5s-chat")
    temperature: float = float(os.getenv("TEMPERATURE_PATH_GEN", "0.7"))


path_gen_settings = PathGenSettings()
