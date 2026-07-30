from http import HTTPStatus

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.dependencies import get_current_admin_user, get_db
from app.models.user import User as UserModel
from app.schemas.menu import (
	MenuCategory,
	MenuItem,
	MenuItemAvailabilityUpdate,
	MenuItemCreate,
	MenuItemUpdate,
)
from app.services.menu import MenuService

router = APIRouter(prefix="/menu", tags=["menu"])


@router.post("/", response_model=MenuItem, status_code=HTTPStatus.CREATED)
def create_menu_item(
	new_item: MenuItemCreate = Body(),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	return MenuService.save_item(db, new_item)


@router.get("/", response_model=list[MenuItem], status_code=HTTPStatus.OK)
def get_menu_items(
	category: MenuCategory | None = Query(default=None),
	is_available: bool | None = Query(default=None),
	tag_id: int | None = Query(default=None, gt=0),
	db: Session = Depends(get_db),
):
	cat_str = category.value if category else None
	return MenuService.get_items(
		db, category=cat_str, is_available=is_available, tag_id=tag_id
	)


@router.get("/{id}", response_model=MenuItem, status_code=HTTPStatus.OK)
def get_menu_item(id: int = Path(gt=0), db: Session = Depends(get_db)):
	item = MenuService.get_item_by_id(db, id)
	if not item:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND, detail="Menu item not found"
		)
	return item


@router.put("/{id}", response_model=MenuItem, status_code=HTTPStatus.OK)
def update_menu_item(
	id: int = Path(gt=0),
	updated_item: MenuItemUpdate = Body(),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	item = MenuService.update_item(db, id, updated_item)
	if not item:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND, detail="Menu item not found"
		)
	return item


@router.patch("/{id}/availability", response_model=MenuItem, status_code=HTTPStatus.OK)
def patch_menu_item_availability(
	id: int = Path(gt=0),
	availability_data: MenuItemAvailabilityUpdate = Body(),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	item = MenuService.update_availability(db, id, availability_data.is_available)
	if not item:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND, detail="Menu item not found"
		)
	return item


@router.delete("/{id}", status_code=HTTPStatus.NO_CONTENT)
def delete_menu_item(
	id: int = Path(gt=0),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	if not MenuService.delete_item(db, id):
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND, detail="Menu item not found"
		)
