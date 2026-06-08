# Getting Started

This page provides a technical guide for setting up the **althara-news-service** development environment. It covers the transition from a clean system to a fully operational FastAPI server with a synchronized database and accessible News Studio UI.

## Environment Prerequisites

The service is built to run on **Python 3.11.9** [runtime.txt:1-1](). It relies on a PostgreSQL backend (specifically optimized for Neon) and uses `asyncio` for non-blocking database operations via `asyncpg`.

### Dependency Overview
The project manages its dependencies via `requirements.txt`. Key components include:
*   **Web Framework**: `fastapi` and `uvicorn` [requirements.txt:1-2]().
*   **ORM & Migrations**: `sqlalchemy` (with asyncio support) and `alembic` [requirements.txt:3-5]().
*   **Data Ingestion**: `feedparser`, `httpx`, and `beautifulsoup4` [requirements.txt:9-11]().
*   **Configuration**: `pydantic-settings` for environment variable management [requirements.txt:8]().

**Sources:** [requirements.txt:1-16](), [runtime.txt:1-1](), [README.md:132-137]()

---

## Local Setup Workflow

To initialize the project locally, follow the sequence below to ensure the database schema and environment variables are correctly aligned.

### 1. Virtual Environment and Installation
```bash
# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables (`.env`)
Create a `.env` file in the root directory. The application uses `pydantic-settings` to load these values.

| Variable | Requirement | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | **Required** | Must use the `postgresql+asyncpg://` scheme. [README.md:165-166]() |
| `INGEST_TOKEN` | Optional | Bearer token for authenticating admin ingestion endpoints. |
| `UI_USER` | Optional | Username for News Studio Basic Auth. |
| `UI_PASS` | Optional | Password for News Studio Basic Auth. |

**Database URL Normalization**: The system automatically converts standard `postgresql://` URLs (like those copied from the Neon dashboard) to `postgresql+asyncpg://` and strips incompatible SSL parameters to ensure compatibility with the `asyncpg` driver [README.md:168-172]().

### 3. Database Migrations
The project uses Alembic for asynchronous migrations. The configuration in `alembic.ini` points to the `alembic/` directory [alembic.ini:3-5](), and `env.py` is configured to use an async engine [README.md:43-43]().

```bash
# Apply all migrations to the database
alembic upgrade head
```

**Sources:** [README.md:108-124](), [README.md:155-180](), [alembic.ini:1-13]()

---

## Starting the Service

Once the database is migrated, start the FastAPI server using `uvicorn`.

```bash
uvicorn app.main:app --reload
```

### Access Points
*   **REST API**: `http://localhost:8000/api`
*   **Interactive API Docs (Swagger)**: `http://localhost:8000/docs` [README.md:237-237]()
*   **News Studio UI**: `http://localhost:8000/ui` [README.md:128-128]()

**Sources:** [README.md:122-128](), [README.md:199-210]()

---

## System Initialization Logic

The following diagram illustrates the relationship between the environment configuration, the Python runtime entities, and the resulting service availability.

### Setup and Initialization Flow
```mermaid
graph TD
    subgraph ["Environment Space"]
        ENV[".env file"]
        DB_URL["DATABASE_URL"]
        RT["runtime.txt (Python 3.11.9)"]
    end

    subgraph ["Code Entity Space"]
        CFG["app.config.Settings"]
        ALM["alembic.env:run_migrations_online"]
        APP["app.main:app (FastAPI)"]
        DB_ENG["app.database:engine (AsyncEngine)"]
    end

    ENV --> CFG
    DB_URL --> CFG
    RT --> APP
    CFG --> DB_ENG
    DB_ENG --> ALM
    ALM --> |"Schema Creation"| DB[("Neon PostgreSQL")]
    APP --> |"Dependency Injection"| DB_ENG
```
**Sources:** [app/config.py:1-20](), [app/database.py:1-15](), [app/main.py:1-10](), [README.md:155-180]()

---

## Deployment Configuration

The service is pre-configured for deployment on **Render.com** using the `render.yaml` specification.

### Render Build & Start Pipeline
The deployment process automates the environment setup and migration execution.

```mermaid
graph LR
    subgraph ["Build Phase"]
        B1["pip install --upgrade pip"]
        B2["pip install -r requirements.txt"]
        B3["alembic upgrade head"]
    end

    subgraph ["Runtime Phase"]
        S1["uvicorn app.main:app"]
        S2["PORT environment variable"]
    end

    B1 --> B2
    B2 --> B3
    B3 --> S1
    S2 -.-> |"Injected into"| S1
```

### Deployment Commands
*   **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt && alembic upgrade head` [render.yaml:5-5]()
*   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` [render.yaml:6-6]()

**Sources:** [render.yaml:1-10](), [build.sh:1-16](), [README.md:181-195]()

---
