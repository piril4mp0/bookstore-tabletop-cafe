from datetime import datetime

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column, relationship

from app.db.database import table_registry
from app.models.user import User


@mapped_as_dataclass(table_registry)
class RefreshToken:
	"""
	Represents a database-backed refresh token for user session management.
	- id: Primary key identifier.
	- token: Unique token string.
	- user_id: Foreign key referencing the user.
	- expires_at: Expiration timestamp.
	- revoked: Revocation flag.
	- created_at: Creation timestamp.
	- user: Relationship to User entity.
	"""

	__tablename__ = "refresh_tokens"

	id: Mapped[int] = mapped_column(
		init=False, primary_key=True, autoincrement=True, unique=True
	)
	token: Mapped[str] = mapped_column(
		String(255), unique=True, index=True, nullable=False
	)
	user_id: Mapped[int] = mapped_column(
		ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
	)
	expires_at: Mapped[datetime] = mapped_column(nullable=False)
	revoked: Mapped[bool] = mapped_column(
		default=False, server_default=text("false"), nullable=False
	)
	created_at: Mapped[datetime] = mapped_column(
		default_factory=datetime.now, nullable=False
	)
	user: Mapped[User] = relationship(init=False, lazy="selectin")
