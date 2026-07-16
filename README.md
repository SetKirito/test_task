# Backend Test API

This project is a FastAPI-based backend service for a developer landing page. It accepts contact submissions, stores them in PostgreSQL, runs AI sentiment analysis, logs requests/errors, sends email notifications (best-effort), and exposes health and metrics endpoints.

## Features

- REST API for contact submissions
- Input validation via Pydantic
- Layered architecture: API → Controller → Service → Repository → DB
- PostgreSQL persistence
- OpenAI-based sentiment/category analysis with graceful fallback
- SMTP email notifications with graceful fallback
- Request/error logging to files
- Docker Compose support
- CORS and rate limiting middleware
- OpenAPI documentation

## Stack

- Backend: Python 3.11, FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL
- AI: OpenAI API
- Infrastructure: Docker Compose, environment variables

## Project structure

- app/api — routers/endpoints
- app/controllers — controller layer
- app/services — business logic (AI, email, contact flow)
- app/repositories — database access layer
- app/models — SQLAlchemy models
- app/core — config, database, middleware, logging, exception handling

## Environment variables

Create a `.env` file with values similar to:

```env
DATABASE_URL=postgresql://backend:backend@db:5432/backend
POSTGRES_DB=backend
POSTGRES_USER=backend
POSTGRES_PASSWORD=backend

OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-3.5-turbo

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_SSL=false
OWNER_EMAIL=your_email@gmail.com
```

> Note: email and AI are best-effort integrations. If they are unavailable, creating a contact still succeeds and the request is stored in the database.

## Run with Docker

```bash
docker compose up -d --build
```

The API will be available at:

- http://127.0.0.1:8000/docs for Swagger UI
- http://127.0.0.1:8000/api/health
- http://127.0.0.1:8000/api/metrics

## Example requests

### Health check

```bash
curl http://127.0.0.1:8000/api/health
```

### Metrics

```bash
curl http://127.0.0.1:8000/api/metrics
```

### Create contact

```bash
curl -X POST http://127.0.0.1:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "user@example.com",
    "phone": "+79990001122",
    "comment": "Hello from Docker"
  }'
```

## API behavior

- `POST /api/contact` returns `201 Created` on success.
- Validation errors return `422`.
- Rate limiting returns `429` when the limit is exceeded.
- AI failures fall back to unknown/Other sentiment and do not break the request.
- SMTP failures are logged and do not break the request.

## Notes for reviewers

This project follows a layered structure and demonstrates a complete request lifecycle:

1. Request arrives at the FastAPI router
2. Controller orchestrates the call
3. Service performs business logic
4. Repository persists data in PostgreSQL
5. AI and email services are invoked with graceful fallback
6. Responses and errors are returned consistently
