from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.orders import router as orders_router
from app.config import get_settings
from app.schemas.chat import ChatRequest, ChatResponse, HealthResponse
from app.services.chat_service import chat_with_llm

router = APIRouter()
router.include_router(auth_router)
router.include_router(orders_router)


@router.get("/", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", service=settings.app_name)


@router.get("/api/health", response_model=HealthResponse)
def api_health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", service=settings.app_name)


# AI 聊天接口
# ChatRequest 是请求体，ChatResponse 是返回体
@router.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    return chat_with_llm(req)
