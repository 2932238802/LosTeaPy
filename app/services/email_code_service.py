import logging
import random
import smtplib
import socket
import ssl
import time
from datetime import datetime, timedelta
from email.message import EmailMessage

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.email_code import EmailCode
from app.models.user import User

logger = logging.getLogger(__name__)


def generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def _open_smtp_connection(settings):
    timeout = max(5, settings.smtp_timeout_seconds)

    if settings.smtp_use_ssl:
        context = ssl.create_default_context()
        return smtplib.SMTP_SSL(
            settings.smtp_host,
            settings.smtp_port,
            timeout=timeout,
            context=context,
        )

    smtp = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=timeout)
    smtp.ehlo()
    if settings.smtp_use_starttls:
        smtp.starttls(context=ssl.create_default_context())
        smtp.ehlo()
    return smtp


def send_email_code(to_email: str, code: str) -> None:
    settings = get_settings()

    if not settings.smtp_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="邮件服务未配置：请先在 .env 中填写 SMTP_PASSWORD，163 邮箱需要填写授权码不是邮箱登录密码",
        )

    message = EmailMessage()
    message["Subject"] = "茗不虚传注册验证码"
    message["From"] = settings.smtp_user
    message["To"] = to_email
    message.set_content(
        f"你的注册验证码是：{code}\n\n"
        f"验证码 {settings.email_code_expire_minutes} 分钟内有效\n"
        "如果不是你本人操作，请忽略这封邮件"
    )

    last_error: Exception | None = None
    max_attempts = max(1, settings.smtp_max_retries + 1)

    for attempt in range(1, max_attempts + 1):
        smtp = None
        try:
            smtp = _open_smtp_connection(settings)
            smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(message)
            return

        except smtplib.SMTPAuthenticationError as e:
            logger.exception("SMTP 认证失败: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"邮件服务认证失败：{e.smtp_error.decode(errors='ignore') if isinstance(e.smtp_error, bytes) else e.smtp_error}",
            )

        except smtplib.SMTPSenderRefused as e:
            logger.exception("SMTP 发件被拒: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"邮件发送被拒绝：{e.smtp_error.decode(errors='ignore') if isinstance(e.smtp_error, bytes) else e.smtp_error}",
            )

        except (ConnectionResetError, TimeoutError, OSError, socket.timeout, ssl.SSLError, smtplib.SMTPException) as e:
            last_error = e
            logger.warning(
                "SMTP 发送验证码失败，准备重试(%s/%s): %s %s",
                attempt,
                max_attempts,
                type(e).__name__,
                e,
            )
            if attempt < max_attempts:
                time.sleep(min(2 * attempt, 5))
                continue

        finally:
            if smtp is not None:
                try:
                    smtp.quit()
                except Exception:
                    try:
                        smtp.close()
                    except Exception:
                        pass

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"邮件发送失败：{type(last_error).__name__} {last_error}",
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

    print(f"[LosTea] 注册验证码 email={email}, code={code}")

    try:
        send_email_code(email, code)
    except HTTPException as e:
        # 邮件发送失败时不要把整个流程拦死
        # 验证码已经写进数据库并在后端控制台打印，方便本地调试
        logger.warning(
            "邮件发送失败但验证码已生成，可在后端控制台查看。email=%s detail=%s",
            email,
            e.detail,
        )
    except Exception as e:
        logger.exception("邮件发送未知异常，验证码仍生效: %s", e)


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
