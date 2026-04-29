from datetime import datetime

from pydantic import BaseModel, Field


class OrderItemInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    price: float = Field(ge=0)
    qty: int = Field(ge=1, le=99)


class OrderCreate(BaseModel):
    contact_name: str = Field(min_length=1, max_length=60)
    contact_phone: str = Field(min_length=1, max_length=30)
    contact_address: str = Field(min_length=1, max_length=255)
    note: str | None = Field(default=None, max_length=500)
    items: list[OrderItemInput] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    id: int
    name: str
    price: float
    qty: int


class OrderResponse(BaseModel):
    id: int
    contact_name: str
    contact_phone: str
    contact_address: str
    note: str | None = None
    total_price: float
    status: str
    created_at: datetime
    items: list[OrderItemResponse]
