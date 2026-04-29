from typing import List, Literal

from pydantic import BaseModel, Field


class ChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(default="", max_length=8000)


class ChatRequest(BaseModel):
    message: str = Field(default="", max_length=8000)
    history: List[ChatHistoryItem] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    error: str | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
