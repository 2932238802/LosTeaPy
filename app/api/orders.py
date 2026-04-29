from fastapi import APIRouter, Depends, Header
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import create_order, list_my_orders

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _try_get_user(
    authorization: str | None,
    db: Session,
) -> User | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        return None

    try:
        payload = decode_access_token(token)
    except JWTError:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    try:
        return db.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


@router.post("", response_model=OrderResponse)
def submit_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> OrderResponse:
    # 允许未登录下单，登录状态则关联到当前用户
    current_user = _try_get_user(authorization, db)
    return create_order(payload, db, current_user=current_user)


@router.get("/mine", response_model=list[OrderResponse])
def my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[OrderResponse]:
    return list_my_orders(db, current_user)
