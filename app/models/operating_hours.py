from datetime import time

from sqlalchemy import Time, text
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column

from app.db.database import table_registry


@mapped_as_dataclass(table_registry)
class OperatingHours:
	"""
	Represents store operating hours for a day of the week:
	- id: Unique identifier.
	- day_of_week: Day of week (0=Monday, 1=Tuesday, ..., 6=Sunday).
	- open_time: Store opening time.
	- close_time: Store closing time.
	- is_closed: True if store is closed all day.
	"""

	__tablename__ = "operating_hours"

	id: Mapped[int] = mapped_column(
		init=False, primary_key=True, autoincrement=True, unique=True
	)
	day_of_week: Mapped[int] = mapped_column(unique=True, nullable=False)
	open_time: Mapped[time] = mapped_column(Time, nullable=False)
	close_time: Mapped[time] = mapped_column(Time, nullable=False)
	is_closed: Mapped[bool] = mapped_column(
		default=False, server_default=text("false"), nullable=False
	)
