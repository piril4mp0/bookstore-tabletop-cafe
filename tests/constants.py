

ADMIN_DATA = {
    "username": "admin_test",
    "full_name": "Admin User",
    "email": "admin_test@gmail.com",
    "password": "password123",
}


# Book Constants
BOOK_DATA = {"isbn":"9788532511010", "title": "Harry Potter e a Pedra Filosofal", "stock": 10}
BOOK_IMPORT_BODY = {"isbn": BOOK_DATA["isbn"], "stock": BOOK_DATA['stock']}
BOOK_ENDPOINT = '/books'

# Game Constants
GAME_ENDPOINT = '/games'
CREATE_GAME_BODY = {
        "title": "@test_game",
        "genre": ["RPG", "Fantasy"],
        "description": "An epic fantasy role-playing game",
        "release_date": "2023-01-01",
        "players": 4,
    }