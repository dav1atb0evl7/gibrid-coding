from dataclasses import dataclass
import re
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Client, Order, OrderStatus, User


@dataclass(frozen=True)
class OrderRequest:
    service: str
    description: str
    budget: str
    deadline: str
    contact: str


def validate_order_request(request: OrderRequest) -> None:
    limits = ((request.service, 100), (request.description, 4000), (request.budget, 64),
              (request.deadline, 64), (request.contact, 255))
    if any(not value.strip() or len(value) > limit for value, limit in limits):
        raise ValueError("Order fields must be non-empty and within their length limits")


async def create_order(session: AsyncSession, user: User, request: OrderRequest) -> Order:
    validate_order_request(request)
    order = Order(user=user, public_id=f"ALLOCATING-{uuid4().hex}", service=request.service.strip(),
                  description=request.description.strip(), budget=request.budget.strip(),
                  deadline=request.deadline.strip(), contact=request.contact.strip())
    session.add(order)
    await session.flush()
    order.public_id = f"GXC-{order.id:06d}"
    client = await session.scalar(select(Client).where(Client.user_id == user.id))
    if client is None:
        phone = request.contact if re.fullmatch(r"\+?[0-9][0-9 ()-]{5,30}", request.contact) else None
        session.add(Client(user_id=user.id, phone=phone))
    elif re.fullmatch(r"\+?[0-9][0-9 ()-]{5,30}", request.contact):
        client.phone = request.contact
    await session.commit()
    await session.refresh(order)
    return order


async def dashboard_counts(session: AsyncSession) -> dict[str, int]:
    total_users = await session.scalar(select(func.count(User.id))) or 0
    total_clients = await session.scalar(select(func.count(Client.id))) or 0
    counts = {"total_users": total_users, "total_clients": total_clients}
    for status in OrderStatus:
        count = await session.scalar(select(func.count(Order.id)).where(Order.status == status)) or 0
        counts[f"{status.value.lower()}_orders"] = count
    counts["active_projects"] = counts["in_progress_orders"]
    counts["completed_projects"] = counts["completed_orders"]
    return counts
