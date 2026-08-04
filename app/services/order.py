from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.menu import MenuItem as MenuItemModel
from app.models.order import Order as OrderModel
from app.models.order import OrderItem as OrderItemModel
from app.models.table import GameTable as GameTableModel
from app.schemas.order import OrderCreate, OrderStatus


class OrderService:
	"""OrderService Class handles business logic for Order operations."""

	@staticmethod
	def create_order(
		db: Session, order_in: OrderCreate, user_id: int | None = None
	) -> OrderModel:
		"""Creates a new order with items for a table.
		Args:
		    db (Session): Database session.
		    order_in (OrderCreate): Order creation schema payload.
		    user_id (int | None, optional): Optional ID of placing user. Defaults to None.
		Returns:
		    OrderModel: The created Order instance.
		"""
		# 1. Validate game table exists by table_number
		stmt_table = select(GameTableModel).where(
			GameTableModel.number == order_in.table_number
		)
		table_obj = db.scalar(stmt_table)
		if not table_obj:
			raise HTTPException(
				status_code=HTTPStatus.NOT_FOUND,
				detail=f"Table with number {order_in.table_number} does not exist",
			)
		# 2. Validate menu items exist and are available
		order_items: list[OrderItemModel] = []
		for item_in in order_in.items:
			menu_item = db.get(MenuItemModel, item_in.menu_item_id)
			if not menu_item:
				raise HTTPException(
					status_code=HTTPStatus.NOT_FOUND,
					detail=f"Menu item with ID {item_in.menu_item_id} does not exist",
				)
			if not menu_item.is_available:
				raise HTTPException(
					status_code=HTTPStatus.BAD_REQUEST,
					detail=f'Menu item "{menu_item.name}" is not currently available',
				)
			order_item = OrderItemModel(
				menu_item_id=menu_item.id,
				quantity=item_in.quantity,
				unit_price=menu_item.price,
			)
			order_items.append(order_item)
		# 3. Create parent Order entity
		new_order = OrderModel(
			table_number=order_in.table_number,
			user_id=user_id,
			notes=order_in.notes,
			status=OrderStatus.PENDING.value,
			items=order_items,
		)
		db.add(new_order)
		db.commit()
		db.refresh(new_order)
		return new_order

	@staticmethod
	def get_orders(
		db: Session,
		user_id: int | None = None,
		table_number: int | None = None,
		status: str | None = None,
	) -> list[OrderModel]:
		"""Gets orders matching optional filters.
		Args:
		    db (Session): Database session.
		    user_id (int | None, optional): Filter by user ID. Defaults to None.
		    table_number (int | None, optional): Filter by table number. Defaults to None.
		    status (str | None, optional): Filter by status. Defaults to None.
		Returns:
		    list[OrderModel]: List of matching orders.
		"""
		stmt = select(OrderModel)
		if user_id is not None:
			stmt = stmt.where(OrderModel.user_id == user_id)
		if table_number is not None:
			stmt = stmt.where(OrderModel.table_number == table_number)
		if status:
			stmt = stmt.where(OrderModel.status == status)
		stmt = stmt.order_by(OrderModel.created_at.desc())
		return list(db.scalars(stmt).all())

	@staticmethod
	def get_order_by_id(db: Session, id: int) -> OrderModel | None:
		"""Gets an order by ID.
		Args:
		    db (Session): Database session.
		    id (int): Order ID.
		Returns:
		    OrderModel | None: Order model if found, else None.
		"""
		return db.get(OrderModel, id)

	@staticmethod
	def update_order_status(
		db: Session, id: int, status: OrderStatus
	) -> OrderModel | None:
		"""Updates status of an existing order.
		Args:
		    db (Session): Database session.
		    id (int): Order ID.
		    status (OrderStatus): New order status.
		Returns:
		    OrderModel | None: Updated Order model if found, else None.
		"""
		order = db.get(OrderModel, id)
		if not order:
			return None
		order.status = status.value if hasattr(status, "value") else str(status)
		db.commit()
		db.refresh(order)
		return order
