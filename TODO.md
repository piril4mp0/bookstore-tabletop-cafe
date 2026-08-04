# Project TODOs

## Authentication & Security
- [x] Implement User system (customers and admins)
- [ ] Implement Refresh Token flow (`/auth/refresh`, `RefreshToken` model, token rotation)
- [ ] Implement Rate Limiting (Redis) on sensitive endpoints (`/auth/login`, `/books/import`)

## Models & Features
- [x] Change `Game` model to include stock control
- [x] Create book stock control (similar to the `Game` structure)
- [x] Create a table reservation system for customers to schedule gaming sessions
- [x] Implement Cafe Order System (`Orders` and `OrderItems` for table consummation)
- [ ] Implement Game Check-in/Check-out status tracking (in-game, returned, damaged)
- [ ] Implement pagination & Full-Text Search / filtering for books and games catalog
- [ ] Document all methods and classes

## Architecture & Refactoring
- [ ] Implement custom domain exceptions & global exception handlers
- [ ] Implement Redis caching for static/low-change endpoints (menu, games, operating hours)
- [ ] Implement background workers/tasks (reservation cleanup, email notifications, expired token pruning)

## Testing
- [x] Continue implementing unit & integration tests
- [ ] Implement E2E API tests

## DevOps, CI/CD & Documentation
- [x] Configure GitHub Actions and a CI/CD pipeline
- [x] Create `Dockerfile` & `docker-compose.yml` (FastAPI + Postgres + Redis)
- [x] Enrich OpenAPI/Swagger documentation with field examples and error responses