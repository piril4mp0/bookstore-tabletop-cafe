# Table Reservation System Implementation Plan

Implementation plan for adding game table management, store operating hours, game stock tracking, and table reservation functionality.

## Overview
Users can book and reserve a game table along with a game. When reserved, the game's `current_stock` is decremented by 1. A table cannot be double-booked for overlapping time slots. Reservations are constrained by store operating hours (configurable per day of week by Admin) and must be at least 30 minutes in duration, booked at least 30 minutes prior to store closing time.

---

## User Review Required

> [!IMPORTANT]
> - **Game Stock Management**: `Game` model will now track total `stock` (default `1`) and available `current_stock` (default `1`). Reserving a game decrements `current_stock`. Cancelling a reservation or completing it restores `current_stock`.
> - **Store Operating Hours**: Admin can configure open/close times and closed status for each day of the week (0 = Monday ... 6 = Sunday). Reservations validate against these hours.
> - **Table Overlap Check**: Tables cannot have active overlapping reservations (`(existing.starts_at < request.ends_at) and (existing.ends_at > request.starts_at)`).

---

## Proposed Changes

### Database Layer & Data Models

#### [MODIFY] [game.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/models/game.py)
- Add `stock: Mapped[int] = mapped_column(default=1, nullable=False)`
- Add `current_stock: Mapped[int] = mapped_column(default=1, nullable=False)`

#### [NEW] [table.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/models/table.py)
- Define `GameTable` model:
  - `id: Mapped[int]` (PK, autoincrement)
  - `number: Mapped[int]` (Unique, physical table number)
  - `chairs: Mapped[int]` (Number of available chairs)
  - `size: Mapped[str]` (Constraint/enum: `'small'`, `'medium'`, `'large'`)

#### [NEW] [operating_hours.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/models/operating_hours.py)
- Define `OperatingHours` model:
  - `id: Mapped[int]` (PK, autoincrement)
  - `day_of_week: Mapped[int]` (0 = Monday, ..., 6 = Sunday; unique)
  - `open_time: Mapped[time]` (Store opening time)
  - `close_time: Mapped[time]` (Store closing time)
  - `is_closed: Mapped[bool]` (Default `False`)

#### [NEW] [reservation.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/models/reservation.py)
- Define `Reservation` model:
  - `id: Mapped[int]` (PK, autoincrement)
  - `user_id: Mapped[int]` (FK to `users.id`)
  - `game_id: Mapped[int]` (FK to `games.id`)
  - `table_id: Mapped[int]` (FK to `game_tables.id`)
  - `starts_at: Mapped[datetime]`
  - `ends_at: Mapped[datetime]`
  - `status: Mapped[str]` (Default `"active"`, values: `"active"`, `"cancelled"`, `"completed"`)

#### [MODIFY] [env.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/migrations/env.py)
- Register `GameTable`, `OperatingHours`, and `Reservation` models for Alembic autogeneration.

---

### Schemas Layer

#### [MODIFY] [game.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/schemas/game.py)
- Add `stock: int` and `current_stock: int` to `GameBase`, `GameCreate`, `Game`, and `GamePut`.

#### [NEW] [table.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/schemas/table.py)
- Pydantic schemas: `TableCreate`, `TableUpdate`, `TableResponse`.

#### [NEW] [operating_hours.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/schemas/operating_hours.py)
- Pydantic schemas: `OperatingHoursCreate`, `OperatingHoursUpdate`, `OperatingHoursResponse`.

#### [NEW] [reservation.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/schemas/reservation.py)
- Pydantic schemas: `ReservationCreate`, `ReservationResponse`.

---

### Service & Router Layer

#### [NEW] [table.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/services/table.py) & [table.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/routers/table.py)
- `/tables/` endpoints:
  - `GET /tables/`: List all game tables (Public).
  - `GET /tables/{id}`: Get table details (Public).
  - `POST /tables/`: Create table (Admin).
  - `PUT /tables/{id}`: Update table (Admin).
  - `DELETE /tables/{id}`: Delete table (Admin).

#### [NEW] [operating_hours.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/services/operating_hours.py) & [operating_hours.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/routers/operating_hours.py)
- `/operating-hours/` endpoints:
  - `GET /operating-hours/`: List operating hours for all days of the week (Public).
  - `PUT /operating-hours/{day_of_week}`: Set/update operating hours for a specific day 0-6 (Admin).

#### [NEW] [reservation.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/services/reservation.py) & [reservation.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/routers/reservation.py)
- `/reservations/` endpoints:
  - `POST /reservations/`: Create reservation (Authenticated User).
    - Validates:
      1. `ends_at >= starts_at + 30 min`
      2. Store operating hours for `starts_at.weekday()` (not closed, `starts_at.time() >= open_time`, `starts_at + 30m <= close_time`, `ends_at.time() <= close_time`)
      3. `table_id` exists & has no overlapping active reservation
      4. `game_id` exists & `game.current_stock > 0`
    - Decrements `game.current_stock` by 1 and saves reservation.
  - `GET /reservations/`: List user's reservations (or all reservations if Admin).
  - `GET /reservations/{id}`: Get reservation details (Owner or Admin).
  - `PATCH /reservations/{id}/cancel`: Cancel reservation (Owner or Admin). Restores `game.current_stock`.

#### [MODIFY] [game.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/services/game.py)
- Update `save_game` and `update_game` logic to initialize and handle `stock` and `current_stock`.

#### [MODIFY] [main.py](file:///c:/Users/muril/Projects/bookstore-tabletop-cafe/app/main.py)
- Include `tables_router`, `operating_hours_router`, and `reservations_router`.

---

## Migration Strategy

Generate and execute Alembic migration:
```bash
uv run alembic revision --autogenerate -m "add_tables_operating_hours_and_reservations"
uv run alembic upgrade head
```

---

## Verification Plan

### Automated Checks & Tests
- Execute database migration check:
  `uv run alembic upgrade head`
- Execute ruff linter check:
  `uv run ruff check .`
- Execute ruff formatter check:
  `uv run ruff format --check .`
- Execute existing pytest test suite:
  `$env:DATABASE_URL="sqlite:///./test.db"; $env:SECRET_KEY="test-secret"; $env:ACCESS_TOKEN_EXPIRE_MINUTES="60"; $env:JWT_ALGORITHM="HS256"; uv run python -m pytest`

