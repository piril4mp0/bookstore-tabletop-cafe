# Tabletop Bookstore Cafe FastAPI Project


## Tech Stack
The tech stack is:

 * "alembic>=1.18.4", # Migrations library
  *  "fastapi[standard]>=0.136.1", # Backend framework
  *  "psycopg[binary]>=3.3.4", # PostgreSQL database adapter
   * "pwdlib[argon2]>=0.3.0", # Password hashing library
   * "pyjwt>=2.12.1", # JWT library
   * "pytest>=9.0.3", # Test library
   * "sqlalchemy>=2.0.49", # ORM library

## Rules
Act as a Senior Python FastAPI Developer. Always use the best practices for that framework. Only create safe and fast code that does not contain security vulnerabilities.

## Project Structure and file responsabilities
```
├── alembic.ini
├── app
│   ├── core # Env Settings
│   ├── db # Databse Settings
│   ├── dependencies.py # Dependency injection
│   ├── exceptions # Exceptions
│   ├── internal # Admin
│   ├── main.py # Main FastAPI App
│   ├── models # Database Models
│   ├── routers # API Routes
│   ├── schemas # Pydantic Models
│   └── services # Business Logic
├── GEMINI.md
├── migrations
├── pyproject.toml
├── README.md
├── tests
└── uv.lock
```