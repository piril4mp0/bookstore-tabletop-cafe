from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column

from app.db.database import table_registry


@mapped_as_dataclass(table_registry)
class Tag:
	"""
	Represents a tag entity (e.g. vegan, gluten-free, caffeinated).
	- id: Unique identifier for the tag.
	- name: Unique tag name.
	"""

	__tablename__ = "tags"

	id: Mapped[int] = mapped_column(
		init=False, primary_key=True, autoincrement=True, unique=True
	)
	name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
