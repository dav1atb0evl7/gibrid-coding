import hmac
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.database.session import get_session
from app.models import Client, Order, User
from app.schemas.orders import OrderUpdate, OrderView
from app.services.orders import dashboard_counts

router = APIRouter(prefix="/api/admin", tags=["admin"])
bearer = HTTPBearer(auto_error=False)
SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def require_admin(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> None:
    expected = get_settings().admin_api_token
    if not credentials or not hmac.compare_digest(credentials.credentials, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized",
                            headers={"WWW-Authenticate": "Bearer"})


AdminDep = Annotated[None, Depends(require_admin)]


@router.get("/dashboard")
async def dashboard(session: SessionDep, _: AdminDep) -> dict[str, int]:
    return await dashboard_counts(session)


@router.get("/orders", response_model=list[OrderView])
async def orders(session: SessionDep, _: AdminDep, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)) -> list[OrderView]:
    rows = (await session.execute(select(Order, User).join(User, Order.user_id == User.id)
                                  .order_by(Order.created_at.desc()).limit(limit).offset(offset))).all()
    return [OrderView(public_id=order.public_id, service=order.service, description=order.description,
                      budget=order.budget, deadline=order.deadline, contact=order.contact,
                      status=order.status, internal_notes=order.internal_notes, assigned_to=order.assigned_to,
                      created_at=order.created_at, client_name=user.first_name, username=user.username,
                      telegram_id=user.telegram_id) for order, user in rows]


@router.patch("/orders/{public_id}", response_model=OrderView)
async def update_order(public_id: str, update: OrderUpdate, session: SessionDep, _: AdminDep) -> OrderView:
    order = await session.scalar(select(Order).where(Order.public_id == public_id))
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    for field in ("status", "internal_notes", "assigned_to"):
        value = getattr(update, field)
        if value is not None:
            setattr(order, field, value)
    await session.commit()
    await session.refresh(order)
    user = await session.get(User, order.user_id)
    return OrderView(public_id=order.public_id, service=order.service, description=order.description,
                     budget=order.budget, deadline=order.deadline, contact=order.contact,
                     status=order.status, internal_notes=order.internal_notes, assigned_to=order.assigned_to,
                     created_at=order.created_at, client_name=user.first_name, username=user.username,
                     telegram_id=user.telegram_id)


@router.get("/clients")
async def clients(session: SessionDep, _: AdminDep, limit: int = Query(100, ge=1, le=500)) -> list[dict[str, object]]:
    rows = (await session.execute(select(Client, User).join(User, Client.user_id == User.id)
                                  .order_by(Client.created_at.desc()).limit(limit))).all()
    return [{"id": client.id, "telegram_id": user.telegram_id, "username": user.username,
             "first_name": user.first_name, "language": user.language, "phone": client.phone,
             "registered_at": user.registered_at} for client, user in rows]
