from datetime import time

from pydantic import BaseModel, Field


class OperatingHoursBase(BaseModel):
	day_of_week: int = Field(
		...,
		ge=0,
		le=6,
		description="Day of week (0=Monday, 1=Tuesday, ..., 6=Sunday)",
		example=0,
	)
	open_time: time = Field(
		..., description="Store opening time (HH:MM:SS)", example="08:00:00"
	)
	close_time: time = Field(
		..., description="Store closing time (HH:MM:SS)", example="22:00:00"
	)
	is_closed: bool = Field(
		False, description="True if store is closed all day", example=False
	)


class OperatingHoursUpdate(BaseModel):
	open_time: time | None = Field(
		None, description="Store opening time (HH:MM:SS)", example="08:00:00"
	)
	close_time: time | None = Field(
		None, description="Store closing time (HH:MM:SS)", example="22:00:00"
	)
	is_closed: bool | None = Field(
		None, description="True if store is closed all day", example=False
	)


class OperatingHoursResponse(OperatingHoursBase):
	id: int = Field(..., description="Unique identifier", example=1)
