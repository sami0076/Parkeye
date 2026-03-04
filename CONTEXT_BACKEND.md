What We Are Building (MVP Scope)
The MVP backend is a single FastAPI service connected to Supabase (PostgreSQL). It serves mock parking data to the iOS app so every frontend screen works end-to-end for the demo. There is no live data ingestion, no ML training pipeline, and no complex infrastructure — just a clean REST API and a WebSocket feed powered by pre-seeded mock data.

What is NOT in the MVP:
Live GPS / telemetry ingestion from real users
Real ML model training (predictions use simple table look-ahead instead)
Weather or other external API integrations
APNs push notifications (admin changes surface via WebSocket only for demo)
Redis caching layer
Analytics dashboards

Tech Stack
Layer
Choice
Why for MVP
Language
Python 3.12
FastAPI ecosystem; easy to bolt on real ML later
Framework
FastAPI
Auto-generates docs, fast to build, Pydantic validation built in
Database
Supabase (PostgreSQL)
Free hosted Postgres + built-in Auth + easy dashboard to inspect seeded data
Auth
Supabase Auth (JWT)
Handles GMU OAuth and Google OAuth; backend just verifies the JWT
WebSocket
FastAPI WebSocket
Streams mock occupancy to the iOS map every 30 seconds
Mock Data
JSON/CSV files + seed.py
Populates DB on startup; no live feeds needed for demo
Hosting
Render.com (free tier)
Zero-config Docker deploy; free for demo-level traffic
Local Dev
docker-compose
FastAPI + Postgres running locally in one command



Project File Structure
Deliberately flat and small. No unnecessary layers for the MVP.

parkeye-backend/
├── app/
│   ├── main.py              # FastAPI app init, router registration, CORS
│   ├── config.py            # Settings loaded from .env
│   ├── database.py          # Supabase client + async SQLAlchemy session
│   ├── auth.py              # JWT decode helper, get_current_user dependency
│   │
│   ├── models/              # SQLAlchemy ORM table definitions
│   │   ├── lot.py           # Lot: id, name, capacity, permit_types, lat, lon, status
│   │   ├── occupancy.py     # OccupancySnapshot: lot_id, hour_of_day, day_of_week, pct, color
│   │   ├── event.py         # CampusEvent: title, start, end, affected_lots
│   │   └── feedback.py      # Feedback: lot_id, accuracy_rating, experience_rating, note
│   │
│   ├── schemas/             # Pydantic request/response shapes
│   │   ├── lot.py           # LotResponse, LotListResponse
│   │   ├── occupancy.py     # OccupancyResponse, PredictionResponse
│   │   ├── feedback.py      # FeedbackCreate
│   │   └── recommendations.py  # RecommendationResponse
│   │
│   ├── routers/             # One file per feature area
│   │   ├── lots.py          # GET /lots, GET /lots/{id}, GET /lots/{id}/history
│   │   ├── predictions.py   # GET /predictions/{lot_id}
│   │   ├── recommendations.py  # GET /recommendations
│   │   ├── events.py        # GET /events
│   │   ├── feedback.py      # POST /feedback
│   │   ├── admin.py         # PATCH /admin/lots/{id}/status
│   │   └── websocket.py     # ws://.../ws/occupancy
│   │
│   └── services/            # Business logic (thin layer for MVP)
│       ├── occupancy.py     # Fetch current occupancy from snapshot table
│       ├── prediction.py    # Rule-based look-ahead (no real ML)
│       └── recommendation.py   # Rank lots by predicted pct + walk distance
├── mock/                    # All mock data lives here
│   ├── lots.json            # 10 GMU lots: coords, capacity, permit types
│   ├── occupancy_history.csv  # Synthetic hourly occupancy (24h x 7 days x 10 lots)
│   ├── events.json          # ~20 campus events with affected lot IDs
│   └── seed.py              # Run once: loads all mock files into Supabase
├── tests/
│   └── test_api.py          # Smoke tests for every endpoint
├── .env                     # Secrets — NEVER commit to GitHub
├── Dockerfile
├── docker-compose.yml       # Local: FastAPI + Postgres
├── requirements.txt
└── README.md


Database Schema (4 Tables)
Minimal schema — only what the iOS app actually needs for the demo.

lots
Column
Type
Notes
id
UUID (PK)
Auto-generated
name
TEXT
e.g. Lot K, Parking Deck 1
capacity
INT
Total spaces
permit_types
TEXT[]
e.g. [general, west_campus]
lat
FLOAT
Centroid latitude
lon
FLOAT
Centroid longitude
is_deck
BOOL
True if multi-floor
floors
INT
Floor count (decks only, else null)
status
TEXT
open | limited | closed
status_until
TIMESTAMPTZ
Expiry of admin override (null = no expiry)
status_reason
TEXT
Admin note shown to users


occupancy_snapshots
Pre-populated from mock/occupancy_history.csv on seed. The WebSocket loop and prediction service read rows matching the current hour_of_day + day_of_week to simulate live data without any real feeds.
Column
Type
Notes
id
BIGINT (PK)
Auto-increment
lot_id
UUID (FK)
References lots.id
hour_of_day
INT
0 to 23
day_of_week
INT
0 = Monday through 6 = Sunday
occupancy_pct
FLOAT
0.0 to 1.0
color
TEXT
green | yellow | red 



campus_events
Column
Type
Notes
id
UUID (PK)


title
TEXT
e.g. Basketball vs. VCU
start_time
TIMESTAMPTZ


end_time
TIMESTAMPTZ


impact_level
TEXT
low | medium | high
affected_lots
UUID[]
Lot IDs expected to be impacted


feedback
Column
Type
Notes
id
UUID (PK)


user_id
UUID
From Supabase Auth JWT (nullable for guests)
lot_id
UUID (FK)


accuracy_rating
INT
1 to 5 stars
experience_rating
INT
1 to 5 stars
note
TEXT
Optional free text from user
created_at
TIMESTAMPTZ
Auto-set on insert



API Endpoints

Lots
Method
Path
What it returns
GET
/lots
All lots with current occupancy_pct, color badge, and admin status
GET
/lots/{id}
Single lot: occupancy, permit types, status, upcoming events affecting it
GET
/lots/{id}/history
Hourly occupancy for past 7 days (powers the detail screen graph)
GET
/lots/{id}/floors
Per-floor occupancy breakdown for parking decks


Predictions (Rule-Based Look-Ahead, No ML)
Predictions fetch occupancy_snapshots rows for hour+1 and hour+2 on the same day_of_week. No model file, no inference — just a table lookup dressed up as a prediction. Confidence is always labeled as 'Estimated from historical patterns' for honesty.
Method
Path
What it returns
GET
/predictions/{lot_id}
{ t15: { pct, color }, t30: { pct, color }, note: 'Estimated from historical patterns' }


Recommendations
Filters lots by permit type, fetches predicted occupancy at arrival_hour, adds a +20% bump for lots affected by events in the arrival window, then ranks by occupancy ascending and distance to main campus (Johnson Center). No ML — pure logic on the snapshot table.
Method
Path
Query Params
GET
/recommendations
permit_type, dest_lat, dest_lon, arrival_time (ISO 8601), duration_min


Events, Feedback, Admin
Method
Path
Notes
GET
/events
Upcoming campus events for next 7 days
POST
/feedback
Body: { lot_id, accuracy_rating, experience_rating, note? }
PATCH
/admin/lots/{id}/status
Body: { status, status_until?, status_reason? } — requires admin JWT claim


WebSocket
Path
Behavior
ws://.../ws/occupancy
Every 30 seconds, broadcasts JSON array of { lot_id, occupancy_pct, color } for all lots. Reads occupancy_snapshots row matching current hour/day. Admin status overrides are reflected automatically. iOS map colors update on each message.


Mock Data Layer
This is the heart of the MVP backend. All API responses are backed by data seeded from three files. Switching to live data later only requires changing what writes to occupancy_snapshots — not any API or schema changes.

mock/lots.json
10 GMU parking lots and decks. Each entry: id, name, capacity, permit_types (array), lat, lon, is_deck, floors. Coordinates are real GMU lot centroids from Google Maps.

mock/occupancy_history.csv
Synthetic hourly occupancy per lot covering all 24 hours x 7 days. Generated with a sinusoidal curve peaking 9-11 AM on weekdays, low on weekends, plus gaussian noise. Columns: lot_id, hour_of_day, day_of_week, occupancy_pct. This one file powers current occupancy, history graphs, and predictions.

Occupancy generation formula:
# For each (lot, hour, day_of_week):
base = sin_curve(hour, peak=10, trough=3)   # peaks 10 AM, troughs 3 AM
weekend_factor = 0.4 if day_of_week >= 5 else 1.0
noise = random.gauss(0, 0.05)
occupancy_pct = clamp(base * weekend_factor + noise, 0.0, 1.0)
color = 'green' if pct < 0.6 else 'yellow' if pct < 0.85 else 'red'

mock/events.json
~20 campus events (basketball games, graduation, finals) with start/end times and affected lot IDs. Events within 2 hours of a requested arrival time bump predicted occupancy for affected lots by +20% in the recommendations logic.

mock/seed.py
Run once on setup. Reads all three mock files and inserts into Supabase via the Python client. Idempotent — skips rows that already exist by checking lot name, so it is safe to re-run.
python mock/seed.py


Services Layer (Thin MVP Versions)
Three small files. No ML, no external calls — just logic on top of the DB.

services/occupancy.py — get_current_occupancy(lot_id)
Queries occupancy_snapshots for the row matching lot_id + current hour_of_day + current day_of_week. If an admin override is active (status = closed), returns 1.0 / red regardless of the snapshot value.

services/prediction.py — get_prediction(lot_id)
Fetches occupancy_snapshots rows for hours t+1 and t+2 for the same lot and day_of_week. Returns { t15: { pct, color }, t30: { pct, color }, note: 'Estimated from historical patterns' }. No model file, no inference. Just a table look-ahead.

services/recommendation.py — get_recommendations(...)
Inputs: permit_type, dest_lat, dest_lon, arrival_time, duration_min. Steps: (1) filter lots by permit_types, (2) fetch predicted occupancy at arrival_hour, (3) apply +20% event bump for affected lots, (4) compute haversine distance to destination, (5) sort by pct ascending. Returns top 5 lots each with predicted_pct, color, walk_minutes, and a confidence label.

Auth (Supabase JWT)
Supabase Auth handles GMU OAuth and Google OAuth entirely. The iOS app receives a JWT from Supabase directly after login. Every API call sends this JWT as Authorization: Bearer. The backend decodes it with the Supabase JWT secret and extracts user_id and role. No custom auth logic needed.

# app/auth.py — one dependency used by all protected routes
async def get_current_user(token = Depends(oauth2_scheme)):
    payload = jwt.decode(token, settings.SUPABASE_JWT_SECRET)
    return User(id=payload['sub'], role=payload.get('role', 'user'))

Admin endpoints check role == 'admin'. Admin users are set manually in the Supabase dashboard before the demo.


Division of Labor

Shabeer — API & Database
Supabase project setup: create the 4 tables, set RLS policies
models/ and database.py
routers/lots.py, routers/admin.py, routers/feedback.py, routers/events.py
routers/websocket.py — 30-second broadcast loop
auth.py JWT middleware
docker-compose.yml for local dev
Deployment to Render.com

Sami — Mock Data & Intelligence
Generate mock/occupancy_history.csv using the formula above
Compile mock/lots.json (real GMU coordinates from Google Maps)
Compile mock/events.json (~20 campus events)
Write mock/seed.py
services/occupancy.py, services/prediction.py, services/recommendation.py
routers/predictions.py, routers/recommendations.py
tests/test_api.py — smoke test for every endpoint

Shared (Day 1 Priority)
schemas/ — agree on all Pydantic response shapes before either person writes a router
README with local setup instructions
Integration testing with iOS team in Weeks 2-3


4-Week Build Schedule

Week
Shabeer
Sami
Together
1
Supabase tables + RLS. /lots GET returning seeded data. docker-compose running locally.
Generate all mock files. Write and run seed.py against Shabeer's DB.
Agree on all Pydantic schemas on Day 1. iOS can hit /lots by end of week.
2
/lots/{id}, /lots/{id}/history, /lots/{id}/floors. Auth middleware. Admin PATCH status.
services/occupancy.py + prediction.py. Wire up /predictions endpoint.
iOS map screen pulling real (mock) data. Verify JSON shapes match frontend expectations.
3
WebSocket hub — 30-second occupancy broadcast. /feedback POST. /events GET.
services/recommendation.py. /recommendations endpoint. Tune event bump logic.
Full user flow demo-able end to end: home screen to map to lot detail to prediction to feedback.
4
Deploy to Render.com with HTTPS. Final bug fixes and README polish.
Smoke tests for all endpoints. Seed data tuned for demo time window.
Full dry-run of demo script against production URL. iOS app points to prod.

Not yet done from Shabeer's Week 2 scope:
app/auth.py -- JWT middleware (not present)
app/routers/lots.py -- GET /lots/{id}, /lots/{id}/history, /lots/{id}/floors (not present)
app/routers/admin.py -- PATCH /admin/lots/{id}/status (not present)


Data Flow

How the iOS Map Gets Its Data
iOS App connects to ws://.../ws/occupancy on launch


Backend (every 30 seconds):
  SELECT * FROM occupancy_snapshots
  WHERE hour_of_day = current_hour
    AND day_of_week = current_day
  Apply admin overrides (status = 'closed' -> color = 'red')
  Broadcast JSON array to all connected iOS clients


iOS map colors update on each message received

How Recommendations Work
GET /recommendations?permit_type=general&dest_lat=38.83&arrival_time=2026-03-01T10:00
  1. Filter lots WHERE permit_types contains 'general'
  2. For each lot: fetch occupancy_snapshots WHERE hour = 10, day = Saturday
  3. Check campus_events overlapping arrival window:
     affected lots get occupancy_pct += 0.20
  4. Compute haversine(lot.lat, lot.lon, dest_lat, dest_lon) -> walk_minutes
  5. Sort by occupancy_pct ASC -> return top 5

How Admin Status Overrides Work
Admin: PATCH /admin/lots/{id}/status
  { status: 'closed', status_reason: 'Construction until 5pm' }


  -> Update lots.status in DB
  -> Next WebSocket broadcast (within 30s) picks up the change
  -> iOS map refreshes automatically, no push notification needed for demo


Setup & Environment

.env Variables
Variable
Description
SUPABASE_URL
Your Supabase project URL
SUPABASE_KEY
Supabase service role key (never exposed to the iOS app)
SUPABASE_JWT_SECRET
From Supabase dashboard: Settings > API > JWT Secret
DATABASE_URL
postgres://... async connection string for SQLAlchemy
ALLOWED_ORIGINS
CORS origins: iOS app scheme + localhost for local dev
ENV
development | production


Local Dev (One Command)
git clone https://github.com/parkeye/parkeye-backend
cd parkeye-backend
cp .env.example .env          # fill in your Supabase keys
docker-compose up             # starts FastAPI + Postgres
python mock/seed.py           # load mock data (run once)
# API live at  http://localhost:8000
# Auto-docs at http://localhost:8000/docs

Requirements (Minimal)
Package
Purpose
fastapi
Web framework
uvicorn
ASGI server
supabase
Supabase Python client (used in seed.py)
sqlalchemy + asyncpg
Async DB access for all routers
pydantic
Request/response validation
python-jose
JWT decode for auth middleware
httpx
Async HTTP client (used in tests)
pytest
Testing


Key Risks & Mitigations
Risk
Mitigation
Mock occupancy looks unconvincing during demo
Tune seed data so the demo hour (e.g. 10 AM Tuesday) shows a realistic mix of green/yellow/red across lots
WebSocket adds complexity in Week 1
Start with a polling fallback: iOS calls GET /lots every 30 seconds. Add WebSocket in Week 3 once the rest is stable.
Supabase RLS accidentally blocks API calls
Use service role key server-side (bypasses RLS entirely). RLS only matters for direct browser/client queries.
iOS and backend disagree on JSON shapes
Lock Pydantic schemas on Day 1 and share as a spec. iOS mocks against it immediately so both teams can work in parallel.
Render deployment breaks the day before demo
Deploy to Render at end of Week 3. Demo against production from Week 4 onward, not localhost.

