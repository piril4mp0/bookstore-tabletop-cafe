from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.tag import Tag


class MenuCategory(str, Enum):
	DRINK = "drink"
	MEAL = "meal"


class MenuItemBase(BaseModel):
	name: str = Field(
		...,
		min_length=1,
		max_length=255,
		description="The name of the menu item",
		example="Espresso",
	)
	category: MenuCategory = Field(
		..., description="Category of the menu item", example=MenuCategory.DRINK
	)
	description: str | None = Field(
		None,
		max_length=500,
		description="Description of the menu item",
		example="Rich single-shot espresso",
	)
	price: float = Field(..., ge=0.0, description="Price of the item", example=3.50)
	stock: int = Field(0, ge=0, description="Available stock quantity", example=50)
	is_available: bool = Field(
		True,
		description="Whether item is active and available for ordering",
		example=True,
	)


class MenuItemCreate(MenuItemBase):
	tag_ids: list[int] = Field(
		default_factory=list,
		description="IDs of tags associated with this menu item",
		example=[1, 2],
	)


class MenuItemUpdate(BaseModel):
	name: str | None = Field(
		None, min_length=1, max_length=255, description="The name of the menu item"
	)
	category: MenuCategory | None = Field(None, description="Category of the menu item")
	description: str | None = Field(
		None, max_length=500, description="Description of the menu item"
	)
	price: float | None = Field(None, ge=0.0, description="Price of the item")
	stock: int | None = Field(None, ge=0, description="Available stock quantity")
	is_available: bool | None = Field(None, description="Availability status")
	tag_ids: list[int] | None = Field(
		None, description="IDs of tags associated with this menu item"
	)


class MenuItemAvailabilityUpdate(BaseModel):
	is_available: bool = Field(
		..., description="Whether item is available for ordering", example=False
	)


class MenuItem(MenuItemBase):
	id: int = Field(
		..., description="The unique identifier of the menu item", example=1
	)
	tags: list[Tag] = Field(default_factory=list, description="Associated tag objects")

	class Config:
		from_attributes = True
