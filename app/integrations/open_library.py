from app.core.settings import settings
import httpx
import asyncio

async def fetch_book_by_isbn(isbn: str) -> dict | None:
    url = f"{settings.OPEN_LIBRARY_API_URL}?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            #TODO
            return None
