from typing import Optional
from app.db.database import table_registry
from sqlalchemy import String, JSON
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column


@mapped_as_dataclass(table_registry)
class Book:
    """
    Represents a book entity with the following fields:
    - id: Unique identifier for the book.
    - title: Title of the book.
    - pages: Number of pages in the book.
    - authors: List of authors associated with the book.
    - year_released: The year the book was released.
    - synopsis: A brief summary or synopsis of the book.
    - isbn: The unique 10 or 13 character ISBN of the book.
    - stock: The current inventory stock level.
    """
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True, unique=True
    )
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default=None)
    pages: Mapped[Optional[int]] = mapped_column(nullable=True, default=None)
    authors: Mapped[Optional[list[str]]] = mapped_column(
        postgresql.ARRAY(String(255)).with_variant(JSON, "sqlite"), nullable=True, default=None
    )
    year_released: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default=None)
    synopsis: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True, default="No Synopsis Available")
    stock: Mapped[int] = mapped_column(default=0, nullable=False)
