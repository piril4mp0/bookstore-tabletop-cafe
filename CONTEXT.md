# Project Context: Bookstore Tabletop Cafe

## Overview
Bookstore Tabletop Cafe is an async FastAPI application powered by SQLAlchemy 2.0 and Pydantic. It handles book catalog, board game inventory, user accounts, and customer reservations.

## Implemented Workflows & Custom Skills

### `feature-implementation-workflow`
Location: [.agents/skills/feature-implementation-workflow/SKILL.md](file:///c:/projects/bookstore-tabletop-cafe/.agents/skills/feature-implementation-workflow/SKILL.md)

Enforces a 5-phase process to prevent codebase knowledge debt, eliminate hallucinations, and ensure high code quality:
1. **Context & Discovery**: Reads `CONTEXT.md` and existing codebase schemas to understand system state. The user provides the feature prompt directly.
2. **Grill-Me (Interactive Clarification)**: Asks targeted questions to lock down exact requirements, edge cases, and data structure expectations.
3. **Spec & Plan Sign-Off**: Generates a detailed specification covering Data Models, Pydantic Schemas, API Endpoints, and Affected Files. Waits for explicit user review & approval.
4. **Implementation**: Executes changes adhering to async FastAPI, Pydantic, and SQLAlchemy best practices (no unauthorized unit tests).
5. **Update `CONTEXT.md`**: Updates `CONTEXT.md` with new data structures, endpoints, and architectural changes.

---

## Architectural Conventions & Rules
- **Framework**: FastAPI (async def endpoints), Pydantic v2 schemas.
- **ORM / DB**: SQLAlchemy 2.0 async + Alembic migrations.
- **Testing Rule**: Do NOT create unit or integration tests unless explicitly requested by the user.
- **Knowledge Debt Prevention**: Always present plan/spec to user before coding and document updates in `CONTEXT.md`.
