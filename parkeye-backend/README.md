# Parkeye Backend

FastAPI backend for the Parkeye parking availability app. Serves mock parking data to the iOS app for the MVP demo. Uses Supabase as the hosted PostgreSQL database.

## Tech Stack

- **Python 3.12** + FastAPI
- **Supabase** (hosted PostgreSQL)
- **SQLAlchemy** (async) for database access
- **Pydantic** for validation

## Setup

### 1. Clone and configure

```bash
cd parkeye-backend
cp .env.example .env
```

Edit `.env` with your Supabase credentials:
- `SUPABASE_URL` - from Supabase Dashboard → Settings → API
- `SUPABASE_KEY` - anon key from same page
- `SUPABASE_JWT_SECRET` - from Settings → API → JWT Secret
- `DATABASE_URL` - from **Connect button → Session pooler**, replace `postgresql://` with `postgresql+asyncpg://`

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Seed mock data

```bash
python mock/seed.py
```

### 4. Start the API

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. API docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/lots` | All lots with current occupancy |
| GET | `/lots/{id}` | Single lot + upcoming events |
| GET | `/lots/{id}/history` | Hourly occupancy for 7 days |
| GET | `/lots/{id}/floors` | Per-floor breakdown (decks only) |
| GET | `/predictions/{lot_id}` | t15/t30 occupancy prediction |
| GET | `/recommendations` | Top 5 lots (query: permit_type, dest_lat, dest_lon, arrival_time) |
| GET | `/events` | Upcoming campus events |
| POST | `/feedback` | Submit user feedback |
| PATCH | `/admin/lots/{id}/status` | Update lot status (admin only) |
| WS | `/ws/occupancy` | Real-time occupancy stream (every 30s) |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon key |
| `SUPABASE_JWT_SECRET` | JWT secret for auth |
| `DATABASE_URL` | Session pooler connection string (postgresql+asyncpg://...) |
| `ALLOWED_ORIGINS` | CORS origins (comma-separated) |
| `ENV` | development or production |

## Running Tests

```bash
pytest
```

## Docker

```bash
docker-compose up
```

## Deployment (Render.com)

1. Connect GitHub repo
2. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add environment variables from `.env`
