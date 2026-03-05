# Checkpoint — 2026-03-04

Context document for resuming Claude Code sessions. Records state after completing Days 1-7 of the frontend implementation plan.

---

## Project Summary

**ParkEye** — native iOS app (Swift + SwiftUI) for GMU parking.

| Layer | Choice |
|---|---|
| Language | Swift 5.10 |
| UI | SwiftUI + MapKit |
| Auth | Supabase (JWT in Keychain) |
| Networking | URLSession async/await |
| WebSocket | URLSessionWebSocketTask |
| State | `@Observable` + `@StateObject` |
| Charts | Swift Charts |
| SPM | supabase-swift only |

---

## Implementation Status

### Completed (Days 1-7)

All source code is written. The `parkeye/` directory uses Xcode's `PBXFileSystemSynchronizedRootGroup` — every `.swift` file placed inside is automatically compiled with no edits to `project.pbxproj` required.

#### App Shell & Auth
| File | Status |
|---|---|
| `App/parkeyeApp.swift` | Done — creates `SupabaseClient`, injects `AppState` |
| `App/AppState.swift` | Done — owns all ViewModels and services, `hasCompletedOnboarding` in UserDefaults |
| `App/RootView.swift` | Done — routes: unauthenticated → `WelcomeView`; auth + no onboarding → `PermissionsView`; auth + onboarded → `MainTabView` |
| `Features/Auth/AuthViewModel.swift` | Done — `signIn()`, `signUp()`, `signOut()` via Supabase SDK |
| `Features/Auth/WelcomeView.swift` | Done — branding + 3 nav buttons (Sign In / Create Account / GMU SSO) |
| `Features/Auth/SignInView.swift` | Done — email + password fields, no "Create Account" link (moved to WelcomeView) |
| `Features/Auth/SignUpView.swift` | Done — confirm password validation |
| `Features/Auth/MockGMULoginView.swift` | Done — fake CAS screen, submits hardcoded `demo@gmu.edu / demo123456` |
| `Features/Auth/PermissionsView.swift` | Done — Allow / Skip buttons, auto-continues on grant via `onChange` |

#### Services & Networking
| File | Status |
|---|---|
| `Network/APIError.swift` | Done |
| `Network/APIEndpoints.swift` | Done — `lots`, `lot(id:)`, `lotHistory(id:)`, `predictions(lotId:)`, `recommendations(permit:)`, `feedback`, `wsOccupancy` |
| `Network/APIClient.swift` | Done — `get`, `post`, `postVoid`; snake_case decode/encode; ISO8601 dates; Bearer token injection |
| `Network/WebSocketClient.swift` | Done — `actor`; `AsyncStream<[OccupancyUpdate]>`; 5s reconnect backoff |
| `Services/ParkingService.swift` | Done — `fetchLots`, `fetchLotDetail`, `fetchLotHistory`, `fetchPredictions`, `fetchRecommendations`, `submitFeedback` |
| `Services/LocationService.swift` | Done — `@Observable NSObject` wrapping `CLLocationManager`; delegate methods `nonisolated`, dispatching to `@MainActor` |

#### Map (Days 2-4)
| File | Status |
|---|---|
| `Models/Lot.swift` | Done — `Codable, Identifiable` |
| `Models/OccupancyUpdate.swift` | Done |
| `Models/OccupancyHistory.swift` | Done — `Codable, Identifiable`, `timestamp: Date` |
| `Models/Prediction.swift` | Done — `minutesAhead`, `predictedOccupancyPct`, `predictedColor` |
| `Features/Map/MapViewModel.swift` | Done — `loadLots()`, `connectLiveOccupancy()` (WebSocket stream + poll fallback), `selectLot(id:)`, `clearSelection()` |
| `Features/Map/ParkeyeMapView.swift` | Done — `UIViewRepresentable` wrapping `MKMapView`; polygon overlays from `LotData.geojson`; `UITapGestureRecognizer` with simultaneous recognition; hit-tests polygons via `renderer.path.contains` |
| `Features/Map/MapOverlayRenderer.swift` | Done — `LotPolygonRenderer: MKPolygonRenderer` |
| `Features/Map/LotDetailViewModel.swift` | Done — parallel `async let` fetch (lot + history + predictions) |
| `Features/Map/LotDetailSheet.swift` | Done — `OccupancyIndicator`, `PredictionChip`, `OccupancyHistoryChart`; `.presentationDetents([.medium, .large])` |
| `Features/Map/OccupancyHistoryChart.swift` | Done — Swift Charts `LineMark` + `AreaMark`, `.catmullRom`, Y-axis 0-100% |
| `Features/Map/MainTabView.swift` | Done — 4 tabs wired; `.task` for `loadLots` + `connectLiveOccupancy`; `.sheet(item:)` for `LotDetailSheet` |
| `Features/Map/LotsListView.swift` | **Deleted** (dead code) |
| `Resources/LotData.geojson` | Exists — GMU lot polygons |

#### Home & Recommendations (Day 5)
| File | Status |
|---|---|
| `Models/Recommendation.swift` | Done |
| `Features/Home/HomeViewModel.swift` | Done — permit picker state, `findParking()` |
| `Features/Home/HomeView.swift` | Done — segmented `Picker`, "Find Parking" button, results `List`, empty/error states |

#### Feedback (Day 7)
| File | Status |
|---|---|
| `Models/FeedbackRequest.swift` | Done — `FeedbackRequest` + `FeedbackResponse` |
| `Features/Feedback/FeedbackViewModel.swift` | Done — `submit()`, `reset()` |
| `Features/Feedback/FeedbackView.swift` | Done — `Form` with lot `Picker`, `StarRatingView`, comment `TextField`, success state |

#### Profile (Day 7)
| File | Status |
|---|---|
| `Features/Profile/ProfileViewModel.swift` | Done — loads email from Supabase session, delegates `signOut` to `AuthViewModel` |
| `Features/Profile/ProfileView.swift` | Done — email, version, destructive Sign Out |

#### Core
| File | Status |
|---|---|
| `Core/ColorExtension.swift` | Done — `Color(hex:)` supporting 3/6/8-digit hex |

#### Info.plist
| Key | Status |
|---|---|
| `SUPABASE_URL` | Set (Supabase project URL) |
| `SUPABASE_ANON_KEY` | Set |
| `API_BASE_URL` | `http://localhost:8000` |
| `WS_BASE_URL` | `ws://localhost:8000` |
| `NSLocationWhenInUseUsageDescription` | Set |

---

### Pending / Not Started

| Item | Reason |
|---|---|
| **Build verification** | Not yet run — deferred until repo merge |
| `Admin/` feature | Out of MVP scope for now |
| APNs push notifications | Explicitly out of MVP |
| Geofence arrival detection | "I've Arrived" manual button approach only |
| Real GMU SSO / Duo MFA | Mocked |
| `demo@gmu.edu` Supabase seed | Must be seeded manually before `MockGMULoginView` works |
| `LotData.geojson` UUID alignment | Lot IDs in geojson **must match** `mock/lots.json` in backend |

---

## Frontend ↔ Backend Synchronization Plan

### Context

The frontend and backend are currently in **separate repositories**. Integration testing is blocked until the merge (or shared deployment) is complete. The following outlines exactly what needs to happen at merge time.

---

### Step 1 — Align Lot UUIDs

This is the most critical integration step.

- `Resources/LotData.geojson` assigns a `feature.identifier` (UUID string) to each parking lot polygon.
- The backend's `mock/lots.json` (and seeded Supabase rows) assign UUIDs to lots.
- These **must be identical**. Mismatch = polygons never color-update because `MapViewModel.applyUpdates()` matches on `lot.id`.

**Action at merge:** Cross-reference `LotData.geojson` identifiers against the backend's seeded lot UUIDs. Edit whichever side is wrong to make them match.

---

### Step 2 — Update `Info.plist` for the Shared Environment

Once the backend has a deployed URL (Render, Railway, etc.) or is reachable on a shared local network:

```plist
<key>API_BASE_URL</key>
<string>https://your-backend.onrender.com</string>   <!-- or http://192.168.x.x:8000 for LAN dev -->
<key>WS_BASE_URL</key>
<string>wss://your-backend.onrender.com</string>      <!-- or ws://192.168.x.x:8000 for LAN dev -->
```

> `Info.plist` is gitignored. Each developer sets their own copy. For CI/testing, use environment variable injection or a `Info.plist.ci` template.

---

### Step 3 — Verify the API Contract

The frontend assumes these exact JSON shapes (snake_case from backend, decoded via `.convertFromSnakeCase`):

#### `GET /lots` → `[Lot]`
```json
[
  {
    "id": "uuid",
    "name": "Lot J",
    "occupancy_pct": 72.5,
    "color": "FF6B35",
    "capacity_total": 450,
    "permit_types": ["Student", "Faculty"]
  }
]
```

#### `GET /lots/{id}` → `Lot` (same shape)

#### `GET /lots/{id}/history` → `[OccupancyHistory]`
```json
[
  {
    "id": "uuid",
    "lot_id": "uuid",
    "timestamp": "2026-03-04T08:00:00Z",   // ISO 8601 required
    "occupancy_pct": 45.0
  }
]
```

#### `GET /predictions/{lot_id}` → `[Prediction]`
```json
[
  {
    "id": "uuid",
    "lot_id": "uuid",
    "minutes_ahead": 15,
    "predicted_occupancy_pct": 80.0,
    "predicted_color": "FF0000"
  }
]
```

#### `GET /recommendations?permit_type=Student` → `[Recommendation]`
```json
[
  {
    "id": "uuid",
    "lot_name": "Lot J",
    "occupancy_pct": 72.5,
    "color": "FF6B35",
    "distance": 0.3,
    "score": 0.85,
    "permit_types": ["Student"]
  }
]
```

#### `POST /feedback` (body)
```json
{
  "lot_id": "uuid",
  "rating": 4,
  "comment": "Easy to find a spot"    // nullable
}
```
Expected response: `200` or `201` (body ignored by `postVoid`).

#### WebSocket `ws://.../ws/occupancy` message payload
```json
[
  {
    "lot_id": "uuid",
    "occupancy_pct": 78.2,
    "color": "FF6B35"
  }
]
```
Backend should broadcast this array every 30s. Frontend reconnects with 5s backoff on disconnect.

---

### Step 4 — Supabase Auth Integration

The frontend uses Supabase's Swift SDK which stores the JWT automatically in the iOS Keychain. Every API request injects `Authorization: Bearer <access_token>`.

**Backend must:**
- Verify the JWT using the Supabase project's JWT secret (available in Supabase dashboard → Project Settings → API)
- Or use Supabase's REST verification endpoint

**For the demo `MockGMULoginView`:**
Before testing, seed `demo@gmu.edu / demo123456` as a Supabase Auth user:
```bash
# Via Supabase dashboard → Authentication → Users → Add User
# Or via supabase-cli:
supabase auth admin create-user --email demo@gmu.edu --password demo123456
```

---

### Step 5 — FastAPI CORS Configuration

The backend must allow requests from the iOS app. Since it's a native app (not a browser), CORS is not strictly enforced, but if backend tests include web-based tools:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten for production
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Step 6 — Smoke Test Sequence (post-merge)

Run these manually in order to validate end-to-end integration:

1. **Launch app** → WelcomeView renders with ParkEye branding and 3 buttons
2. **Sign In** with a real Supabase user → `RootView` transitions to `PermissionsView`
3. **Grant / Skip location** → transitions to `MainTabView` (Map tab)
4. **Map tab** → colored polygons appear (requires `GET /lots` returning data with matching UUIDs to geojson)
5. **WebSocket** → polygon colors update within 30s without a reload
6. **Tap a polygon** → `LotDetailSheet` slides up with occupancy %, prediction chips, 7-day chart
7. **Home tab** → select permit type → "Find Parking" → recommendations list appears
8. **Feedback tab** → select lot → star rating → submit → success checkmark
9. **Profile tab** → email shown → Sign Out → back to `WelcomeView`
10. **MockGMU login** → WelcomeView → "Continue with GMU" → enter any NetID → authenticates as `demo@gmu.edu`

---

### Quick-Reference: What Each Side Owns

| Concern | Frontend | Backend |
|---|---|---|
| JWT generation & storage | Supabase SDK (automatic) | Supabase (cloud service) |
| JWT verification on requests | N/A | FastAPI dependency / Supabase JWT secret |
| Lot polygon boundaries | `LotData.geojson` | N/A (display only) |
| Lot UUIDs (must match) | `LotData.geojson` feature identifiers | `mock/lots.json` seeded rows |
| Live occupancy broadcast | Consumes via WebSocket | Produces via `ws://.../ws/occupancy` |
| Occupancy color logic | Renders hex string from API | Computes hex string based on thresholds |
| Predictions model | Renders `minutesAhead` chips | Computes from ML/heuristic model |
| Feedback storage | POSTs to `/feedback` | Persists to Supabase table |

---

## Repo Structure (current)

```
parkeye_frontend/
├── .gitignore
├── CLAUDE.md
├── Info.plist                    ← LOCAL ONLY (gitignored)
├── Info.plist.example
├── checkpoint_03012026.md
├── checkpoint03042026.md         ← this file
├── plan.md
├── parkeye/
│   ├── App/
│   │   ├── parkeyeApp.swift
│   │   ├── AppState.swift
│   │   └── RootView.swift
│   ├── Core/
│   │   └── ColorExtension.swift
│   ├── Models/
│   │   ├── Lot.swift
│   │   ├── OccupancyUpdate.swift
│   │   ├── OccupancyHistory.swift
│   │   ├── Prediction.swift
│   │   ├── Recommendation.swift
│   │   └── FeedbackRequest.swift
│   ├── Network/
│   │   ├── APIError.swift
│   │   ├── APIEndpoints.swift
│   │   ├── APIClient.swift
│   │   └── WebSocketClient.swift
│   ├── Services/
│   │   ├── ParkingService.swift
│   │   └── LocationService.swift
│   ├── Features/
│   │   ├── Auth/
│   │   │   ├── AuthViewModel.swift
│   │   │   ├── WelcomeView.swift
│   │   │   ├── SignInView.swift
│   │   │   ├── SignUpView.swift
│   │   │   ├── MockGMULoginView.swift
│   │   │   └── PermissionsView.swift
│   │   ├── Map/
│   │   │   ├── MapViewModel.swift
│   │   │   ├── ParkeyeMapView.swift
│   │   │   ├── MapOverlayRenderer.swift
│   │   │   ├── MainTabView.swift
│   │   │   ├── LotDetailViewModel.swift
│   │   │   ├── LotDetailSheet.swift
│   │   │   └── OccupancyHistoryChart.swift
│   │   ├── Home/
│   │   │   ├── HomeViewModel.swift
│   │   │   └── HomeView.swift
│   │   ├── Feedback/
│   │   │   ├── FeedbackViewModel.swift
│   │   │   └── FeedbackView.swift
│   │   └── Profile/
│   │       ├── ProfileViewModel.swift
│   │       └── ProfileView.swift
│   ├── Resources/
│   │   └── LotData.geojson
│   └── Assets.xcassets/
└── parkeye.xcodeproj/
```

---

## Session 2 Changes — 2026-03-04

### Backend Fix: `POST /feedback` 401 Unauthorized

**File:** `parkeye-backend/app/auth.py`

`get_current_user()` was raising `HTTPException(401)` on any `JWTError`. Since the feedback endpoint uses optional auth (`User | None`), an invalid or mismatched JWT should gracefully return `None` rather than reject the request. Changed `except JWTError` block to `return None`.

- `require_user` and `require_admin` remain protected — they check `if not user` after `get_current_user` returns.
- Feedback rows submitted with an unverifiable token will have `user_id=None`, which is already supported by the backend schema.

---

### Frontend Fix: Auth State Not Reset on Sign-Out

**Problem:** `FeedbackViewModel`, `HomeViewModel`, and `ProfileViewModel` are singletons in `AppState`. Signing out and signing in with a different account left stale state (previous user's feedback form, recommendations, email) visible.

**Changes:**
- `Features/Feedback/FeedbackViewModel.swift` — already had `reset()`, no change needed
- `Features/Home/HomeViewModel.swift` — added `reset()`: clears `recommendations`, `hasSearched`, `errorMessage`, resets `selectedPermitType` and `arrivalTime`
- `Features/Profile/ProfileViewModel.swift` — added `reset()`: clears `userEmail`
- `App/AppState.swift` — added `resetAllViewModels()` which calls all three
- `App/RootView.swift` — `.signedOut` case now calls `appState.resetAllViewModels()` before clearing `isAuthenticated`/`currentUser`

---

### Frontend Feature: Email Confirmation Alert on Sign-Up

**Problem:** After a successful `signUp()` call, the app was silent — no indication that a confirmation email was sent. Users had no idea they needed to check their inbox.

**Changes:**
- `Features/Auth/AuthViewModel.swift` — added `needsEmailConfirmation: Bool` flag; `signUp()` now inspects the returned `AuthResponse`: if `response.session == nil`, Supabase requires email confirmation and the flag is set to `true`
- `Features/Auth/SignUpView.swift` — added `.alert("Check Your Email", isPresented: $viewModel.needsEmailConfirmation)` showing the user's email and instructing them to confirm before signing in

> Note: The confirmation email links to a localhost URL — this is a Supabase project config issue. Fix by setting the **Site URL** and **Redirect URLs** in the Supabase dashboard (Authentication → URL Configuration) to the app's custom URL scheme (e.g. `io.parkeye://`).

---

### Frontend Feature: Auto-Refresh Recommendations on Filter Change

**Problem:** Changing permit type or arrival time required tapping "Find Parking" again — the results list did not update automatically.

**Change:** `Features/Home/HomeView.swift` — added `.onChange(of: viewModel.selectedPermitType)` and `.onChange(of: viewModel.arrivalTime)` modifiers that call `viewModel.findParking()` automatically. Both guard on `viewModel.hasSearched` so the initial empty-state prompt is preserved until the user performs a first search.

---

## Notes for Next Session

- **Build first.** Run `xcodebuild -project parkeye.xcodeproj -scheme parkeye -destination 'platform=iOS Simulator,name=iPhone 17' build` and fix any compiler errors before proceeding.
- **No `project.pbxproj` edits needed** for new source files — `PBXFileSystemSynchronizedRootGroup` auto-includes everything in `parkeye/`.
- `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` — all types are implicitly `@MainActor`; actor types and `nonisolated` methods are the exception.
- Supabase products: `import Supabase` covers all (Auth, PostgREST, Realtime, Storage, Functions).
- `Info.plist` lives at the **project root** (not inside `parkeye/`) — this prevents the synced group from bundling it as a resource.
- Supabase dashboard → Authentication → URL Configuration: set Site URL + Redirect URLs to the app's custom URL scheme to fix the localhost confirmation link.
