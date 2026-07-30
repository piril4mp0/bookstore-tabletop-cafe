---
name: feature-implementation-workflow
description: Guided feature implementation workflow to prevent codebase knowledge debt, eliminate hallucinations, clarify user intent, obtain plan sign-off, run automated checks (ruff, pytest), report failures, and update CONTEXT.md. Use whenever implementing features, creating endpoints, modifying data models, or when the user asks to build or extend functionality.
---

# Feature Implementation Workflow

This skill enforces a structured, interactive 6-phase process for implementing features in the codebase. It ensures high technical quality, prevents agent hallucinations, avoids "codebase knowledge debt" by keeping the user informed of architectural decisions, runs automated checks/tests, and maintains `CONTEXT.md`.

## Workflow Phases

```
┌─────────────────────────┐
│ 1. Context & Discovery  │  Read CONTEXT.md & inspect codebase models/schemas
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 2. Grill-Me (Clarify)   │  Ask questions to lock down intent & requirements
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 3. Spec & Plan Review   │  Write detailed spec (models, endpoints, files) & get sign-off
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 4. Implementation       │  Write clean async FastAPI/SQLAlchemy code
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 5. Automated Checks     │  Run ruff check, ruff format --check, & pytest; report failures
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 6. Update CONTEXT.md    │  Document new structures & architecture in CONTEXT.md
└─────────────────────────┘
```

---

### Phase 1: Context & Discovery

1. **Read Project Context**: View [CONTEXT.md](file:///c:/projects/bookstore-tabletop-cafe/CONTEXT.md) in the workspace root to understand current system context and existing domain structures.
2. **Inspect Existing Code**: Check existing database models, Pydantic schemas, and API routers relevant to the user's request. Never guess schemas or signatures.
3. **Receive User Prompt**: Receive the specific feature requirement directly from the user's message.

---

### Phase 2: Interactive Clarification (Grill-Me)

1. Conduct an interactive clarification session with the user before writing any feature code.
2. Ask clear, focused questions regarding:
   - Specific fields, data types, and constraints
   - Business logic and edge cases
   - Permission/authentication requirements
   - Preferred user interaction or API response formats
3. Use the `ask_question` tool or structured markdown questions to collect explicit choices from the user.

---

### Phase 3: Specification & Plan Sign-Off

1. Write a comprehensive specification and implementation plan.
2. The spec MUST document:
   - **Data Models**: DB tables, columns, data types, foreign keys, and indexes (SQLAlchemy 2.0 async).
   - **Pydantic Schemas**: Request/Response models, field validations, DTOs.
   - **API Endpoints**: HTTP methods, routes, status codes, query/body params.
   - **Files Created/Modified**: List exact file paths using markdown links (e.g. [app/models/feature.py](file:///c:/projects/bookstore-tabletop-cafe/app/models/feature.py)).
   - **Architectural Notes**: Highlight key design decisions so the user retains full codebase knowledge.
3. Present the plan to the user and **wait for explicit approval** before proceeding to implementation.

---

### Phase 4: Implementation

1. Follow FastAPI and SQLAlchemy best practices:
   - Write `async def` for endpoints and DB operations.
   - Use Pydantic models for validation and responses.
   - Follow project rules (e.g., `fastapi.md`, `sqlalchemy-postgres`).
2. **Restrictions**: Do NOT write *new* unit/E2E test files unless explicitly requested by the user.

---

### Phase 5: Automated Verification & Testing

Always execute existing codebase verification checks after implementing code changes:

1. **Ruff Linting**:
   ```bash
   uv run ruff check .
   ```
2. **Ruff Formatting**:
   ```bash
   uv run ruff format --check .
   ```
3. **Pytest Suite**:
   Execute the test suite with required test environment variables:
   ```bash
   $env:DATABASE_URL="sqlite:///./test.db"; $env:SECRET_KEY="test-secret"; $env:ACCESS_TOKEN_EXPIRE_MINUTES="60"; $env:JWT_ALGORITHM="HS256"; uv run python -m pytest
   ```
4. **Local GitHub Actions Workflow Runner (`act`)** (Optional / Full CI Emulation):
   If `act` and Docker are available, GitHub Actions workflows (`.github/workflows/`) can be emulated locally:
   ```bash
   act push          # Run all push workflows locally
   act -j ruff       # Run ruff lint/format workflow job
   act -j test       # Run pytest workflow job
   ```
5. **Report Failures**:
   - If any linter, formatter, or test fails, **report the exact failure logs to the user**.
   - Resolve and fix all underlying causes before declaring completion.

---

### Phase 6: Update CONTEXT.md

1. Upon completing implementation and verifying clean test results, update [CONTEXT.md](file:///c:/projects/bookstore-tabletop-cafe/CONTEXT.md).
2. Record:
   - Overview of the implemented feature
   - Added/modified database models and Pydantic schemas
   - New API endpoints and routes
   - Verification status (linter, formatter, pytest output summary)
   - Important architectural or setup instructions
