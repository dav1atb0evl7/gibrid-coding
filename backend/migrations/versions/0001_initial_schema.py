"""Initial GIBRID X CODING schema."""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

order_status = sa.Enum("NEW", "CONTACTED", "NEGOTIATION", "IN_PROGRESS", "COMPLETED", "CANCELLED", name="order_status")


def upgrade() -> None:
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(64)), sa.Column("first_name", sa.String(128), nullable=False),
        sa.Column("language", sa.String(2), nullable=False), sa.Column("registered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("telegram_id"))
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])
    op.create_table("admins", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False), sa.Column("display_name", sa.String(128)),
        sa.Column("is_active", sa.Boolean(), nullable=False), sa.UniqueConstraint("telegram_id"))
    op.create_index("ix_admins_telegram_id", "admins", ["telegram_id"])
    op.create_table("clients", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("phone", sa.String(32)), sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("user_id"))
    op.create_table("services", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("key", sa.String(64), nullable=False),
        sa.Column("title", sa.String(160), nullable=False), sa.Column("description", sa.Text(), nullable=False),
        sa.Column("details", sa.Text(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.UniqueConstraint("key"))
    op.create_table("portfolio", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(160), nullable=False),
        sa.Column("category", sa.String(100), nullable=False), sa.Column("description", sa.Text(), nullable=False),
        sa.Column("technologies", sa.String(255), nullable=False), sa.Column("status", sa.String(64), nullable=False), sa.Column("image_url", sa.String(500)))
    op.create_table("orders", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("public_id", sa.String(24), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("service", sa.String(100), nullable=False), sa.Column("description", sa.Text(), nullable=False),
        sa.Column("budget", sa.String(64), nullable=False), sa.Column("deadline", sa.String(64), nullable=False),
        sa.Column("contact", sa.String(255), nullable=False), sa.Column("status", order_status, nullable=False),
        sa.Column("internal_notes", sa.Text()), sa.Column("assigned_to", sa.String(128)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("public_id"))
    op.create_index("ix_orders_public_id", "orders", ["public_id"])
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_table("messages", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("direction", sa.String(16), nullable=False), sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("notifications", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="SET NULL")),
        sa.Column("recipient_id", sa.BigInteger(), nullable=False), sa.Column("kind", sa.String(64), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("messages")
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_index("ix_orders_public_id", table_name="orders")
    op.drop_table("orders")
    op.drop_table("portfolio")
    op.drop_table("services")
    op.drop_table("clients")
    op.drop_index("ix_admins_telegram_id", table_name="admins")
    op.drop_table("admins")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
    order_status.drop(op.get_bind(), checkfirst=True)
