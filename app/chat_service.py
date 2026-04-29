from typing import Any

from openai import AuthenticationError, BadRequestError
from openai.types.chat import ChatCompletionMessageParam

from app.config import get_settings
from app.llm_client import get_llm_client
from app.prompt_loader import load_system_prompt
from app.schemas import ChatRequest, ChatResponse

EMPTY_MESSAGE_REPLY = "你可以先告诉我想了解导览、预约、茶叶、文创、溯源、就餐、团购、茶金融、市场调研还是茶碳汇 ~ "
EMPTY_REPLY_FALLBACK = "抱歉，我暂时没有生成有效回答，你可以换个问法再试试 ~ "
LLM_ERROR_FALLBACK = "抱歉，茶小泽暂时连接 大模型 失败了你可以先问我导览、预约、茶叶、文创、溯源、就餐、团购、茶金融、市场调研或茶碳汇相关问题 ~ "
AUTH_ERROR_FALLBACK = "抱歉，茶小泽暂时无法连接大模型：DeepSeek API Key 无效或未生效，请检查后端 .env 里的 DEEPSEEK_API_KEY ~ "
BAD_REQUEST_FALLBACK = "抱歉，茶小泽暂时无法连接大模型：DeepSeek 请求参数不兼容，请检查模型名、thinking 或 reasoning 配置 ~ "


def build_messages(req: ChatRequest) -> list[ChatCompletionMessageParam]:
    settings = get_settings()
    system_prompt = load_system_prompt()

    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    for item in (req.history or [])[-settings.max_history:]:
        content = (item.content or "").strip()
        if not content:
            continue

        if item.role == "user":
            messages.append({
                "role": "user",
                "content": content[:settings.max_history_chars],
            })
        elif item.role == "assistant":
            messages.append({
                "role": "assistant",
                "content": content[:settings.max_history_chars],
            })

    messages.append({
        "role": "user",
        "content": req.message.strip()[:settings.max_message_chars],
    })

    return messages


def build_extra_kwargs() -> dict[str, Any]:
    """根据配置动态拼接 DeepSeek v4-pro 额外参数"""
    settings = get_settings()
    extra: dict[str, Any] = {}

    if settings.reasoning_effort:
        extra["reasoning_effort"] = settings.reasoning_effort

    if settings.thinking_enabled:
        extra["extra_body"] = {"thinking": {"type": "enabled"}}

    return extra


def chat_with_llm(req: ChatRequest) -> ChatResponse:
    settings = get_settings()
    message = req.message.strip()

    if not message:
        return ChatResponse(reply=EMPTY_MESSAGE_REPLY)

    try:
        client = get_llm_client()
        completion = client.chat.completions.create(
            model=settings.deepseek_model,
            messages=build_messages(req),
            temperature=settings.temperature,
            stream=False,
            **build_extra_kwargs(),
        )

        reply = completion.choices[0].message.content
        if not reply or not reply.strip():
            return ChatResponse(reply=EMPTY_REPLY_FALLBACK)

        return ChatResponse(reply=reply.strip())

    except AuthenticationError as e:
        return ChatResponse(
            reply=AUTH_ERROR_FALLBACK,
            error=f"AuthenticationError: {e}",
        )

    except BadRequestError as e:
        return ChatResponse(
            reply=BAD_REQUEST_FALLBACK,
            error=f"BadRequestError: {e}",
        )

    except Exception as e:
        return ChatResponse(
            reply=LLM_ERROR_FALLBACK,
            error=f"{type(e).__name__}: {e}",
        )
