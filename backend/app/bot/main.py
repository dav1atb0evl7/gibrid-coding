from aiogram import Bot, Dispatcher

from app.bot.middleware import UserRateLimitMiddleware
from app.bot.routers.admins import router as admins_router
from app.bot.routers.users import router as users_router


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.message.middleware(UserRateLimitMiddleware())
    dispatcher.callback_query.middleware(UserRateLimitMiddleware())
    dispatcher.include_router(admins_router)
    dispatcher.include_router(users_router)
    return dispatcher


def create_bot(token: str) -> Bot:
    return Bot(token=token)
