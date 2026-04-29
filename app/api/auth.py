from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    SendCodeRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import login_user, register_user, to_user_response
from app.services.email_code_service import create_register_code

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/send-code", response_model=MessageResponse)
def send_code(
    req: SendCodeRequest,
    db: Session = Depends(get_db),
) -> MessageResponse:
    create_register_code(req.email, db)
    return MessageResponse(message="验证码已发送")


@router.post("/register", response_model=TokenResponse)
def register(
    req: RegisterRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    return register_user(req, db)


@router.post("/login", response_model=TokenResponse)
def login(
    req: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    return login_user(req, db)


@router.get("/me", response_model=UserResponse)
def me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return to_user_response(current_user)
