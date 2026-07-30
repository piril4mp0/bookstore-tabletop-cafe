from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.menu import MenuItem as MenuItemModel
from app.models.tag import Tag as TagModel
from app.schemas.menu import MenuItemCreate, MenuItemUpdate
from app.services.tag import TagService


class MenuService:
	"""MenuService Class deals with business logic involving the Menu endpoint."""

	@staticmethod
	def save_item(db: Session, item: MenuItemCreate) -> MenuItemModel:
		"""Saves a menu item to the database.

		Args:
		    db (Session): Database session.
		    item (MenuItemCreate): Menu item creation schema.

		Returns:
		    MenuItemModel: The saved menu item model.
		"""
		tags = TagService.get_tags_by_ids(db, item.tag_ids) if item.tag_ids else []
		new_item = MenuItemModel(
			name=item.name,
			category=item.category.value
			if hasattr(item.category, "value")
			else str(item.category),
			description=item.description,
			price=item.price,
			stock=item.stock,
			is_available=item.is_available,
			tags=tags,
		)
		db.add(new_item)
		db.commit()
		db.refresh(new_item)
		return new_item

	@staticmethod
	def get_items(
		db: Session,
		category: str | None = None,
		is_available: bool | None = None,
		tag_id: int | None = None,
	) -> list[MenuItemModel]:
		"""Gets all menu items matching optional filters.

		Args:
		    db (Session): Database session.
		    category (str | None, optional): Filter by category ('drink' or 'meal'). Defaults to None.
		    is_available (bool | None, optional): Filter by availability status. Defaults to None.
		    tag_id (int | None, optional): Filter by tag ID. Defaults to None.

		Returns:
		    list[MenuItemModel]: List of matching menu item models.
		"""
		stmt = select(MenuItemModel)
		if category:
			stmt = stmt.where(MenuItemModel.category == category)
		if is_available is not None:
			stmt = stmt.where(MenuItemModel.is_available == is_available)
		if tag_id is not None:
			stmt = stmt.where(MenuItemModel.tags.any(TagModel.id == tag_id))

		return list(db.scalars(stmt).all())

	@staticmethod
	def get_item_by_id(db: Session, id: int) -> MenuItemModel | None:
		"""Gets a menu item from the database by ID.

		Args:
		    db (Session): Database session.
		    id (int): Menu item ID.

		Returns:
		    MenuItemModel | None: Menu item model if found, else None.
		"""
		return db.get(MenuItemModel, id)

	@staticmethod
	def update_item(
		db: Session, id: int, item_update: MenuItemUpdate
	) -> MenuItemModel | None:
		"""Updates a menu item in the database.

		Args:
		    db (Session): Database session.
		    id (int): Menu item ID.
		    item_update (MenuItemUpdate): Update schema payload.

		Returns:
		    MenuItemModel | None: Updated menu item model if found, else None.
		"""
		current_item = db.get(MenuItemModel, id)
		if not current_item:
			return None

		update_data = item_update.model_dump(exclude_unset=True)

		if "tag_ids" in update_data:
			tag_ids = update_data.pop("tag_ids")
			if tag_ids is not None:
				current_item.tags = TagService.get_tags_by_ids(db, tag_ids)

		for key, value in update_data.items():
			if key == "category" and value is not None:
				value = value.value if hasattr(value, "value") else str(value)
			setattr(current_item, key, value)

		db.commit()
		db.refresh(current_item)
		return current_item

	@staticmethod
	def update_availability(
		db: Session, id: int, is_available: bool
	) -> MenuItemModel | None:
		"""Updates the availability status of a menu item.

		Args:
		    db (Session): Database session.
		    id (int): Menu item ID.
		    is_available (bool): New availability status.

		Returns:
		    MenuItemModel | None: Updated menu item model if found, else None.
		"""
		current_item = db.get(MenuItemModel, id)
		if not current_item:
			return None

		current_item.is_available = is_available
		db.commit()
		db.refresh(current_item)
		return current_item

	@staticmethod
	def delete_item(db: Session, id: int) -> bool:
		"""Deletes a menu item from the database.

		Args:
		    db (Session): Database session.
		    id (int): Menu item ID.

		Returns:
		    bool: True if deleted, False if not found.
		"""
		current_item = db.get(MenuItemModel, id)
		if not current_item:
			return False
		db.delete(current_item)
		db.commit()
		return True
