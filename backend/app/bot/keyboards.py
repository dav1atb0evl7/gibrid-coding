from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


TEXT = {
    "en": {"services": "💻 Services", "portfolio": "📁 Portfolio", "order": "🚀 Order a Project",
           "about": "🏢 About Us", "contact": "💬 Contact", "language": "🌐 Language",
           "home": "🏠 Home", "back": "⬅️ Back", "details": "📋 Details", "order_this": "🚀 Order This Service",
           "similar": "🚀 Order Similar Project", "previous": "⬅️ Previous", "next": "Next ➡️",
           "contact_us": "💬 Contact Us", "cancel": "❌ Cancel", "confirm": "✅ Confirm Order",
           "edit": "✏️ Edit", "dashboard": "📊 Dashboard", "orders": "📩 Orders",
           "clients": "👥 Clients", "portfolio_admin": "📁 Portfolio", "services_admin": "💻 Services",
           "broadcast": "📢 Broadcast", "settings": "⚙️ Settings"},
    "ru": {"services": "💻 Услуги", "portfolio": "📁 Портфолио", "order": "🚀 Заказать проект",
           "about": "🏢 О компании", "contact": "💬 Контакты", "language": "🌐 Язык",
           "home": "🏠 Главная", "back": "⬅️ Назад", "details": "📋 Подробнее", "order_this": "🚀 Заказать услугу",
           "similar": "🚀 Заказать похожий проект", "previous": "⬅️ Назад", "next": "Вперёд ➡️",
           "contact_us": "💬 Связаться", "cancel": "❌ Отмена", "confirm": "✅ Подтвердить",
           "edit": "✏️ Изменить", "dashboard": "📊 Сводка", "orders": "📩 Заявки",
           "clients": "👥 Клиенты", "portfolio_admin": "📁 Портфолио", "services_admin": "💻 Услуги",
           "broadcast": "📢 Рассылка", "settings": "⚙️ Настройки"},
    "uz": {"services": "💻 Xizmatlar", "portfolio": "📁 Portfolio", "order": "🚀 Loyiha buyurtma qilish",
           "about": "🏢 Biz haqimizda", "contact": "💬 Aloqa", "language": "🌐 Til",
           "home": "🏠 Bosh sahifa", "back": "⬅️ Orqaga", "details": "📋 Batafsil", "order_this": "🚀 Xizmatga buyurtma",
           "similar": "🚀 O'xshash loyiha buyurtma qilish", "previous": "⬅️ Oldingi", "next": "Keyingi ➡️",
           "contact_us": "💬 Bog'lanish", "cancel": "❌ Bekor qilish", "confirm": "✅ Tasdiqlash",
           "edit": "✏️ Tahrirlash", "dashboard": "📊 Hisobot", "orders": "📩 Buyurtmalar",
           "clients": "👥 Mijozlar", "portfolio_admin": "📁 Portfolio", "services_admin": "💻 Xizmatlar",
           "broadcast": "📢 Xabar yuborish", "settings": "⚙️ Sozlamalar"},
}

HOME_TEXT = {
    "en": "👋 Welcome to GIBRID X CODING\n\nWe build modern digital solutions using AI, software and web technologies.\n\n💻 Web Development\n🤖 AI Solutions\n📱 Telegram Bots\n⚙️ Software & Automation\n🔐 Cybersecurity\n\nTurn your idea into a real digital product.",
    "ru": "👋 Добро пожаловать в GIBRID X CODING\n\nМы создаём современные цифровые решения с помощью ИИ, программного обеспечения и веб-технологий.\n\n💻 Веб-разработка\n🤖 Решения на основе ИИ\n📱 Telegram-боты\n⚙️ ПО и автоматизация\n🔐 Кибербезопасность\n\nПревратим вашу идею в цифровой продукт.",
    "uz": "👋 GIBRID X CODING'ga xush kelibsiz\n\nBiz AI, dasturiy ta'minot va veb-texnologiyalar asosida zamonaviy raqamli yechimlar yaratamiz.\n\n💻 Veb-ishlab chiqish\n🤖 AI yechimlari\n📱 Telegram botlar\n⚙️ Dasturiy ta'minot va avtomatlashtirish\n🔐 Kiberxavfsizlik\n\nG'oyangizni haqiqiy raqamli mahsulotga aylantiring.",
}

def t(language: str, key: str) -> str:
    return TEXT.get(language, TEXT["en"]).get(key, TEXT["en"].get(key, key))


def home_keyboard(language: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(language, "services"), callback_data="menu:services"),
         InlineKeyboardButton(text=t(language, "portfolio"), callback_data="menu:portfolio")],
        [InlineKeyboardButton(text=t(language, "order"), callback_data="order:start")],
        [InlineKeyboardButton(text=t(language, "about"), callback_data="menu:about"),
         InlineKeyboardButton(text=t(language, "contact_us"), callback_data="menu:contact")],
        [InlineKeyboardButton(text=t(language, "language"), callback_data="menu:language")],
    ])


def back_home_keyboard(language: str = "en", back: str = "menu:home") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(language, "back"), callback_data=back),
         InlineKeyboardButton(text=t(language, "home"), callback_data="menu:home")],
    ])


def service_keyboard(language: str, key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(language, "details"), callback_data=f"service:details:{key}")],
        [InlineKeyboardButton(text=t(language, "order_this"), callback_data=f"order:service:{key}")],
        [InlineKeyboardButton(text=t(language, "back"), callback_data="menu:services"),
         InlineKeyboardButton(text=t(language, "home"), callback_data="menu:home")],
    ])


def portfolio_keyboard(language: str, index: int, total: int) -> InlineKeyboardMarkup:
    navigation = []
    if total > 1:
        navigation = [[InlineKeyboardButton(text=t(language, "previous"), callback_data=f"portfolio:{(index - 1) % total}"),
                       InlineKeyboardButton(text=t(language, "next"), callback_data=f"portfolio:{(index + 1) % total}")]]
    return InlineKeyboardMarkup(inline_keyboard=navigation + [
        [InlineKeyboardButton(text=t(language, "similar"), callback_data="order:start")],
        [InlineKeyboardButton(text=t(language, "back"), callback_data="menu:home"),
         InlineKeyboardButton(text=t(language, "home"), callback_data="menu:home")],
    ])


def choice_keyboard(values: list[tuple[str, str]], language: str = "en") -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=label, callback_data=f"choice:{value}")] for value, label in values]
    rows.append([InlineKeyboardButton(text=t(language, "cancel"), callback_data="order:cancel"),
                 InlineKeyboardButton(text=t(language, "home"), callback_data="menu:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
