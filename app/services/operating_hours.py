from datetime import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.operating_hours import OperatingHours
from app.schemas.operating_hours import OperatingHoursUpdate


class OperatingHoursService:
	"""OperatingHoursService handles store operating hours logic."""

	@staticmethod
	def get_operating_hours(db: Session) -> list[OperatingHours]:
		stmt = select(OperatingHours).order_by(OperatingHours.day_of_week)
		return list(db.scalars(stmt).all())

	@staticmethod
	def get_operating_hours_by_day(
		db: Session, day_of_week: int
	) -> OperatingHours | None:
		stmt = select(OperatingHours).where(OperatingHours.day_of_week == day_of_week)
		return db.scalars(stmt).first()

	@staticmethod
	def upsert_operating_hours(
		db: Session, day_of_week: int, hours_update: OperatingHoursUpdate
	) -> OperatingHours:
		hours = OperatingHoursService.get_operating_hours_by_day(db, day_of_week)
		update_data = hours_update.model_dump(exclude_unset=True)

		if not hours:
			# Default open/close if creating new
			open_t = update_data.get("open_time", time(8, 0, 0))
			close_t = update_data.get("close_time", time(22, 0, 0))
			is_closed_val = update_data.get("is_closed", False)
			hours = OperatingHours(
				day_of_week=day_of_week,
				open_time=open_t,
				close_time=close_t,
				is_closed=is_closed_val,
			)
			db.add(hours)
		else:
			for key, value in update_data.items():
				setattr(hours, key, value)

		db.commit()
		db.refresh(hours)
		return hours
