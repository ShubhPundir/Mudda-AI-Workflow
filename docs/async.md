# Asynchronous Backend Architecture

This document outlines the asynchronous architecture implemented in the Mudda AI Workflow backend to ensure high performance and scalability.

## Overview

The backend is built using **FastAPI** and **SQLAlchemy** with `async/await` support throughout the stack. This allows the application to handle multiple concurrent requests efficiently, especially during I/O-bound operations like database queries and external AI service calls.

## Core Components

### 1. Database Session (`backend/sessions/database.py`)

- **Engine**: Uses `create_async_engine` with `postgresql+asyncpg` driver.
- **Session**: Uses `AsyncSession` managed by `async_sessionmaker`.
- **Dependency**: The `get_db` dependency yields an `AsyncSession` to be used in routers.

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(DATABASE_URL)
# ...
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
```

### 2. Services (`backend/services/`)

All service methods are defined as `async def` and await asynchronous operations.

- **ComponentService**: Uses `await db.execute(select(...))` for non-blocking database queries.
- **WorkflowService**: Awaits `AIService` methods and database operations.
- **AIService**: Wraps blocking Gemini AI calls in `loop.run_in_executor` via `gemini_client.generate_async`.

### 3. Routers (`backend/routers/`)

Routers are defined as `async def` endpoints and inject the `AsyncSession` dependency.

```python
@router.get("/components")
async def list_components(db: AsyncSession = Depends(get_db)):
    return await ComponentService.list_components(db)
```

## Developer Guidelines

When adding new features:

1.  **Always use `async def`** for route handlers and service methods.
2.  **Use `await`** for all database interactions and external API calls.
3.  **Use `select()` syntax** for SQLAlchemy queries (legacy `query()` style is synchronous).
    *   *Correct*: `result = await db.execute(select(Model).filter(...))`
    *   *Incorrect*: `result = db.query(Model).filter(...)`
4.  **Await commits and flushes**: `await db.commit()`, `await db.refresh(obj)`.

## Initialization

Database tables are created asynchronously during application startup using the `lifespan` event handler in `main.py`.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
```
