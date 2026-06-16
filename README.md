# AI Interview Practice Platform

A production-ready FastAPI backend for practicing technical interviews with AI-generated questions, AI-assisted answer evaluation, analytics, JWT authentication, Redis caching support, Alembic migrations, Docker, PDF reports, and pytest coverage.

## Architecture

The project follows Clean Architecture with thin API controllers, service-layer business rules, repository-pattern persistence, dependency injection through FastAPI dependencies, and isolated infrastructure integrations.

## File Purposes

| File | Purpose |
| --- | --- |
| `app/main.py` | FastAPI app factory, middleware, health check, Swagger/OpenAPI setup, and router registration. |
| `app/api/dependencies.py` | Dependency injection providers for repositories, services, AI provider selection, auth, cache, and role guards. |
| `app/api/v1/router.py` | Composes versioned API routers. |
| `app/api/v1/endpoints/auth.py` | Register, login, refresh token, and current-user endpoints. |
| `app/api/v1/endpoints/interviews.py` | Interview session creation/list/detail and answer submission endpoints. |
| `app/api/v1/endpoints/analytics.py` | User analytics summary endpoint. |
| `app/api/v1/endpoints/reports.py` | PDF interview report endpoint. |
| `app/core/config.py` | Environment-driven settings using Pydantic Settings. |
| `app/core/security.py` | Password hashing and JWT creation/validation helpers. |
| `app/core/exceptions.py` | Domain exceptions and global exception handlers. |
| `app/core/logging.py` | Structured console logging configuration. |
| `app/database/base.py` | SQLAlchemy declarative base. |
| `app/database/session.py` | Async SQLAlchemy engine/session and DB dependency. |
| `app/models/enums.py` | User, interview role, and interview status enums. |
| `app/models/user.py` | User ORM model. |
| `app/models/interview.py` | InterviewSession, Question, Answer, Evaluation, and Analytics ORM models. |
| `app/repositories/user_repository.py` | User persistence operations. |
| `app/repositories/interview_repository.py` | Interview, question, answer, evaluation, and analytics persistence operations. |
| `app/schemas/*.py` | Pydantic request/response validation schemas. |
| `app/services/auth_service.py` | Registration, login, and refresh-token business logic. |
| `app/services/interview_service.py` | Interview creation and answer evaluation workflow. |
| `app/services/analytics_service.py` | Aggregate scoring, trends, and skill breakdown calculations. |
| `app/services/ai_service.py` | OpenAI, Gemini, and mock AI provider abstraction. |
| `app/services/cache_service.py` | Redis JSON cache wrapper with graceful failure handling. |
| `app/services/report_service.py` | ReportLab PDF generation. |
| `alembic/env.py` | Alembic runtime configuration. |
| `alembic/versions/202606160001_initial_schema.py` | Initial database migration. |
| `Dockerfile` | API container image. |
| `docker-compose.yml` | API, Postgres, and Redis local stack. |
| `requirements.txt` | Python runtime and test dependencies. |
| `tests/*.py` | Async endpoint tests for authentication and interview workflow. |

## Run Locally With Docker

1. Create an environment file:

```bash
cp .env.example .env
```

2. Start the stack:

```bash
docker compose up --build
```

3. Open Swagger documentation:

```text
http://localhost:8000/docs
```

The default `AI_PROVIDER=mock` makes the platform fully usable without external API keys. Set `AI_PROVIDER=openai` with `OPENAI_API_KEY`, or `AI_PROVIDER=gemini` with `GEMINI_API_KEY`, to use a real model.

## Run Without Docker

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

For non-Docker local Postgres, update `DATABASE_URL`, `SYNC_DATABASE_URL`, and `REDIS_URL` in `.env`.

## Run Tests

```bash
pytest
```

Tests use SQLite and the mock AI provider, so they do not require Postgres, Redis, OpenAI, or Gemini.

## Main API Flow

1. `POST /api/v1/auth/register`
2. `POST /api/v1/auth/login`
3. Use the returned bearer token.
4. `POST /api/v1/interviews`
5. `POST /api/v1/interviews/questions/{question_id}/answers`
6. `GET /api/v1/analytics/summary`
7. `GET /api/v1/reports/interview.pdf`
