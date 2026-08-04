from datetime import datetime

from sqlalchemy import Float, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column, relationship

from app.db.database import table_registry
from app.models.menu import MenuItem
from app.models.table import GameTable
from app.models.user import User


@mapped_as_dataclass(table_registry)
class OrderItem:
	"""
	Represents an individual line item inside a cafe order.
	- id: Unique identifier.
	- order_id: Foreign key referencing the parent order.
	- menu_item_id: Foreign key referencing the menu item ordered.
	- quantity: Quantity of item ordered.
	- unit_price: Historical price per item at time of ordering.
	- menu_item: Relationship to MenuItem entity.
	"""

	__tablename__ = "order_items"

	id: Mapped[int] = mapped_column(
		init=False, primary_key=True, autoincrement=True, unique=True
	)
	order_id: Mapped[int] = mapped_column(
		ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, init=False
	)
	menu_item_id: Mapped[int] = mapped_column(
		ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False
	)
	unit_price: Mapped[float] = mapped_column(Float, nullable=False)
	quantity: Mapped[int] = mapped_column(default=1, nullable=False)

	menu_item: Mapped[MenuItem] = relationship(init=False, lazy="selectin")


@mapped_as_dataclass(table_registry)
class Order:
	"""
	Represents a cafe order placed at a game table.
	- id: Primary key identifier.
	- table_number: Foreign key referencing the game table number.
	- user_id: Foreign key referencing the placing user (optional).
	- notes: Special instructions or customization notes.
	- status: Order lifecycle status ('pending', 'preparing', 'ready', 'served', 'cancelled').
	- created_at: Timestamp when order was placed.
	- items: Relationship to associated OrderItem entities.
	- table: Relationship to GameTable entity.
	- user: Relationship to User entity.
	"""

	__tablename__ = "orders"

	id: Mapped[int] = mapped_column(
		init=False, primary_key=True, autoincrement=True, unique=True
	)
	table_number: Mapped[int] = mapped_column(
		ForeignKey("game_tables.number", ondelete="CASCADE"), nullable=False
	)
	user_id: Mapped[int | None] = mapped_column(
		ForeignKey("users.id", ondelete="SET NULL"), nullable=True, default=None
	)
	notes: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
	status: Mapped[str] = mapped_column(
		String(20), default="pending", server_default=text("'pending'"), nullable=False
	)
	created_at: Mapped[datetime] = mapped_column(
		default_factory=datetime.now, nullable=False
	)
	items: Mapped[list[OrderItem]] = relationship(
		default_factory=list, lazy="selectin", cascade="all, delete-orphan"
	)
	table: Mapped[GameTable] = relationship(
		init=False,
		lazy="selectin",
		primaryjoin="Order.table_number == GameTable.number",
		foreign_keys="[Order.table_number]",
	)
	user: Mapped[User | None] = relationship(init=False, lazy="selectin")
