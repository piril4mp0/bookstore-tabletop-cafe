from datetime import datetime

from pydantic import BaseModel, Field


class ReservationCreate(BaseModel):
	game_id: int = Field(..., description="ID of the game to reserve", example=1)
	table_id: int = Field(..., description="ID of the table to reserve", example=1)
	starts_at: datetime = Field(
		...,
		description="Start timestamp of reservation",
		example="2026-08-01T14:00:00",
	)
	ends_at: datetime = Field(
		...,
		description="End timestamp of reservation",
		example="2026-08-01T16:00:00",
	)


class ReservationResponse(BaseModel):
	id: int = Field(..., description="Reservation ID", example=1)
	user_id: int = Field(..., description="ID of reserving user", example=1)
	game_id: int = Field(..., description="ID of reserved game", example=1)
	table_id: int = Field(..., description="ID of reserved table", example=1)
	starts_at: datetime = Field(..., description="Start timestamp of reservation")
	ends_at: datetime = Field(..., description="End timestamp of reservation")
	status: str = Field(..., description="Status of reservation", example="active")
