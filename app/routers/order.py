from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_current_admin_user, get_db
from app.models.user import User as UserModel
from app.schemas.order import (
	OrderCreate,
	OrderResponse,
	OrderStatus,
	OrderStatusUpdate,
)
from app.services.order import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=HTTPStatus.CREATED)
def create_order(
	order_in: OrderCreate,
	db: Session = Depends(get_db),
	current_admin: UserModel = Depends(get_current_admin_user),
):
	"""Places a new order for a table (Admin / Staff only)."""
	return OrderService.create_order(db, order_in, user_id=current_admin.id)


@router.get("/", response_model=list[OrderResponse], status_code=HTTPStatus.OK)
def list_orders(
	table_number: int | None = Query(None, description="Filter by table number"),
	status: OrderStatus | None = Query(None, description="Filter by order status"),
	db: Session = Depends(get_db),
	current_admin: UserModel = Depends(get_current_admin_user),
):
	"""Lists orders (Admin only). Supports filtering by table_number and status."""
	status_str = status.value if status else None
	return OrderService.get_orders(
		db, user_id=None, table_number=table_number, status=status_str
	)


@router.get("/{id}", response_model=OrderResponse, status_code=HTTPStatus.OK)
def get_order(
	id: int,
	db: Session = Depends(get_db),
	current_admin: UserModel = Depends(get_current_admin_user),
):
	"""Gets order details by ID (Admin only)."""
	order = OrderService.get_order_by_id(db, id)
	if not order:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND, detail=f"Order with ID {id} not found"
		)
	return order


@router.patch("/{id}/status", response_model=OrderResponse, status_code=HTTPStatus.OK)
def update_order_status(
	id: int,
	status_update: OrderStatusUpdate,
	db: Session = Depends(get_db),
	current_admin: UserModel = Depends(get_current_admin_user),
):
	"""Updates the order status (Admin / Staff only)."""
	order = OrderService.update_order_status(db, id, status_update.status)
	if not order:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND, detail=f"Order with ID {id} not found"
		)
	return order
