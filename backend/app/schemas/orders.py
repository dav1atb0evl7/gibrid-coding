from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import OrderStatus


class OrderUpdate(BaseModel):
    status: OrderStatus | None = None
    internal_notes: str | None = Field(default=None, max_length=4000)
    assigned_to: str | None = Field(default=None, max_length=128)


class OrderView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: str
    service: str
    description: str
    budget: str
    deadline: str
    contact: str
    status: OrderStatus
    internal_notes: str | None
    assigned_to: str | None
    created_at: datetime
    client_name: str
    username: str | None
    telegram_id: int
