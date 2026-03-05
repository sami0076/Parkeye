# Checkpoint — 2026-03-01

Context document for resuming Claude Code sessions on the `parkeye_frontend` repo.

---

## What This Project Is

**ParkEye** — native iOS app (Swift + SwiftUI) for GMU parking.
- Connects to a **FastAPI backend** (separate repo, not present here)
- Authenticates via **Supabase Auth** (JWT stored in iOS Keychain automatically)
- No local database of any kind — all state lives in Supabase/backend

---

## Current State

### What's done (as of this checkpoint)
- Xcode project created, boilerplate stripped, **Core Data fully removed**
- `supabase-swift` SPM package added to the `parkeye` target (Auth, PostgREST, Realtime, Storage, Functions — version ≥ 2.5.1)
- Static `Info.plist` wired up (`GENERATE_INFOPLIST_FILE = NO`, `INFOPLIST_FILE = Info.plist`)
- `Info.plist` is **gitignored** — each dev copies `Info.plist.example` → `Info.plist` and fills in 4 keys
- `.gitignore` in place (Info.plist, xcuserdata, DerivedData, .DS_Store)
- `CLAUDE.md` in place with build commands, architecture, bootstrap checklist
- **Build verified:** `xcodebuild … -destination 'platform=iOS Simulator,name=iPhone 17' build` → `BUILD SUCCEEDED`
- Committed and pushed to `origin/main` (commit `454c7fc`)

### What does NOT exist yet
Every feature file is missing — the app currently shows `Text("ParkEye")`. Nothing in:
- `parkeye/App/` (except `parkeyeApp.swift` stub)
- `parkeye/Models/`
- `parkeye/Features/`
- `parkeye/Services/`
- `parkeye/Network/`
- `parkeye/Core/`
- `parkeye/Resources/` (no `LotData.geojson` yet)

---

## Repo Layout

```
parkeye_frontend/
├── .gitignore
├── CLAUDE.md                  ← instructions for Claude Code
├── Info.plist                 ← LOCAL ONLY (gitignored) — real credentials
├── Info.plist.example         ← committed template with placeholders
├── plan.md                    ← week 1 feature plan
├── parkeye/                   ← Xcode FileSystemSynchronizedRootGroup (all .swift files auto-included)
│   ├── parkeyeApp.swift       ← @main stub, shows Text("ParkEye")
│   └── Assets.xcassets/
└── parkeye.xcodeproj/
    ├── project.pbxproj        ← supabase-swift linked, INFOPLIST_FILE = Info.plist
    └── project.xcworkspace/
        └── xcshareddata/swiftpm/Package.resolved
```

---

## Info.plist Keys (all required before building)

| Key | Description |
|-----|-------------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase public anon key |
| `API_BASE_URL` | FastAPI base URL — `http://localhost:8000` in dev |
| `WS_BASE_URL` | WebSocket base URL — `ws://localhost:8000` in dev |

---

## Build Commands

```bash
# Must set DEVELOPER_DIR if xcode-select points to CommandLineTools
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
  /Applications/Xcode.app/Contents/Developer/usr/bin/xcodebuild \
  -project parkeye.xcodeproj \
  -scheme parkeye \
  -destination 'platform=iOS Simulator,name=iPhone 17' \
  build
```

> No iPhone 16 simulator is installed on this machine — use iPhone 17.

---

## Architecture (target — nothing built yet)

**Data flow:** Views → ViewModels → Services → `APIClient` / `SupabaseClient`

**Key patterns:**
- State management: `@Observable` (not `ObservableObject`) + `@StateObject`
- Compiler default: `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` — everything is MainActor unless opted out
- Models: plain `Codable` structs mirroring backend JSON, in `parkeye/Models/`
- Auth: Supabase SDK auto-stores JWT in Keychain; `APIClient` reads `supabase.auth.session?.accessToken` and injects `Authorization: Bearer`
- Live occupancy: WebSocket at `ws://.../ws/occupancy` → `AsyncStream` → SwiftUI; falls back to 30s `GET /lots` poll
- Map: `MKMapView` + `MKPolygon` overlays (NOT Google/Apple Maps SDK)
- Charts: Swift Charts (occupancy history)
- GMU SSO: mocked (`MockGMUAuthService`, hardcoded session)
- No Core Data, no SwiftData, no SQLite

---

## Key API Endpoints

| Endpoint | Method | Consumer |
|----------|--------|----------|
| `/lots` | GET | MapViewModel — initial load + poll fallback |
| `/lots/{id}` | GET | LotDetailSheet |
| `/lots/{id}/history` | GET | OccupancyHistoryChart |
| `/lots/{id}/floors` | GET | DeckViewModel |
| `/predictions/{lot_id}` | GET | LotDetailSheet |
| `/recommendations` | GET | HomeViewModel |
| `/events` | GET | LotDetailSheet + MapViewModel |
| `/feedback` | POST | FeedbackViewModel |
| `/admin/lots/{id}/status` | PATCH | LotStatusEditorViewModel (admin only) |
| `ws://.../ws/occupancy` | WS | WebSocketClient → MapViewModel |

---

## Week 1 Priorities

See `plan.md` for the day-by-day breakdown. TL;DR:
1. **Day 1:** Core plumbing — AppState, SupabaseClient setup, auth flow, APIClient, `GET /lots` displaying in a list
2. **Day 2:** MKMapView with polygon overlays from `LotData.geojson`
3. **Day 3:** WebSocket live occupancy
4. **Day 4:** Lot detail sheet + occupancy history chart
5. **Day 5:** Home view + recommendations
6. **Day 6:** Auth polish (WelcomeView, MockGMU, PermissionsView, LocationService)
7. **Day 7:** Feedback, Profile, MainTabView wire-up, smoke test

---

## Notes for New Session

- When starting a new session, read `CLAUDE.md` first — it has build commands, architecture summary, and the bootstrap checklist (already complete)
- The `parkeye/` directory is a `PBXFileSystemSynchronizedRootGroup` — **any `.swift` file you create inside it is automatically compiled**; no need to touch `project.pbxproj` for new source files
- `Info.plist` lives at the project root (not inside `parkeye/`) to avoid being bundled as a resource by the synced group
- Supabase-swift products available: `import Auth`, `import PostgREST`, `import Realtime`, `import Storage`, `import Functions` — or just `import Supabase` for all
