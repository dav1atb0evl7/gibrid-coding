from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import select

from app.bot.keyboards import TEXT
from app.config.settings import get_settings
from app.database.session import SessionFactory
from app.models import Notification, Order, OrderStatus, User
from app.services.orders import dashboard_counts

router = Router(name="admins")

def is_admin(telegram_id: int) -> bool:
    return telegram_id in get_settings().admin_ids


async def notify_admins(bot, order: Order, username: str) -> None:
    settings = get_settings()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Client", url=f"tg://user?id={order.user.telegram_id}"),
         InlineKeyboardButton(text="📋 Order", callback_data=f"admin:order:{order.public_id}")],
        [InlineKeyboardButton(text="✅ Accept", callback_data=f"admin:status:{order.public_id}:CONTACTED"),
         InlineKeyboardButton(text="❌ Reject", callback_data=f"admin:status:{order.public_id}:CANCELLED")],
    ])
    text = (f"🔔 NEW PROJECT REQUEST\n\nOrder: {order.public_id}\nClient: {username}\n"
            f"Service: {order.service}\nBudget: {order.budget}\nDeadline: {order.deadline}")
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(admin_id, text, reply_markup=keyboard)
            async with SessionFactory() as session:
                session.add(Notification(order_id=order.id, recipient_id=admin_id, kind="new_order", sent_at=datetime.now(timezone.utc)))
                await session.commit()
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Could not deliver order notification to admin %s", admin_id)


@router.message(Command("admin"))
async def admin_menu(message: Message) -> None:
    if not is_admin(message.from_user.id):
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Dashboard", callback_data="admin:dashboard"), InlineKeyboardButton(text="📩 Orders", callback_data="admin:orders")],
        [InlineKeyboardButton(text="👥 Clients", callback_data="admin:clients"), InlineKeyboardButton(text="📁 Portfolio", callback_data="admin:portfolio")],
        [InlineKeyboardButton(text="💻 Services", callback_data="admin:services"), InlineKeyboardButton(text="⚙️ Settings", callback_data="admin:settings")],
    ])
    await message.answer("GIBRID X CODING · Admin", reply_markup=keyboard)


@router.callback_query(F.data.startswith("admin:"))
async def admin_actions(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized", show_alert=True)
        return
    parts = callback.data.split(":")
    async with SessionFactory() as session:
        if parts[1] == "dashboard":
            counts = await dashboard_counts(session)
            text = (f"📊 Dashboard\nUsers: {counts['total_users']}\nClients: {counts['total_clients']}\n"
                    f"New orders: {counts['new_orders']}\nActive projects: {counts['active_projects']}\n"
                    f"Completed: {counts['completed_projects']}\nCancelled: {counts['cancelled_orders']}")
            await callback.message.edit_text(text)
        elif parts[1] == "orders":
            orders = list((await session.scalars(select(Order).order_by(Order.created_at.desc()).limit(20))).all())
            text = "📩 Recent orders\n\n" + ("\n".join(f"{o.public_id} · {o.status.value} · {o.service}" for o in orders) or "No orders yet.")
            await callback.message.edit_text(text)
        elif parts[1] == "order" and len(parts) == 3:
            order = await session.scalar(select(Order).where(Order.public_id == parts[2]))
            if order:
                user = await session.get(User, order.user_id)
                text = f"{order.public_id} · {order.status.value}\n{order.service}\n{order.description}\n{order.budget} · {order.deadline}\nClient: {user.username or user.first_name}\nContact: {order.contact}"
                await callback.message.answer(text)
        elif parts[1] == "status" and len(parts) == 4 and parts[3] in OrderStatus.__members__:
            order = await session.scalar(select(Order).where(Order.public_id == parts[2]))
            if order:
                order.status = OrderStatus[parts[3]]
                await session.commit()
                await callback.answer(f"{order.public_id}: {order.status.value}", show_alert=True)
        elif parts[1] == "clients":
            total = await session.scalar(select(User.id).where(User.client.has()).limit(100))
            await callback.message.answer(f"👥 Client records are available in the admin dashboard. Latest client record: {'available' if total else 'none'}")
        else:
            await callback.message.answer("This admin workspace is available in the web dashboard.")
    await callback.answer()
