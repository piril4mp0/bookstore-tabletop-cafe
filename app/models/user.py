from datetime import datetime
from app.db.database import table_registry
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column


@mapped_as_dataclass(table_registry)
class User:
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True, unique=True
    )
    username: Mapped[str]
    email: Mapped[str]
    password: Mapped[str]
    full_name: Mapped[str] = mapped_column(nullable=True)

