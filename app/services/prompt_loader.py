from functools import lru_cache

from app.config import get_settings

FALLBACK_SYSTEM_PROMPT = """
你是“茶小泽”，安顶山云雾茶数字焕新平台的 AI 客服与导览助手
请使用中文回答，语气亲切、专业、简洁
不要编造联系电话、政策、库存、付款方式
不确定时明确说明不确定，并建议用户查看页面信息或联系平台客服确认
""".strip()


@lru_cache
def load_system_prompt() -> str:
    settings = get_settings()

    try:
        content = settings.prompt_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return FALLBACK_SYSTEM_PROMPT

    return content or FALLBACK_SYSTEM_PROMPT
