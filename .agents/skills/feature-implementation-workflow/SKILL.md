---
name: feature-implementation-workflow
description: Guided feature implementation workflow to prevent codebase knowledge debt, eliminate hallucinations, clarify user intent, obtain plan sign-off, and update CONTEXT.md. Use whenever implementing features, creating endpoints, modifying data models, or when the user asks to build or extend functionality.
---

# Feature Implementation Workflow

This skill enforces a structured, interactive 5-phase process for implementing features in the codebase. It ensures high technical quality, prevents agent hallucinations, avoids "codebase knowledge debt" by keeping the user informed of architectural decisions, and maintains `CONTEXT.md`.

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
│ 4. Implementation       │  Write clean async FastAPI/SQLAlchemy code (no auto tests)
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 5. Update CONTEXT.md    │  Document new structures & architecture in CONTEXT.md
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
2. **Restrictions**: Do NOT write unit/E2E tests unless explicitly requested by the user.

---

### Phase 5: Update CONTEXT.md

1. Upon completing the feature implementation, update [CONTEXT.md](file:///c:/projects/bookstore-tabletop-cafe/CONTEXT.md).
2. Record:
   - Overview of the implemented feature
   - Added/modified database models and Pydantic schemas
   - New API endpoints and routes
   - Important architectural or setup instructions
