from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, computed_field


class OrderStatus(str, Enum):
	PENDING = "pending"
	PREPARING = "preparing"
	READY = "ready"
	SERVED = "served"
	CANCELLED = "cancelled"


class OrderItemCreate(BaseModel):
	menu_item_id: int = Field(
		..., description="ID of the menu item to order", example=1
	)
	quantity: int = Field(1, ge=1, description="Quantity of the menu item", example=2)


class OrderCreate(BaseModel):
	table_number: int = Field(
		..., description="Number of the game table where order is placed", example=1
	)
	items: list[OrderItemCreate] = Field(
		..., min_length=1, description="List of items in the order"
	)
	notes: str | None = Field(
		None,
		max_length=255,
		description="Optional special instructions or notes",
		example="Extra hot, please!",
	)


class OrderStatusUpdate(BaseModel):
	status: OrderStatus = Field(
		..., description="New order status", example=OrderStatus.PREPARING
	)


class OrderItemResponse(BaseModel):
	id: int = Field(..., description="Order item ID", example=1)
	menu_item_id: int = Field(..., description="Menu item ID", example=1)
	quantity: int = Field(..., description="Quantity ordered", example=2)
	unit_price: float = Field(..., description="Unit price per item", example=4.50)

	class Config:
		from_attributes = True


class OrderResponse(BaseModel):
	id: int = Field(..., description="Order ID", example=1)
	table_number: int = Field(..., description="Game table number", example=1)
	user_id: int | None = Field(
		None, description="ID of placing user, if logged in", example=1
	)
	status: OrderStatus = Field(
		..., description="Current order status", example=OrderStatus.PENDING
	)
	notes: str | None = Field(
		None, description="Order notes", example="Extra hot, please!"
	)
	created_at: datetime = Field(..., description="Timestamp when order was placed")
	items: list[OrderItemResponse] = Field(
		default_factory=list, description="Ordered items list"
	)

	@computed_field
	@property
	def total_price(self) -> float:
		return round(sum(item.quantity * item.unit_price for item in self.items), 2)

	class Config:
		from_attributes = True
