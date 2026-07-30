from pydantic import BaseModel, Field


class IncreaseBookStock(BaseModel):
	stock: int = Field(..., description="Stock to increase", example=10)


class BookBase(BaseModel):
	isbn: str = Field(
		...,
		min_length=10,
		max_length=13,
		description="The ISBN of the book",
		example="9780261103283",
	)
	title: str | None = Field(
		None, max_length=255, description="The title of the book", example="The Hobbit"
	)
	pages: int | None = Field(
		None, gt=0, description="Number of pages in the book", example=310
	)
	authors: list[str] | None = Field(
		None, description="List of authors", example=["J.R.R. Tolkien"]
	)
	year_released: str | None = Field(
		None, description="The year the book was released", example="1937"
	)
	stock: int = Field(
		default=0, ge=0, description="Current physical stock of the book"
	)


class BookCreate(BookBase):
	pass


class BookPublic(BookBase):
	id: int = Field(..., description="The unique identifier of the book", example=1)


class BookPut(BaseModel):
	isbn: str | None = Field(
		None, min_length=10, max_length=13, description="The ISBN of the book"
	)
	title: str | None = Field(None, max_length=255, description="The title of the book")
	pages: int | None = Field(None, gt=0, description="Number of pages in the book")
	authors: list[str] | None = Field(None, description="List of authors")
	year_released: str | None = Field(
		None, description="The year the book was released"
	)
	stock: int | None = Field(
		None, ge=0, description="Current physical stock of the book"
	)


class BookImport(BaseModel):
	"""Schema used strictly for importing a book via an external integration"""

	isbn: str = Field(
		...,
		min_length=10,
		max_length=13,
		description="The ISBN of the book to fetch and import from Open Library",
		example="9780261103283",
	)
	stock: int | None = Field(
		default=0, ge=0, description="Current physical stock of the book"
	)
