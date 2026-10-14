from app.bot.i18n import message
from app.bot.keyboards import HOME_TEXT
from app.bot.routers.admins import is_admin
from app.models import OrderStatus


def test_home_copy_exists_in_supported_languages() -> None:
    assert set(HOME_TEXT) == {"en", "ru", "uz"}
    assert "GIBRID X CODING" in HOME_TEXT["en"]


def test_catalog_has_localized_service_details() -> None:
    for language in ("en", "ru", "uz"):
        title, summary, details = message(language, "ai")
        assert title and summary and details


def test_admin_authorization_uses_telegram_ids(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "test-token")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
    monkeypatch.setenv("ADMIN_API_TOKEN", "test-secret")
    monkeypatch.setenv("ADMIN_TELEGRAM_IDS", "12345,67890")
    from app.config.settings import get_settings
    get_settings.cache_clear()
    try:
        assert is_admin(12345)
        assert not is_admin(99999)
    finally:
        get_settings.cache_clear()


def test_orders_have_declared_lifecycle() -> None:
    assert len(OrderStatus) == 6
