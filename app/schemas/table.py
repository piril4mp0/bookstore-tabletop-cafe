from typing import Literal

from pydantic import BaseModel, Field


class TableBase(BaseModel):
	number: int = Field(
		..., gt=0, description="Number on top of physical table", example=1
	)
	chairs: int = Field(..., gt=0, description="Number of chairs available", example=4)
	size: Literal["small", "medium", "large"] = Field(
		..., description="Size of table", example="medium"
	)


class TableCreate(TableBase):
	pass


class TableUpdate(BaseModel):
	number: int | None = Field(
		None, gt=0, description="Number on top of physical table", example=1
	)
	chairs: int | None = Field(
		None, gt=0, description="Number of chairs available", example=4
	)
	size: Literal["small", "medium", "large"] | None = Field(
		None, description="Size of table", example="medium"
	)


class Table(TableBase):
	id: int = Field(..., description="Unique identifier for the table", example=1)
