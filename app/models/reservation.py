from datetime import datetime

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column

from app.db.database import table_registry


@mapped_as_dataclass(table_registry)
class Reservation:
	"""
	Represents a game table and game reservation entity:
	- id: Primary key identifier.
	- user_id: Foreign key referencing the user.
	- game_id: Foreign key referencing the reserved game.
	- table_id: Foreign key referencing the reserved table.
	- starts_at: Datetime when reservation begins.
	- ends_at: Datetime when reservation ends.
	- status: Status of reservation ('active', 'cancelled', 'completed').
	"""

	__tablename__ = "reservations"

	id: Mapped[int] = mapped_column(
		init=False, primary_key=True, autoincrement=True, unique=True
	)
	user_id: Mapped[int] = mapped_column(
		ForeignKey("users.id", ondelete="CASCADE"), nullable=False
	)
	game_id: Mapped[int] = mapped_column(
		ForeignKey("games.id", ondelete="CASCADE"), nullable=False
	)
	table_id: Mapped[int] = mapped_column(
		ForeignKey("game_tables.id", ondelete="CASCADE"), nullable=False
	)
	starts_at: Mapped[datetime] = mapped_column(nullable=False)
	ends_at: Mapped[datetime] = mapped_column(nullable=False)
	status: Mapped[str] = mapped_column(
		String(20), default="active", server_default=text("'active'"), nullable=False
	)
