# IncidentIQ

IncidentIQ is an AI-powered incident response platform that analyzes uploaded application logs, extracts evidence, reasons about root cause and cascade risk, and returns a structured incident report.

## Architecture

- React dashboard for log upload and incident lookup
- FastAPI backend for analysis and persistence
- Log parser for structured evidence extraction
- Incident builder for domain object creation
- Reasoning agent for root cause, impact, and recommendations
- PostgreSQL-backed persistence for incident history

## Backend

Path: `backend/`

Required environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `CORS_ORIGINS` - optional comma-separated list of allowed frontend origins

Run locally:

```bash
cd backend
uvicorn main:app --reload
```

Database migrations:

```bash
cd backend
.\venv\Scripts\alembic.exe upgrade head
```

Docker:

```bash
docker compose up --build
```

## Frontend

Path: `frontend/`

Optional environment variable:

- `VITE_API_BASE_URL` - backend base URL, defaults to `http://localhost:8000`

Run locally:

```bash
cd frontend
npm install
npm run dev
```

Docker:

```bash
docker build -t incidentiq-frontend ./frontend
```

## API

- `POST /analyze` - upload a log file and generate a structured incident report
- `GET /incident/{incident_id}` - retrieve a persisted incident report
- `GET /health` - health check
