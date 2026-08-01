from datetime import datetime

from sqlalchemy import JSON, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column

from app.db.database import table_registry


@mapped_as_dataclass(table_registry)
class Game:
	"""
	Represents a game entity with the following fields:
	- id: Unique identifier for the game.
	- title: Title of the game (must be unique and not null).
	- genre: List of genres associated with the game.
	- description: Description of the game.
	- release_date: Release date of the game.
	- players: Number of players supported by the game.
	"""

	__tablename__ = "games"
	id: Mapped[int] = mapped_column(
		init=False, primary_key=True, autoincrement=True, unique=True
	)
	title: Mapped[str] = mapped_column(unique=True, nullable=False)
	genre: Mapped[list[str]] = mapped_column(
		postgresql.ARRAY(String).with_variant(JSON, "sqlite"), nullable=False
	)
	description: Mapped[str] = mapped_column(nullable=False)
	release_date: Mapped[datetime] = mapped_column(nullable=False)
	players: Mapped[int] = mapped_column(nullable=False)
	stock: Mapped[int] = mapped_column(default=1, nullable=False)
	current_stock: Mapped[int] = mapped_column(default=1, nullable=False)
