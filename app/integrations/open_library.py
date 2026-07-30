from http import HTTPStatus

import httpx
from fastapi import HTTPException

from app.core.settings import settings
from app.models.book import Book


async def fetch_book_from_open_library(isbn: str, stock: int) -> Book | None:
	url = f"{settings.OPEN_LIBRARY_API_URL}?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
	isbn_key = f"ISBN:{isbn}"
	async with httpx.AsyncClient() as client:
		try:
			response = await client.get(url, timeout=10.0)
			response.raise_for_status()
			data = response.json()
			if not data:
				raise HTTPException(
					status_code=HTTPStatus.NOT_FOUND,
					detail=f"Book with ISBN {isbn} not found in Open Library",
				)
			book_data = data[isbn_key]
			authors = [author.get("name") for author in book_data.get("authors", [])]
			publish_date = book_data.get("publish_date", "")
			pages = book_data.get("number_of_pages")
			title = book_data.get("title")
			return Book(
				authors=authors,
				isbn=isbn,
				pages=pages,
				title=title,
				year_released=publish_date,
				stock=stock,
				synopsis="No Synopsis",
			)
		except httpx.HTTPError as e:
			raise HTTPException(
				status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
				detail=f"Error fetching data from Open Library: {e!s}",
			)
