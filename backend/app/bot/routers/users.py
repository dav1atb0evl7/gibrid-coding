from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from app.bot.keyboards import HOME_TEXT, back_home_keyboard, choice_keyboard, home_keyboard, portfolio_keyboard, service_keyboard, t
from app.bot.i18n import message as tr
from app.database.session import SessionFactory
from app.models import Message as StoredMessage, Order, PortfolioItem, Service, User
from app.services.catalog import list_portfolio, list_services
from app.services.orders import OrderRequest, create_order

router = Router(name="users")

class OrderForm(StatesGroup):
    service = State()
    description = State()
    budget = State()
    deadline = State()
    contact = State()
    confirmation = State()


async def get_or_create_user(telegram_user) -> User:
    async with SessionFactory() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_user.id))
        if user is None:
            language = telegram_user.language_code if telegram_user.language_code in {"uz", "ru", "en"} else "en"
            user = User(telegram_id=telegram_user.id, username=telegram_user.username,
                        first_name=telegram_user.first_name or "", language=language)
            session.add(user)
        else:
            user.username = telegram_user.username
            user.first_name = telegram_user.first_name or user.first_name
        await session.commit()
        await session.refresh(user)
        return user


async def language_for(telegram_id: int) -> str:
    async with SessionFactory() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        return user.language if user else "en"


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = await get_or_create_user(message.from_user)
    await message.answer(HOME_TEXT.get(user.language, HOME_TEXT["en"]), reply_markup=home_keyboard(user.language))


@router.callback_query(F.data == "menu:home")
async def show_home(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    language = await language_for(callback.from_user.id)
    await callback.message.edit_text(HOME_TEXT.get(language, HOME_TEXT["en"]), reply_markup=home_keyboard(language))
    await callback.answer()


@router.callback_query(F.data == "menu:language")
async def show_languages(callback: CallbackQuery) -> None:
    language = await language_for(callback.from_user.id)
    keyboard = choice_keyboard([("lang:uz", "🇺🇿 O'zbekcha"), ("lang:ru", "🇷🇺 Русский"), ("lang:en", "🇬🇧 English")], language)
    await callback.message.edit_text(tr(language, "language_prompt"), reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("choice:lang:"))
async def set_language(callback: CallbackQuery) -> None:
    selected = callback.data.rsplit(":", 1)[-1]
    async with SessionFactory() as session:
        user = await session.scalar(select(User).where(User.telegram_id == callback.from_user.id))
        if user:
            user.language = selected
            await session.commit()
    await callback.message.edit_text(HOME_TEXT[selected], reply_markup=home_keyboard(selected))
    await callback.answer()


@router.callback_query(F.data == "menu:services")
async def show_services(callback: CallbackQuery) -> None:
    language = await language_for(callback.from_user.id)
    async with SessionFactory() as session:
        services = await list_services(session)
    lines = [f"{tr(language, service.key)[0]}\n{tr(language, service.key)[1]}" for service in services]
    keyboard = choice_keyboard([(f"service:{service.key}", tr(language, service.key)[0]) for service in services], language)
    await callback.message.edit_text((tr(language, "services_intro") + "\n\n" + "\n\n".join(lines)) if lines else tr(language, "service_unavailable"), reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("choice:service:"))
async def show_service(callback: CallbackQuery) -> None:
    key = callback.data.rsplit(":", 1)[-1]
    language = await language_for(callback.from_user.id)
    async with SessionFactory() as session:
        service = await session.scalar(select(Service).where(Service.key == key, Service.is_active.is_(True)))
    if service:
        title, description, _ = tr(language, key)
        await callback.message.edit_text(f"{title}\n\n{description}", reply_markup=service_keyboard(language, key))
    await callback.answer()


@router.callback_query(F.data.startswith("service:details:"))
async def service_details(callback: CallbackQuery) -> None:
    key = callback.data.rsplit(":", 1)[-1]
    language = await language_for(callback.from_user.id)
    async with SessionFactory() as session:
        service = await session.scalar(select(Service).where(Service.key == key))
    if service:
        title, _, details = tr(language, key)
        await callback.message.edit_text(f"{title}\n\n{details}", reply_markup=service_keyboard(language, key))
    await callback.answer()


async def send_portfolio(callback: CallbackQuery, index: int) -> None:
    language = await language_for(callback.from_user.id)
    async with SessionFactory() as session:
        items = await list_portfolio(session)
    if not items:
        await callback.message.edit_text(tr(language, "portfolio_empty"), reply_markup=back_home_keyboard(language))
        return
    index %= len(items)
    item = items[index]
    text = f"📁 {item.name}\n{item.category}\n\n{item.description}\n\n🧰 {item.technologies}\n📍 {item.status}"
    await callback.message.edit_text(text, reply_markup=portfolio_keyboard(language, index, len(items)))


@router.callback_query(F.data == "menu:portfolio")
async def portfolio_start(callback: CallbackQuery) -> None:
    await send_portfolio(callback, 0)
    await callback.answer()


@router.callback_query(F.data.startswith("portfolio:"))
async def portfolio_page(callback: CallbackQuery) -> None:
    await send_portfolio(callback, int(callback.data.rsplit(":", 1)[-1]))
    await callback.answer()


@router.callback_query(F.data == "menu:about")
async def about(callback: CallbackQuery) -> None:
    language = await language_for(callback.from_user.id)
    await callback.message.edit_text(tr(language, "about"), reply_markup=back_home_keyboard(language))
    await callback.answer()


@router.callback_query(F.data == "menu:contact")
async def contact(callback: CallbackQuery) -> None:
    language = await language_for(callback.from_user.id)
    await callback.message.edit_text(tr(language, "contact"), reply_markup=back_home_keyboard(language, "order:start"))
    await callback.answer()


@router.callback_query(F.data.startswith("order:service:"))
async def order_selected_service(callback: CallbackQuery, state: FSMContext) -> None:
    key = callback.data.rsplit(":", 1)[-1]
    language = await language_for(callback.from_user.id)
    async with SessionFactory() as session:
        service = await session.scalar(select(Service).where(Service.key == key))
    await state.clear()
    await state.update_data(service=tr(language, key)[0] if service else "Other")
    await state.set_state(OrderForm.description)
    await callback.message.edit_text(tr(language, "description_prompt"), reply_markup=back_home_keyboard(language))
    await callback.answer()


@router.callback_query(F.data == "order:start")
async def order_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(OrderForm.service)
    language = await language_for(callback.from_user.id)
    options = ["web", "ai", "telegram", "software", "security", "other"]
    await callback.message.edit_text(tr(language, "service_prompt"), reply_markup=choice_keyboard(
        [(f"order-service:{key}", tr(language, "services")[index]) for index, key in enumerate(options)], language))
    await callback.answer()


@router.callback_query(OrderForm.service, F.data.startswith("choice:order-service:"))
async def order_choose_service(callback: CallbackQuery, state: FSMContext) -> None:
    service = callback.data.rsplit(":", 1)[-1]
    language = await language_for(callback.from_user.id)
    keys = ["web", "ai", "telegram", "software", "security"]
    label = tr(language, keys[keys.index(service)])[0] if service in keys else tr(language, "services")[5]
    await state.update_data(service=label)
    await state.set_state(OrderForm.description)
    await callback.message.edit_text(tr(language, "description_prompt"), reply_markup=back_home_keyboard(language))
    await callback.answer()


@router.message(OrderForm.description)
async def order_description(message: Message, state: FSMContext) -> None:
    language = await language_for(message.from_user.id)
    value = (message.text or "").strip()
    if not value or len(value) > 4000:
        await message.answer(tr(language, "description_invalid"))
        return
    await state.update_data(description=value)
    await state.set_state(OrderForm.budget)
    labels = tr(language, "budgets")
    values = ["$50–$100", "$100–$300", "$300–$500", "$500+", "Unknown"]
    await message.answer(tr(language, "budget_prompt"), reply_markup=choice_keyboard(list(zip(values, labels)), language))


@router.callback_query(OrderForm.budget, F.data.startswith("choice:"))
async def order_budget(callback: CallbackQuery, state: FSMContext) -> None:
    language = await language_for(callback.from_user.id)
    await state.update_data(budget=callback.data.removeprefix("choice:"))
    await state.set_state(OrderForm.deadline)
    values = ["1 week", "2 weeks", "1 month", "Flexible"]
    await callback.message.edit_text(tr(language, "deadline_prompt"), reply_markup=choice_keyboard(list(zip(values, tr(language, "deadlines"))), language))
    await callback.answer()


@router.callback_query(OrderForm.deadline, F.data.startswith("choice:"))
async def order_deadline(callback: CallbackQuery, state: FSMContext) -> None:
    language = await language_for(callback.from_user.id)
    await state.update_data(deadline=callback.data.removeprefix("choice:"))
    await state.set_state(OrderForm.contact)
    await callback.message.edit_text(tr(language, "contact_prompt"), reply_markup=back_home_keyboard(language))
    await callback.answer()


@router.message(OrderForm.contact)
async def order_contact(message: Message, state: FSMContext, bot) -> None:
    language = await language_for(message.from_user.id)
    contact = message.contact.phone_number if message.contact else (message.text or "").strip()
    if not contact or len(contact) > 255:
        await message.answer(tr(language, "contact_invalid"))
        return
    await state.update_data(contact=contact)
    await state.set_state(OrderForm.confirmation)
    data = await state.get_data()
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    summary = (f"{tr(language, 'summary_title')}\n\n{tr(language, 'service_label')}: {data['service']}\n{tr(language, 'description_label')}: {data['description']}\n"
               f"{tr(language, 'budget_label')}: {data['budget']}\n{tr(language, 'deadline_label')}: {data['deadline']}\n{tr(language, 'client_label')}: {username}\n{tr(language, 'contact_label')}: {contact}")
    buttons = [[("confirm", t(language, "confirm")), ("edit", t(language, "edit"))], [("cancel", t(language, "cancel"))]]
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=f"order:{key}") for key, label in row] for row in buttons])
    await message.answer(summary, reply_markup=keyboard)


@router.callback_query(OrderForm.confirmation, F.data == "order:confirm")
async def order_confirm(callback: CallbackQuery, state: FSMContext, bot) -> None:
    data = await state.get_data()
    try:
        async with SessionFactory() as session:
            user = await session.scalar(select(User).where(User.telegram_id == callback.from_user.id))
            if user is None:
                raise ValueError("User is not registered")
            order = await create_order(session, user, OrderRequest(**{key: data[key] for key in ("service", "description", "budget", "deadline", "contact")}))
            session.add(StoredMessage(user_id=user.id, direction="inbound", body=data["description"]))
            await session.commit()
            username = f"@{user.username}" if user.username else user.first_name
            from app.bot.routers.admins import notify_admins
            await notify_admins(bot, order, username)
        await state.clear()
        language = await language_for(callback.from_user.id)
        await callback.message.edit_text(tr(language, "confirmed").format(order_id=order.public_id), reply_markup=home_keyboard(language))
    except Exception:
        await callback.message.edit_text(tr(await language_for(callback.from_user.id), "error"), reply_markup=home_keyboard())
        raise
    finally:
        await callback.answer()


@router.callback_query(F.data == "order:edit")
async def order_edit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await order_start(callback, state)


@router.callback_query(F.data == "order:cancel")
async def order_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await show_home(callback, state)
