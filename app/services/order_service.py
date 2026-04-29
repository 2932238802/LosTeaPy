from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderCreate, OrderItemResponse, OrderResponse


def _to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        contact_name=order.contact_name,
        contact_phone=order.contact_phone,
        contact_address=order.contact_address,
        note=order.note,
        total_price=order.total_price,
        status=order.status,
        created_at=order.created_at,
        items=[
            OrderItemResponse(
                id=item.id,
                name=item.name,
                price=item.price,
                qty=item.qty,
            )
            for item in order.items
        ],
    )


def create_order(
    payload: OrderCreate,
    db: Session,
    current_user: User | None = None,
) -> OrderResponse:
    if not payload.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="购物车为空，无法提交订单",
        )

    total_price = sum(item.price * item.qty for item in payload.items)

    order = Order(
        user_id=current_user.id if current_user else None,
        contact_name=payload.contact_name,
        contact_phone=payload.contact_phone,
        contact_address=payload.contact_address,
        note=payload.note,
        total_price=total_price,
        status="pending",
        items=[
            OrderItem(name=item.name, price=item.price, qty=item.qty)
            for item in payload.items
        ],
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return _to_response(order)


def list_my_orders(
    db: Session,
    current_user: User,
) -> list[OrderResponse]:
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return [_to_response(order) for order in orders]
