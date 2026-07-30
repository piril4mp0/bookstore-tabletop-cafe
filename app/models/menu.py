from sqlalchemy import Column, Float, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column, relationship

from app.db.database import table_registry
from app.models.tag import Tag

menu_item_tags = Table(
	"menu_item_tags",
	table_registry.metadata,
	Column(
		"menu_item_id",
		ForeignKey("menu_items.id", ondelete="CASCADE"),
		primary_key=True,
	),
	Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


@mapped_as_dataclass(table_registry)
class MenuItem:
	"""
	Represents a menu item entity (drink or meal).
	- id: Unique identifier.
	- name: Name of the menu item.
	- category: Category ('drink' or 'meal').
	- description: Description of the item.
	- price: Price of the item.
	- stock: Inventory stock quantity.
	- is_available: Availability status for customers.
	- tags: Associated Tag objects via many-to-many relationship.
	"""

	__tablename__ = "menu_items"

	id: Mapped[int] = mapped_column(
		init=False, primary_key=True, autoincrement=True, unique=True
	)
	name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
	category: Mapped[str] = mapped_column(String(50), nullable=False)
	price: Mapped[float] = mapped_column(Float, nullable=False)
	description: Mapped[str | None] = mapped_column(
		String(500), nullable=True, default=None
	)
	stock: Mapped[int] = mapped_column(default=0, nullable=False)

	is_available: Mapped[bool] = mapped_column(default=True, nullable=False)
	tags: Mapped[list[Tag]] = relationship(
		secondary=menu_item_tags, default_factory=list, lazy="selectin"
	)
