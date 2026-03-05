# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands

All builds and tests are driven through Xcode. Use `xcodebuild` from the project root:

```bash
# Build the app
xcodebuild -project parkeye.xcodeproj -scheme parkeye -destination 'platform=iOS Simulator,name=iPhone 17' build

# Run unit tests
xcodebuild -project parkeye.xcodeproj -scheme parkeye -destination 'platform=iOS Simulator,name=iPhone 17' test

# Run a single test (by test class)
xcodebuild -project parkeye.xcodeproj -scheme parkeye -destination 'platform=iOS Simulator,name=iPhone 17' -only-testing:parkeyeTests/parkeyeTests test

# Run UI tests only
xcodebuild -project parkeye.xcodeproj -scheme parkeye -destination 'platform=iOS Simulator,name=iPhone 17' -only-testing:parkeyeUITests test
```

## MVP Overview

ParkEye is a native iOS app (Swift + SwiftUI) for GMU parking. It connects to a FastAPI backend and authenticates via Supabase Auth. All persistent state lives in Supabase — **no Core Data, no SwiftData, no SQLite, no local database of any kind**. The app is stateless between launches: authenticate, fetch, display.

**Only external dependency:** `github.com/supabase/supabase-swift` via SPM (adds Supabase Auth, PostgREST client, Realtime). Everything else is Apple SDK.

**Not in MVP:** offline mode, APNs push notifications, Apple/Google Maps SDK (MKMapView only), real geofence detection, background location tracking, real GMU SSO/Duo MFA, iPad layout, localization.

## Tech Stack

| Layer | Choice |
|---|---|
| Language | Swift 5.10 |
| UI | SwiftUI |
| Auth | Supabase Swift SDK |
| Networking | URLSession async/await |
| WebSocket | URLSessionWebSocketTask |
| State | `@Observable` + `@StateObject` |
| Map | MapKit (MKMapView + MKPolygon overlays) |
| Charts | Swift Charts (occupancy history) |
| Packages | SPM — supabase-swift only |

## Project Structure (Target)

All source files live in the `parkeye/` target subdirectory (mirroring the Xcode project structure). The layout below is the **intended** structure to build towards — not the current state.

```
parkeye/
├── App/              # ParkeyeApp.swift, RootView.swift, AppState.swift, DependencyContainer.swift
├── Models/           # Codable structs mirroring backend JSON (no NSManagedObject)
├── Features/
│   ├── Auth/         # WelcomeView, SignupView, MockGMULoginView, PermissionsView + ViewModels
│   ├── Home/         # Permit picker, duration/arrival pickers, FindParkingButton + ViewModel
│   ├── Map/          # MKMapView wrapper, overlays, detail sheets, charts + ViewModels
│   ├── Feedback/     # Star rating views, submission + ViewModel
│   ├── Profile/      # User info, notification settings + ViewModel
│   └── Admin/        # Dashboard, lot list, status editor + ViewModels (admin JWT required)
├── Services/         # Auth, Location, Parking, Feedback, Admin — business logic between ViewModels and network
├── Network/          # APIClient, APIEndpoints, APIError, AuthInterceptor, WebSocketClient
├── Core/             # Reusable components, extensions, Logger, Constants, Theme
└── Resources/        # Assets.xcassets, LotData.geojson, Info.plist
```

## Architecture

**Entry point:** `App/ParkeyeApp.swift` creates the single `SupabaseClient` singleton (URL + anon key from Info.plist) and injects it into the environment. `RootView` reads `AppState.isAuthenticated` and routes to either the auth flow or `MainTabView`.

**Data flow pattern:** Views → ViewModels → Services → Network/APIClient or SupabaseClient. No view touches URLSession directly.

**Models:** Plain `Codable` structs in `Models/` that mirror backend JSON exactly. No migration files — if the backend schema changes, update the struct.

**Auth:** Supabase SDK stores JWT in iOS Keychain automatically. `AuthInterceptor` reads `SupabaseClient.auth.session?.accessToken` and injects `Authorization: Bearer` on every request. Admin tab only visible when `AppState.currentUser.role == "admin"`.

**Live occupancy:** `MapViewModel` connects to `ws://.../ws/occupancy` on appear. Backend broadcasts `[{lot_id, occupancy_pct, color}]` every 30s → `WebSocketClient` publishes via `AsyncStream` → SwiftUI re-renders overlays. Falls back to `GET /lots` polling every 30s if WebSocket drops.

**Demo stubs:** GMU SSO = `MockGMUAuthService` returning a hardcoded session. Geofence arrival = manual "I've Arrived" button. APNs = not implemented (WebSocket only).

**Critical shared file:** `Resources/LotData.geojson` — GMU lot boundary polygons for `MKPolygon` overlays. Lot IDs here **must match** UUIDs seeded in the backend `mock/lots.json`. Verify on Day 1.

## Key API Endpoints

| Endpoint | Method | Used By |
|---|---|---|
| `/lots` | GET | MapViewModel — initial load + 30s poll fallback |
| `/lots/{id}` | GET | LotDetailSheet |
| `/lots/{id}/history` | GET | OccupancyHistoryChart (7-day) |
| `/lots/{id}/floors` | GET | DeckViewModel |
| `/predictions/{lot_id}` | GET | LotDetailSheet — t+15/t+30 chips |
| `/recommendations` | GET | HomeViewModel — after Find Parking tap |
| `/events` | GET | LotDetailSheet + MapViewModel |
| `/feedback` | POST | FeedbackViewModel |
| `/admin/lots/{id}/status` | PATCH | LotStatusEditorViewModel (admin JWT) |
| `ws://.../ws/occupancy` | WS | WebSocketClient → MapViewModel |

## Environment Configuration

Secrets live in `Info.plist` (not committed — add to `.gitignore`, commit `Info.plist.example` with placeholders):

| Key | Description |
|---|---|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Public anon key (not the service role key) |
| `API_BASE_URL` | FastAPI URL: `http://localhost:8000` (dev) or Render URL (prod) |
| `WS_BASE_URL` | WebSocket URL: `ws://localhost:8000` (dev) or `wss://...` (prod) |

## Bootstrap Checklist

Steps required before writing any feature code (one-time setup):

1. **Remove Core Data boilerplate** — the Xcode template generated `parkeye/Persistence.swift`, `parkeye/ContentView.swift`, and `parkeye/parkeye.xcdatamodeld`. Delete all three; they contradict the no-Core-Data rule.
2. **Add supabase-swift** — In Xcode: File → Add Package Dependencies → `https://github.com/supabase/supabase-swift` (use the latest tagged release). No other SPM packages are needed.
3. **Create Info.plist** — copy `Info.plist.example` into `Info.plist` (project root, next to `Info.plist.example`) and fill in the four keys from the Environment Configuration table. `Info.plist` is in `.gitignore`.

## Testing

- Unit tests (`ParkeyeTests/`) use the Swift Testing framework (`import Testing`, `@Test`, `#expect()`).
- UI tests (`ParkeyeUITests/`) use XCTest (`XCUIApplication`).

**Compiler settings of note:** `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` — all types default to `@MainActor` isolation unless explicitly opted out.
