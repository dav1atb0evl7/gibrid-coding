from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PortfolioItem, Service

SERVICE_CATALOG = [
    ("web", "💻 Web Development", "Landing pages, corporate websites, e-commerce and web applications.", "We design and build fast, accessible digital products, from conversion-focused landing pages to custom web applications."),
    ("ai", "🤖 AI Solutions", "AI chatbots, assistants, automation and custom AI systems.", "We integrate practical AI into your workflows, with human handoff for complex or sensitive questions."),
    ("telegram", "📱 Telegram Bots", "Business, support, ordering and CRM-integrated bots.", "We create reliable Telegram experiences that connect customers, operations and your existing systems."),
    ("software", "⚙️ Software Development", "CRM systems, management tools and business automation.", "Purpose-built software to simplify operations and give your team better visibility and control."),
    ("security", "🔐 Cybersecurity", "Security consultation, assessment and tailored solutions.", "Practical security reviews and improvements that help protect your applications, systems and data."),
]


async def seed_catalog(session: AsyncSession) -> None:
    existing = set((await session.scalars(select(Service.key))).all())
    for key, title, description, details in SERVICE_CATALOG:
        if key not in existing:
            session.add(Service(key=key, title=title, description=description, details=details))
    await session.commit()


async def list_services(session: AsyncSession) -> list[Service]:
    return list((await session.scalars(select(Service).where(Service.is_active.is_(True)).order_by(Service.id))).all())


async def list_portfolio(session: AsyncSession) -> list[PortfolioItem]:
    return list((await session.scalars(select(PortfolioItem).order_by(PortfolioItem.id))).all())
