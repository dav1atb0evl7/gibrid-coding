import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.admin.routes import router as admin_router
from app.bot.main import create_bot, create_dispatcher
from app.config.settings import get_settings
from app.database.session import engine

settings = get_settings()
logging.basicConfig(level=settings.log_level.upper(), format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("gxc")
bot = create_bot(settings.bot_token)
dispatcher = create_dispatcher()
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.bot_task = None
    if settings.bot_mode == "polling":
        app.state.bot_task = asyncio.create_task(dispatcher.start_polling(bot, handle_signals=False))
    elif settings.webhook_base_url:
        await bot.set_webhook(f"{settings.webhook_base_url.rstrip('/')}/telegram/webhook",
                              secret_token=settings.webhook_secret, drop_pending_updates=False)
    yield
    if app.state.bot_task:
        await dispatcher.stop_polling()
        await app.state.bot_task
    await bot.session.close()
    await engine.dispose()


app = FastAPI(title="GIBRID X CODING API", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=False,
                   allow_methods=["GET", "PATCH", "POST", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])
app.include_router(admin_router)


@app.get("/health")
@limiter.limit("30/minute")
async def health(request: Request) -> dict[str, str]:
    return {"status": "ok"}


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request) -> JSONResponse:
    if settings.bot_mode != "webhook" or not settings.webhook_secret:
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != settings.webhook_secret:
        return JSONResponse(status_code=403, content={"detail": "Forbidden"})
    from aiogram.types import Update
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dispatcher.feed_update(bot, update)
    return JSONResponse(content={"ok": True})


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled request error on %s", request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
