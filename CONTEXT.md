# Project Context: Bookstore Tabletop Cafe

## Overview
Bookstore Tabletop Cafe is an async FastAPI backend system for managing a combined bookstore and tabletop gaming cafe. Built with **FastAPI**, **Pydantic v2**, **SQLAlchemy 2.0** (dataclass mapping), **Alembic**, and **PostgreSQL** (with SQLite fallback for tests). Features JWT authentication, role-based authorization (Admin / Customer), catalog management for books and games, and external integration with the Open Library API.

---

## Core Tech Stack & Dependencies
- **Backend Framework**: FastAPI (`fastapi[standard]>=0.136.1`)
- **ORM & Database**: SQLAlchemy 2.0 (`sqlalchemy>=2.0.49`), Alembic migrations (`alembic>=1.18.4`), PostgreSQL driver (`psycopg[binary]>=3.3.4`)
- **Authentication**: JWT (`pyjwt>=2.12.1`), Argon2 password hashing (`pwdlib[argon2]>=0.3.0`)
- **HTTP Client**: HTTPX (`httpx`) for external Open Library API integration
- **Linter & Formatter**: Ruff (`ruff>=0.15.13`)
- **Testing**: Pytest (`pytest>=9.0.3`)

---

## Domain Architecture & Data Models

### 1. User Management ([app/models/user.py](file:///c:/projects/bookstore-tabletop-cafe/app/models/user.py))
- **Table**: `users`
- **Fields**:
  - `id`: Primary key (autoincrement)
  - `username`: `str`
  - `email`: `str`
  - `password`: `str` (Argon2 hash)
  - `full_name`: `Optional[str]`
  - `is_admin`: `bool` (default `false`)

### 2. Book Catalog ([app/models/book.py](file:///c:/projects/bookstore-tabletop-cafe/app/models/book.py))
- **Table**: `books`
- **Fields**:
  - `id`: Primary key (autoincrement)
  - `isbn`: `str` (10 or 13 chars, unique, required)
  - `title`: `Optional[str]` (255 chars)
  - `pages`: `Optional[int]`
  - `authors`: `Optional[list[str]]` (`ARRAY(String)` on Postgres, `JSON` on SQLite)
  - `year_released`: `Optional[str]`
  - `synopsis`: `Optional[str]` (default "No Synopsis Available")
  - `stock`: `int` (default `0`)

### 3. Game Inventory ([app/models/game.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/models/game.py))
- **Table**: `games`
- **Fields**:
  - `id`: Primary key (autoincrement)
  - `title`: `str` (unique, required)
  - `genre`: `list[str]` (`ARRAY(String)` on Postgres, `JSON` on SQLite)
  - `description`: `str`
  - `release_date`: `datetime`
  - `players`: `int`
  - `stock`: `int` (default `1`)
  - `current_stock`: `int` (default `1`)

### 4. Tag Management ([app/models/tag.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/models/tag.py))
- **Table**: `tags`
- **Fields**:
  - `id`: Primary key (autoincrement)
  - `name`: `str` (50 chars, unique, required)

### 5. Menu Items ([app/models/menu.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/models/menu.py))
- **Table**: `menu_items` (and association table `menu_item_tags`)
- **Fields**:
  - `id`: Primary key (autoincrement)
  - `name`: `str` (255 chars, unique, required)
  - `category`: `str` (`"drink"` or `"meal"`, required)
  - `price`: `float` (required, >= 0.0)
  - `description`: `Optional[str]` (500 chars)
  - `is_available`: `bool` (default `true`)
  - `tags`: `list[Tag]` (many-to-many relationship with `Tag` via `menu_item_tags`)

### 6. Game Tables ([app/models/table.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/models/table.py))
- **Table**: `game_tables`
- **Fields**:
  - `id`: Primary key (autoincrement)
  - `number`: `int` (unique, required)
  - `chairs`: `int` (required)
  - `size`: `str` (`"small"`, `"medium"`, `"large"`)

### 7. Operating Hours ([app/models/operating_hours.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/models/operating_hours.py))
- **Table**: `operating_hours`
- **Fields**:
  - `id`: Primary key (autoincrement)
  - `day_of_week`: `int` (0=Monday ... 6=Sunday, unique, required)
  - `open_time`: `time` (required)
  - `close_time`: `time` (required)
  - `is_closed`: `bool` (default `false`)

### 8. Reservations ([app/models/reservation.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/models/reservation.py))
- **Table**: `reservations`
- **Fields**:
  - `id`: Primary key (autoincrement)
  - `user_id`: `int` (foreign key to `users.id`)
  - `game_id`: `int` (foreign key to `games.id`)
  - `table_id`: `int` (foreign key to `game_tables.id`)
  - `starts_at`: `datetime` (required)
  - `ends_at`: `datetime` (required)
  - `status`: `str` (default `"active"`, values: `"active"`, `"cancelled"`, `"completed"`)

### 9. Orders & Order Items ([app/models/order.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/models/order.py))
- **Table**: `orders` and `order_items`
- **Fields (`orders`)**:
  - `id`: Primary key (autoincrement)
  - `table_number`: `int` (foreign key to `game_tables.number`)
  - `user_id`: `Optional[int]` (foreign key to `users.id`)
  - `notes`: `Optional[str]` (255 chars)
  - `status`: `str` (default `"pending"`, values: `"pending"`, `"preparing"`, `"ready"`, `"served"`, `"cancelled"`)
  - `created_at`: `datetime` (required)
- **Fields (`order_items`)**:
  - `id`: Primary key (autoincrement)
  - `order_id`: `int` (foreign key to `orders.id`, cascade delete)
  - `menu_item_id`: `int` (foreign key to `menu_items.id`, cascade delete)
  - `unit_price`: `float` (historical price snapshot)
  - `quantity`: `int` (default 1)

---

## Database Migrations ([migrations/versions](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/migrations/versions))
- **Latest Migration**: `8a2b3c4d5e6f_add_orders_and_remove_menu_stock.py`
  - Created tables `orders` and `order_items`; dropped obsolete `stock` column from `menu_items`.

---

## API Routers & Endpoints

### Auth Router ([app/routers/auth.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/routers/auth.py)) — Prefix: `/auth`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/auth/signup` | Public | Register new user account (`UserCreate` -> `UserPublic`) |
| `POST` | `/auth/login` | Public | Authenticate user & return JWT token (`OAuth2PasswordRequestForm` -> `Token`) |

### Book Router ([app/routers/book.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/routers/book.py)) — Prefix: `/books`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/books/` | Public | List all books in catalog |
| `GET` | `/books/{isbn}` | Public | Get book details by ISBN |
| `POST` | `/books/import` | Admin | Fetch metadata from Open Library API by ISBN & import book |
| `PATCH` | `/books/add-stock/{isbn}` | Admin | Increase inventory stock count for a book |
| `PUT` | `/books/{isbn}` | Admin | Update book metadata |
| `DELETE` | `/books/{isbn}` | Admin | Delete book from catalog |

### Game Router ([app/routers/game.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/routers/game.py)) — Prefix: `/games`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/games/` | Public | List games (optional query param `genre` filter) |
| `GET` | `/games/{id}` | Public | Get game details by ID |
| `POST` | `/games/` | Admin | Create new game entry |
| `PUT` | `/games/{id}` | Admin | Update game entry |
| `DELETE` | `/games/{id}` | Admin | Delete game entry |

### Tag Router ([app/routers/tag.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/routers/tag.py)) — Prefix: `/tags`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/tags/` | Public | List all tags |
| `GET` | `/tags/{id}` | Public | Get tag by ID |
| `POST` | `/tags/` | Admin | Create new tag entry (`TagCreate` -> `Tag`) |
| `DELETE` | `/tags/{id}` | Admin | Delete tag entry |

### Menu Router ([app/routers/menu.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/routers/menu.py)) — Prefix: `/menu`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/menu/` | Public | List menu items (optional query filters: `category`, `is_available`, `tag_id`) |
| `GET` | `/menu/{id}` | Public | Get menu item details by ID |
| `POST` | `/menu/` | Admin | Create menu item (`MenuItemCreate` -> `MenuItem`) |
| `PUT` | `/menu/{id}` | Admin | Update menu item details (`MenuItemUpdate` -> `MenuItem`) |
| `PATCH` | `/menu/{id}/availability` | Admin | Quick toggle availability status (`MenuItemAvailabilityUpdate` -> `MenuItem`) |
| `DELETE` | `/menu/{id}` | Admin | Delete menu item |

### Table Router ([app/routers/table.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/routers/table.py)) — Prefix: `/tables`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/tables/` | Public | List all game tables |
| `GET` | `/tables/{id}` | Public | Get game table by ID |
| `POST` | `/tables/` | Admin | Create game table (`TableCreate` -> `Table`) |
| `PUT` | `/tables/{id}` | Admin | Update game table (`TableUpdate` -> `Table`) |
| `DELETE` | `/tables/{id}` | Admin | Delete game table |

### Operating Hours Router ([app/routers/operating_hours.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/routers/operating_hours.py)) — Prefix: `/operating-hours`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/operating-hours/` | Public | List operating hours for all days (0-6) |
| `GET` | `/operating-hours/{day_of_week}` | Public | Get operating hours for a specific day |
| `PUT` | `/operating-hours/{day_of_week}` | Admin | Upsert operating hours for a day (`OperatingHoursUpdate` -> `OperatingHoursResponse`) |

### Reservation Router ([app/routers/reservation.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/routers/reservation.py)) — Prefix: `/reservations`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/reservations/` | Authenticated | Create a table and game reservation (`ReservationCreate` -> `ReservationResponse`) |
| `GET` | `/reservations/` | Authenticated | List reservations (Customer sees own, Admin sees all) |
| `GET` | `/reservations/{id}` | Authenticated | Get reservation details by ID (Owner or Admin) |
| `PATCH` | `/reservations/{id}/cancel` | Authenticated | Cancel reservation and replenish game stock (Owner or Admin) |

### Order Router ([app/routers/order.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/routers/order.py)) — Prefix: `/orders`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/orders/` | Admin | Create multi-item order at a game table (`OrderCreate` -> `OrderResponse`) |
| `GET` | `/orders/` | Admin | List all orders (Admin only; filters: `table_number`, `status`) |
| `GET` | `/orders/{id}` | Admin | Get order details by ID (Admin only) |
| `PATCH` | `/orders/{id}/status` | Admin | Update order status (`pending` -> `preparing` -> `ready` -> `served` / `cancelled`) |

---

## Service Layer & Integrations
- **Authentication Service**: [app/services/auth.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/services/auth.py) (password verification, token generation).
- **Book Service**: [app/services/book.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/services/book.py) (CRUD operations & stock management).
- **Game Service**: [app/services/game.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/services/game.py) (CRUD operations, genre filtering, and stock management).
- **Tag Service**: [app/services/tag.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/services/tag.py) (Tag CRUD, multi-ID queries, and case-insensitive duplicate name validation).
- **Menu Service**: [app/services/menu.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/services/menu.py) (Menu item CRUD, tag association, availability toggle, filtering).
- **Table Service**: [app/services/table.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/services/table.py) (Game table CRUD and duplicate number checks).
- **Operating Hours Service**: [app/services/operating_hours.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/services/operating_hours.py) (Store hours retrieval and upsert).
- **Reservation Service**: [app/services/reservation.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/services/reservation.py) (Table overlap validation, operating hours validation, 30m minimum duration check, game stock check/decrement, and cancellation replenishment).
- **Order Service**: [app/services/order.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/services/order.py) (Multi-item order creation, table number validation, availability check, order listing with role filters, status progression).
- **Open Library Integration**: [app/integrations/open_library.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/integrations/open_library.py) (async HTTP client using `httpx` to fetch ISBN metadata).
- **Dependency Injection**: [app/dependencies.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/dependencies.py) (`get_db`, `get_current_user`, `get_current_admin_user`).



---

## Verification & Testing Commands

Run all verification checks locally before pushing or completing feature tasks:

```powershell
# 1. Linting
uv run ruff check .

# 2. Formatting Check
uv run ruff format --check .

# 3. Test Suite (66 integration tests passing)
$env:DATABASE_URL="sqlite:///./test.db"; $env:SECRET_KEY="test-secret"; $env:ACCESS_TOKEN_EXPIRE_MINUTES="60"; $env:JWT_ALGORITHM="HS256"; uv run python -m pytest
```

### Integration Test Suites (`tests/integration/`)
- [test_book.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/tests/integration/test_book.py): Book catalog CRUD, Open Library import, stock updates.
- [test_game.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/tests/integration/test_game.py): Game catalog CRUD, genre filtering, stock handling.
- [test_menu.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/tests/integration/test_menu.py): Menu item CRUD, category/tag filtering, availability toggle.
- [test_tag.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/tests/integration/test_tag.py): Tag CRUD and case-insensitive uniqueness checks.
- [test_table.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/tests/integration/test_table.py): Game table CRUD, table number conflict validation, public/admin authorization.
- [test_operating_hours.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/tests/integration/test_operating_hours.py): Store hours list, get by day (0-6), admin upsert, non-admin permissions.
- [test_reservation.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/tests/integration/test_reservation.py): Reservation creation, duration check (>=30m), same calendar day validation, store operating hours validation, table overlap prevention, game stock decrement & cancellation replenishment, customer/admin authorization.
- [test_order.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/tests/integration/test_order.py): Multi-item order creation, invalid table validation, item availability check, total price calculation, admin onlyvisibility, status workflow (`pending` -> `preparing` -> `ready` -> `served`).

### Local GitHub Actions Runner (`act`)
Emulate `.github/workflows/` locally using Docker and `nektos/act`:
- **Install**: `winget install nektos.act` (or `choco install act-cli` / `scoop install act`)
- **Run push workflows**: `act push`
- **Run specific job**: `act -j ruff` or `act -j test`

---

## Installed Skills & Workflows

### `feature-implementation-workflow`
Location: [.agents/skills/feature-implementation-workflow/SKILL.md](file:///c:/projects/bookstore-tabletop-cafe/.agents/skills/feature-implementation-workflow/SKILL.md)

Enforces a 6-phase process to prevent codebase knowledge debt, eliminate hallucinations, ensure high code quality, generate and execute Alembic database migrations when DB models change, run automated tests/linters, and maintain documentation:
1. **Context & Discovery**: Read `CONTEXT.md` and codebase schemas to understand system state. The user provides feature requirements directly.
2. **Grill-Me (Interactive Clarification)**: Ask targeted questions to clarify exact requirements, business rules, and edge cases.
3. **Spec & Plan Sign-Off**: Detail Data Models, Migration Files, Pydantic Schemas, API Endpoints, and File Changes. Wait for explicit user approval before coding.
4. **Implementation & Migrations**: Execute changes adhering to async FastAPI, Pydantic, and SQLAlchemy best practices. When DB models change, generate and run Alembic migrations (`alembic revision --autogenerate` & `alembic upgrade head`) following `sqlalchemy-postgres` skill guidance.
5. **Automated Verification & Testing**: Verify DB migrations run cleanly (`alembic upgrade head`), run `ruff check .`, `ruff format --check .`, and `pytest`. Report any failures immediately to the user and fix before concluding.
6. **Update `CONTEXT.md`**: Update `CONTEXT.md` with new data structures, migrations, endpoints, verification status, and architectural changes.

### Additional Installed Skills
- `sqlalchemy-postgres`: Patterns & guidance for SQLAlchemy 2.0 + PostgreSQL.
- `caveman` / `caveman-commit`: Ultra-compressed communication and conventional commit message generator.
- `skill-creator`: Skill creation, evaluation, and iteration tool.
