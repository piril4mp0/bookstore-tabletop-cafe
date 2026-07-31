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

### 3. Game Inventory ([app/models/game.py](file:///c:/projects/bookstore-tabletop-cafe/app/models/game.py))
- **Table**: `games`
- **Fields**:
  - `id`: Primary key (autoincrement)
  - `title`: `str` (unique, required)
  - `genre`: `list[str]` (`ARRAY(String)` on Postgres, `JSON` on SQLite)
  - `description`: `str`
  - `release_date`: `datetime`
  - `players`: `int`

### 4. Tag Management ([app/models/tag.py](file:///c:/projects/bookstore-tabletop-cafe/app/models/tag.py))
- **Table**: `tags`
- **Fields**:
  - `id`: Primary key (autoincrement)
  - `name`: `str` (50 chars, unique, required)

### 5. Menu Items ([app/models/menu.py](file:///c:/projects/bookstore-tabletop-cafe/app/models/menu.py))
- **Table**: `menu_items` (and association table `menu_item_tags`)
- **Fields**:
  - `id`: Primary key (autoincrement)
  - `name`: `str` (255 chars, unique, required)
  - `category`: `str` (`"drink"` or `"meal"`, required)
  - `price`: `float` (required, >= 0.0)
  - `description`: `Optional[str]` (500 chars)
  - `stock`: `int` (default `0`)
  - `is_available`: `bool` (default `true`)
  - `tags`: `list[Tag]` (many-to-many relationship with `Tag` via `menu_item_tags`)


---

## Database Migrations ([migrations/versions](file:///c:/projects/bookstore-tabletop-cafe/migrations/versions))
- **Latest Migration**: `f346dc1545dd_create_menu_items_and_tags_tables.py`
  - Created tables `menu_items`, `tags`, and association table `menu_item_tags`.

---

## API Routers & Endpoints

### Auth Router ([app/routers/auth.py](file:///c:/projects/bookstore-tabletop-cafe/app/routers/auth.py)) — Prefix: `/auth`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/auth/signup` | Public | Register new user account (`UserCreate` -> `UserPublic`) |
| `POST` | `/auth/login` | Public | Authenticate user & return JWT token (`OAuth2PasswordRequestForm` -> `Token`) |

### Book Router ([app/routers/book.py](file:///c:/projects/bookstore-tabletop-cafe/app/routers/book.py)) — Prefix: `/books`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/books/` | Public | List all books in catalog |
| `GET` | `/books/{isbn}` | Public | Get book details by ISBN |
| `POST` | `/books/import` | Admin | Fetch metadata from Open Library API by ISBN & import book |
| `PATCH` | `/books/add-stock/{isbn}` | Admin | Increase inventory stock count for a book |
| `PUT` | `/books/{isbn}` | Admin | Update book metadata |
| `DELETE` | `/books/{isbn}` | Admin | Delete book from catalog |

### Game Router ([app/routers/game.py](file:///c:/projects/bookstore-tabletop-cafe/app/routers/game.py)) — Prefix: `/games`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/games/` | Public | List games (optional query param `genre` filter) |
| `GET` | `/games/{id}` | Public | Get game details by ID |
| `POST` | `/games/` | Admin | Create new game entry |
| `PUT` | `/games/{id}` | Admin | Update game entry |
| `DELETE` | `/games/{id}` | Admin | Delete game entry |

### Tag Router ([app/routers/tag.py](file:///c:/projects/bookstore-tabletop-cafe/app/routers/tag.py)) — Prefix: `/tags`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/tags/` | Public | List all tags |
| `GET` | `/tags/{id}` | Public | Get tag by ID |
| `POST` | `/tags/` | Admin | Create new tag entry (`TagCreate` -> `Tag`) |
| `DELETE` | `/tags/{id}` | Admin | Delete tag entry |

### Menu Router ([app/routers/menu.py](file:///c:/projects/bookstore-tabletop-cafe/app/routers/menu.py)) — Prefix: `/menu`
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/menu/` | Public | List menu items (optional query filters: `category`, `is_available`, `tag_id`) |
| `GET` | `/menu/{id}` | Public | Get menu item details by ID |
| `POST` | `/menu/` | Admin | Create menu item (`MenuItemCreate` -> `MenuItem`) |
| `PUT` | `/menu/{id}` | Admin | Update menu item details (`MenuItemUpdate` -> `MenuItem`) |
| `PATCH` | `/menu/{id}/availability` | Admin | Quick toggle availability status (`MenuItemAvailabilityUpdate` -> `MenuItem`) |
| `DELETE` | `/menu/{id}` | Admin | Delete menu item |

---

## Service Layer & Integrations
- **Authentication Service**: [app/services/auth.py](file:///c:/projects/bookstore-tabletop-cafe/app/services/auth.py) (password verification, token generation).
- **Book Service**: [app/services/book.py](file:///c:/projects/bookstore-tabletop-cafe/app/services/book.py) (CRUD operations & stock management).
- **Game Service**: [app/services/game.py](file:///c:/projects/bookstore-tabletop-cafe/app/services/game.py) (CRUD operations & genre filtering).
- **Tag Service**: [app/services/tag.py](file:///c:/projects/bookstore-tabletop-cafe/app/services/tag.py) (Tag CRUD & multi-ID queries).
- **Menu Service**: [app/services/menu.py](file:///c:/projects/bookstore-tabletop-cafe/app/services/menu.py) (Menu item CRUD, tag association, availability toggle, filtering, and case-insensitive duplicate name validation on create/update).
- **Open Library Integration**: [app/integrations/open_library.py](file:///c:/projects/bookstore-tabletop-cafe/app/integrations/open_library.py) (async HTTP client using `httpx` to fetch ISBN metadata).
- **Dependency Injection**: [app/dependencies.py](file:///c:/projects/bookstore-tabletop-cafe/app/dependencies.py) (`get_db`, `get_current_user`, `get_current_admin_user`).


---

## Verification & Testing Commands

Run all verification checks locally before pushing or completing feature tasks:

```powershell
# 1. Linting
uv run ruff check .

# 2. Formatting Check
uv run ruff format --check .

# 3. Test Suite
$env:DATABASE_URL="sqlite:///./test.db"; $env:SECRET_KEY="test-secret"; $env:ACCESS_TOKEN_EXPIRE_MINUTES="60"; $env:JWT_ALGORITHM="HS256"; uv run python -m pytest
```

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
