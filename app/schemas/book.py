from typing import Optional, List
from pydantic import BaseModel, Field


class BookBase(BaseModel):
    isbn: str = Field(
        ...,
        min_length=10,
        max_length=13,
        description="The ISBN of the book",
        example="9780261103283"
    )
    title: str = Field(
        ..., 
        max_length=255, 
        description="The title of the book", 
        example="The Hobbit"
    )
    pages: int = Field(
        ..., gt=0, description="Number of pages in the book", example=310
    )
    authors: List[str] = Field(
        ..., description="List of authors", example=["J.R.R. Tolkien"]
    )
    year_released: int = Field(
        ..., description="The year the book was released", example=1937
    )
    stock: int = Field(default=0, ge=0, description="Current physical stock of the book")


class BookCreate(BookBase):
    pass


class BookPublic(BookBase):
    id: int = Field(..., description="The unique identifier of the book", example=1)


class BookPut(BaseModel):
    isbn: Optional[str] = Field(None, min_length=10, max_length=13, description="The ISBN of the book")
    title: Optional[str] = Field(None, max_length=255, description="The title of the book")
    pages: Optional[int] = Field(None, gt=0, description="Number of pages in the book")
    authors: Optional[List[str]] = Field(None, description="List of authors")
    year_released: Optional[int] = Field(None, description="The year the book was released")
    stock: Optional[int] = Field(None, ge=0, description="Current physical stock of the book")


class BookImport(BaseModel):
    """Schema used strictly for importing a book via an external integration"""
    isbn: str = Field(
        ...,
        min_length=10,
        max_length=13,
        description="The ISBN of the book to fetch and import from Open Library",
        example="9780261103283"
    )
    stock: Optional[int] = Field(default=0, ge=0, description="Current physical stock of the book")
