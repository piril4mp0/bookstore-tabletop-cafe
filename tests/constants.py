ADMIN_DATA = {
	"username": "admin_test",
	"full_name": "Admin User",
	"email": "admin_test@gmail.com",
	"password": "password123",
}


# Book Constants
BOOK_DATA = {
	"isbn": "9788532511010",
	"title": "Harry Potter e a Pedra Filosofal",
	"stock": 10,
}
BOOK_IMPORT_BODY = {"isbn": BOOK_DATA["isbn"], "stock": BOOK_DATA["stock"]}
BOOK_ENDPOINT = "/books"

# Game Constants
GAME_ENDPOINT = "/games"
CREATE_GAME_BODY = {
	"title": "@test_game",
	"genre": ["RPG", "Fantasy"],
	"description": "An epic fantasy role-playing game",
	"release_date": "2023-01-01",
	"players": 4,
}

# Tag Constants
TAG_ENDPOINT = "/tags"
CREATE_TAG_BODY = {"name": "vegan"}

# Menu Constants
MENU_ENDPOINT = "/menu"
CREATE_MENU_DRINK_BODY = {
	"name": "Oat Milk Latte",
	"category": "drink",
	"description": "Creamy espresso with oat milk",
	"price": 4.50,
	"stock": 25,
	"is_available": True,
}
CREATE_MENU_MEAL_BODY = {
	"name": "Avocado Toast",
	"category": "meal",
	"description": "Sourdough toast topped with smashed avocado",
	"price": 8.00,
	"stock": 15,
	"is_available": True,
}
