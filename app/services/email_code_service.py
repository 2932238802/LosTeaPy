import random
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.email_code import EmailCode
from app.models.user import User


def generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def send_email_code(to_email: str, code: str) -> None:
    settings = get_settings()

    if not settings.smtp_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="邮件服务未配置：请先在 .env 中填写 SMTP_PASSWORD。163 邮箱需要填写授权码，不是邮箱登录密码。",
        )

    message = EmailMessage()
    message["Subject"] = "茗不虚传注册验证码"
    message["From"] = settings.smtp_user
    message["To"] = to_email
    message.set_content(
        f"你的注册验证码是：{code}\n\n"
        f"验证码 {settings.email_code_expire_minutes} 分钟内有效。\n"
        "如果不是你本人操作，请忽略这封邮件。"
    )

    try:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as smtp:
            smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(message)
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="邮件服务认证失败：请检查 163 邮箱 SMTP 授权码是否正确。",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证码邮件发送失败：{type(e).__name__}",
        )


def create_register_code(email: str, db: Session) -> None:
    exists = db.query(User).filter(User.email == email).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已注册",
        )

    settings = get_settings()
    code = generate_code()

    email_code = EmailCode(
        email=email,
        code=code,
        scene="register",
        expires_at=datetime.utcnow() + timedelta(minutes=settings.email_code_expire_minutes),
    )

    db.add(email_code)
    db.commit()

    send_email_code(email, code)


def verify_register_code(email: str, code: str, db: Session) -> None:
    email_code = db.query(EmailCode).filter(
        EmailCode.email == email,
        EmailCode.code == code,
        EmailCode.scene == "register",
        EmailCode.used_at.is_(None),
    ).order_by(EmailCode.created_at.desc()).first()

    if not email_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期",
        )

    if email_code.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期",
        )

    email_code.used_at = datetime.utcnow()
    db.commit()
