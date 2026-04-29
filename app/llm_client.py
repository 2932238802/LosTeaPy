from openai import OpenAI
from app.config import get_settings

def get_llm_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
    )
