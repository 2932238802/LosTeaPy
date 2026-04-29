from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.email_code_service import verify_register_code


def to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username or user.email,
    )


def to_token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id),
        user=to_user_response(user),
    )


def register_user(req: RegisterRequest, db: Session) -> TokenResponse:
    exists = db.query(User).filter(User.email == req.email).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已注册",
        )

    verify_register_code(req.email, req.code, db)

    user = User(
        email=req.email,
        username=req.email,
        password_hash=hash_password(req.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return to_token_response(user)


def login_user(req: LoginRequest, db: Session) -> TokenResponse:
    user = db.query(User).filter(User.email == req.email).first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
        )

    return to_token_response(user)
