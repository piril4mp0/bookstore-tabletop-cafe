from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column

from app.db.database import table_registry


@mapped_as_dataclass(table_registry)
class GameTable:
	"""
	Represents a game table entity with:
	- id: Unique identifier for the table.
	- number: Number placed on top of physical table.
	- chairs: Number of chairs available at the table.
	- size: Size of the table ('small', 'medium', 'large').
	"""

	__tablename__ = "game_tables"

	id: Mapped[int] = mapped_column(
		init=False, primary_key=True, autoincrement=True, unique=True
	)
	number: Mapped[int] = mapped_column(unique=True, nullable=False)
	chairs: Mapped[int] = mapped_column(nullable=False)
	size: Mapped[str] = mapped_column(String(20), nullable=False)
