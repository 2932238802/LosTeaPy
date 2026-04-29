from fastapi import APIRouter

from app.chat_service import chat_with_llm
from app.config import get_settings
from app.schemas import ChatRequest, ChatResponse, HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", service=settings.app_name)


@router.get("/api/health", response_model=HealthResponse)
def api_health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", service=settings.app_name)


@router.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    return chat_with_llm(req)
