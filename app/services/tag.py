from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tag import Tag as TagModel
from app.schemas.tag import TagCreate


class TagService:
	"""TagService Class deals with business logic involving Tags."""

	@staticmethod
	def create_tag(db: Session, tag: TagCreate) -> TagModel:
		"""Creates a new tag in the database.

		Args:
		    db (Session): Database session.
		    tag (TagCreate): Tag creation schema.

		Returns:
		    TagModel: The created tag model.
		"""
		new_tag = TagModel(name=tag.name)
		db.add(new_tag)
		db.commit()
		db.refresh(new_tag)
		return new_tag

	@staticmethod
	def get_tags(db: Session) -> list[TagModel]:
		"""Gets all tags from the database.

		Args:
		    db (Session): Database session.

		Returns:
		    list[TagModel]: List of tags.
		"""
		stmt = select(TagModel)
		return list(db.scalars(stmt).all())

	@staticmethod
	def get_tag_by_id(db: Session, id: int) -> TagModel | None:
		"""Gets a tag from the database by ID.

		Args:
		    db (Session): Database session.
		    id (int): Tag ID.

		Returns:
		    TagModel | None: The tag model if found, else None.
		"""
		return db.get(TagModel, id)

	@staticmethod
	def get_tags_by_ids(db: Session, ids: list[int]) -> list[TagModel]:
		"""Gets multiple tags from the database by list of IDs.

		Args:
		    db (Session): Database session.
		    ids (list[int]): List of tag IDs.

		Returns:
		    list[TagModel]: List of matching tag models.
		"""
		if not ids:
			return []
		stmt = select(TagModel).where(TagModel.id.in_(ids))
		return list(db.scalars(stmt).all())

	@staticmethod
	def delete_tag(db: Session, id: int) -> bool:
		"""Deletes a tag from the database.

		Args:
		    db (Session): Database session.
		    id (int): Tag ID.

		Returns:
		    bool: True if deleted, False if not found.
		"""
		tag = db.get(TagModel, id)
		if not tag:
			return False
		db.delete(tag)
		db.commit()
		return True
