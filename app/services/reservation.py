from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.game import Game as GameModel
from app.models.operating_hours import OperatingHours
from app.models.reservation import Reservation
from app.models.table import GameTable
from app.schemas.reservation import ReservationCreate


class ReservationService:
	"""ReservationService handles logic and validations for table & game reservations."""

	@staticmethod
	def create_reservation(
		db: Session, user_id: int, reservation_in: ReservationCreate
	) -> Reservation:
		starts_at = reservation_in.starts_at
		ends_at = reservation_in.ends_at

		# 1. Duration check (minimum 30 mins)
		if ends_at < starts_at + timedelta(minutes=30):
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Reservation duration must be at least 30 minutes.",
			)

		# 2. Same-day check
		if starts_at.date() != ends_at.date():
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Reservation must start and end on the same calendar day.",
			)

		# 3. Operating hours check
		day_of_week = starts_at.weekday()  # 0=Monday, ..., 6=Sunday
		hours_stmt = select(OperatingHours).where(
			OperatingHours.day_of_week == day_of_week
		)
		hours = db.scalars(hours_stmt).first()

		if hours:
			if hours.is_closed:
				raise HTTPException(
					status_code=status.HTTP_400_BAD_REQUEST,
					detail="The cafe is closed on this day.",
				)

			open_dt = datetime.combine(starts_at.date(), hours.open_time)
			close_dt = datetime.combine(starts_at.date(), hours.close_time)

			if starts_at < open_dt:
				raise HTTPException(
					status_code=status.HTTP_400_BAD_REQUEST,
					detail="Reservation starts before cafe opening hours.",
				)

			if starts_at + timedelta(minutes=30) > close_dt:
				raise HTTPException(
					status_code=status.HTTP_400_BAD_REQUEST,
					detail="Booking cannot be made when the store is less than 30 minutes from closing.",
				)

			if ends_at > close_dt:
				raise HTTPException(
					status_code=status.HTTP_400_BAD_REQUEST,
					detail="Reservation ends after cafe closing hours.",
				)

		# 4. Table existence check
		table = db.get(GameTable, reservation_in.table_id)
		if not table:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Game table not found.",
			)

		# 5. Table overlap check
		overlap_stmt = select(Reservation).where(
			Reservation.table_id == reservation_in.table_id,
			Reservation.status == "active",
			Reservation.starts_at < ends_at,
			Reservation.ends_at > starts_at,
		)
		overlapping_res = db.scalars(overlap_stmt).first()
		if overlapping_res:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Game table is already reserved for the selected timeframe.",
			)

		# 6. Game existence & stock check
		game = db.get(GameModel, reservation_in.game_id)
		if not game:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Game not found.",
			)

		if game.current_stock <= 0:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Game is currently out of stock for reservation.",
			)

		# Lower game stock by 1
		game.current_stock -= 1

		# Create reservation
		new_reservation = Reservation(
			user_id=user_id,
			game_id=reservation_in.game_id,
			table_id=reservation_in.table_id,
			starts_at=starts_at,
			ends_at=ends_at,
			status="active",
		)
		db.add(new_reservation)
		db.commit()
		db.refresh(new_reservation)
		return new_reservation

	@staticmethod
	def get_reservations(db: Session, user_id: int | None = None) -> list[Reservation]:
		stmt = select(Reservation).order_by(Reservation.starts_at.desc())
		if user_id is not None:
			stmt = stmt.where(Reservation.user_id == user_id)
		return list(db.scalars(stmt).all())

	@staticmethod
	def get_reservation_by_id(db: Session, reservation_id: int) -> Reservation | None:
		return db.get(Reservation, reservation_id)

	@staticmethod
	def cancel_reservation(db: Session, reservation: Reservation) -> Reservation:
		if reservation.status == "cancelled":
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Reservation is already cancelled.",
			)

		reservation.status = "cancelled"

		# Replenish game current stock
		game = db.get(GameModel, reservation.game_id)
		if game and game.current_stock < game.stock:
			game.current_stock += 1

		db.commit()
		db.refresh(reservation)
		return reservation
