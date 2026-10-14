from time import monotonic
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class UserRateLimitMiddleware(BaseMiddleware):
    def __init__(self, interval_seconds: float = 0.7) -> None:
        self.interval_seconds = interval_seconds
        self.last_seen: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is not None:
            now = monotonic()
            previous = self.last_seen.get(user.id, 0)
            if now - previous < self.interval_seconds:
                return None
            self.last_seen[user.id] = now
        return await handler(event, data)
