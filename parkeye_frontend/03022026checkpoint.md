# ParkEye – Session Checkpoint (03/02/2026)

## Status: Days 1 & 2 Complete — BUILD SUCCEEDED

---

## What Was Accomplished

### Day 1 — Foundation & Auth

Bootstrapped the full app skeleton: app entry point, dependency wiring, authentication flow, network layer, and a basic lots list screen. The project now has a working sign-in/sign-up flow backed by Supabase Auth.

**Files created:**

| File | Description |
|---|---|
| `parkeye/parkeyeApp.swift` | `@main` entry. Reads `SUPABASE_URL` + `SUPABASE_ANON_KEY` from `Info.plist`, constructs `SupabaseClient`, seeds `AppState` into environment. |
| `parkeye/App/AppState.swift` | `@Observable @MainActor`. Owns `SupabaseClient`, `AuthViewModel`, `MapViewModel`. Constructs dependency chain: `SupabaseClient → APIClient → ParkingService → MapViewModel`. |
| `parkeye/App/RootView.swift` | Listens to `supabase.auth.authStateChanges` (AsyncStream). Routes to `SignInView` or `MainTabView` based on `appState.isAuthenticated`. Handles `.initialSession`, `.signedIn`, `.tokenRefreshed`, `.signedOut`. |
| `parkeye/Models/Lot.swift` | `Codable, Identifiable`. Fields: `id: UUID`, `name: String`, `occupancyPct: Double`, `color: String`, `capacityTotal: Int?`, `permitTypes: [String]?`. Decoded via `convertFromSnakeCase`. |
| `parkeye/Network/APIError.swift` | Enum: `invalidURL`, `unauthorized`, `httpError(statusCode:)`, `decodingError(Error)`, `networkError(Error)`. |
| `parkeye/Network/APIEndpoints.swift` | Reads `API_BASE_URL` from `Bundle.main`. Provides `lots: URL` and `lot(id: UUID) -> URL`. |
| `parkeye/Network/APIClient.swift` | `actor`. `get<T: Decodable>(_ url: URL)` — injects `Authorization: Bearer <token>` from `supabase.auth.session.accessToken`, decodes with `convertFromSnakeCase`, maps HTTP status codes to `APIError`. |
| `parkeye/Services/ParkingService.swift` | `actor`. `fetchLots() async throws -> [Lot]` via `APIClient`. |
| `parkeye/Features/Auth/AuthViewModel.swift` | `@Observable`. Fields: `email`, `password`, `isLoading`, `errorMessage`. Methods: `signIn()`, `signUp()`, `signOut()` — all delegate to `supabase.auth`. |
| `parkeye/Features/Auth/SignInView.swift` | `@Bindable var viewModel: AuthViewModel`. Email/password fields, Sign In + Create Account buttons, inline error display, loading spinner. |
| `parkeye/Features/Map/MapViewModel.swift` | `@Observable`. `lots: [Lot]`, `isLoading`, `errorMessage`. `loadLots()` calls `ParkingService.fetchLots()`. |
| `parkeye/Features/Map/LotsListView.swift` | Simple `List` of lots with `ContentUnavailableView` fallback (replaced by Day 2 work). |
| `parkeye/Core/ColorExtension.swift` | `Color(hex: String)` extension — handles 3-, 6-, 8-char hex strings. |

**Key fix:** `import Supabase` (umbrella) was broken because Xcode only linked sub-products (Auth, PostgREST, etc.). Fixed by manually adding the `Supabase` umbrella product to `pbxproj` (ProductDep UUID `25B8F3A22F55392600A032EF`, BuildFile UUID `25B8F3A12F55392600A032EF`).

---

### Day 2 — Map View & GeoJSON Overlays

Added the interactive MapKit map with colored polygon overlays for each GMU parking lot, driven by occupancy data from the API.

**Files created/modified:**

| File | Description |
|---|---|
| `parkeye/Resources/LotData.geojson` | 5 GMU lot boundary polygons. Feature identifiers are placeholder UUIDs (`11111...` through `55555...`) — **must be replaced with real UUIDs matching the backend `mock/lots.json` before the WebSocket step**. |
| `parkeye/Features/Map/MapOverlayRenderer.swift` | `LotPolygonRenderer: MKPolygonRenderer`. `configure(hexColor:)` sets fill (45% alpha) + stroke on first render. `updateColor(hexColor:)` updates color + calls `setNeedsDisplay()` for live occupancy updates. |
| `parkeye/Features/Map/ParkeyeMapView.swift` | `UIViewRepresentable`. Centers on GMU (38.8316, -77.3076), span 0.025°. `Coordinator: MKMapViewDelegate` — loads GeoJSON overlays from bundle, caches `LotPolygonRenderer` instances keyed by lot UUID string, updates colors when `viewModel.lots` changes. Lot UUID stored in `MKPolygon.subtitle`. |
| `parkeye/Features/Map/MainTabView.swift` | `TabView` with Map tab (`ParkeyeMapView`) and Home tab (placeholder with Sign Out button). Calls `mapViewModel.loadLots()` via `.task`. |
| `parkeye/App/RootView.swift` | Updated: routes to `MainTabView` (was `LotsListView`). Passes `mapViewModel` and `authViewModel`. |

**GeoJSON → overlay ID matching pattern:**
```swift
// In loadOverlays: store feature.identifier in polygon.subtitle
polygon.subtitle = feature.identifier  // e.g. "11111111-..."

// In renderer lookup: case-insensitive UUID comparison
viewModel.lots.first { $0.id.uuidString.lowercased() == id.lowercased() }
```

---

## Architecture as Built

```
parkeyeApp
└── AppState (@Observable @MainActor)
    ├── SupabaseClient  (singleton, from Info.plist)
    ├── APIClient       (actor, injects Bearer token)
    ├── ParkingService  (actor, fetchLots)
    ├── AuthViewModel   (@Observable, sign in/up/out)
    └── MapViewModel    (@Observable, lots: [Lot])

RootView
├── isAuthenticated=false → SignInView(viewModel: authViewModel)
└── isAuthenticated=true  → MainTabView
    ├── [Map tab]  ParkeyeMapView(viewModel: mapViewModel)
    │              └── Coordinator (MKMapViewDelegate)
    │                  └── LotPolygonRenderer cache [UUID: renderer]
    └── [Home tab] placeholder + Sign Out
```

---

## Known Issues / TODOs Before Day 3

1. **GeoJSON UUIDs are placeholders** — `LotData.geojson` uses `11111111-...` through `55555555-...`. These must match the UUIDs in the backend's `mock/lots.json` before live occupancy colors will work correctly. Update the geojson or seed the backend with matching UUIDs.

2. **LotsListView is dead code** — still exists at `parkeye/Features/Map/LotsListView.swift` but is no longer used after `RootView` was updated to route to `MainTabView`. Can be deleted or repurposed.

3. **Home tab is a placeholder** — just a Sign Out button. Full Home feature (permit picker, duration picker, Find Parking) is Day 5.

---

## Day 3 Plan: WebSocket Live Occupancy

**Goal:** `MapViewModel` receives live occupancy pushes from `ws://.../ws/occupancy` every 30s; polygon colors update in real time.

### Files to create

**`parkeye/Network/WebSocketClient.swift`**
```swift
actor WebSocketClient {
    // Connects to WS_BASE_URL/ws/occupancy
    // Publishes [OccupancyUpdate] via AsyncStream
    // Reconnects on disconnect; falls back to 30s GET /lots poll
}
```

**`parkeye/Models/OccupancyUpdate.swift`**
```swift
struct OccupancyUpdate: Codable {
    let lotId: UUID        // snake_case: lot_id
    let occupancyPct: Double
    let color: String
}
```

### Changes to existing files

**`parkeye/Features/Map/MapViewModel.swift`** — add:
```swift
private let webSocketClient: WebSocketClient

func connectLiveOccupancy() async {
    for await updates in webSocketClient.stream() {
        for update in updates {
            if let i = lots.firstIndex(where: { $0.id == update.lotId }) {
                // Lot is immutable struct — reconstruct with updated fields
                lots[i] = Lot(id: lots[i].id, name: lots[i].name,
                              occupancyPct: update.occupancyPct,
                              color: update.color,
                              capacityTotal: lots[i].capacityTotal,
                              permitTypes: lots[i].permitTypes)
            }
        }
    }
}
```

**`parkeye/Features/Map/MainTabView.swift`** — add `.task { await mapViewModel.connectLiveOccupancy() }` alongside existing `loadLots` task.

**`parkeye/App/AppState.swift`** — construct `WebSocketClient` and inject into `MapViewModel`.

### WS_BASE_URL
Read from `Info.plist` key `WS_BASE_URL` (same pattern as `API_BASE_URL` in `APIEndpoints.swift`).

---

## Environment & Build Notes

- **Build command:**
  ```
  DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
  xcodebuild -project parkeye.xcodeproj -scheme parkeye \
  -destination 'platform=iOS Simulator,name=iPhone 17' build
  ```
- **`Info.plist`** is at the project root (not inside `parkeye/`). Keys: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `API_BASE_URL`, `WS_BASE_URL`.
- **`PBXFileSystemSynchronizedRootGroup`** — new `.swift` files dropped into `parkeye/` subdirectories are auto-compiled; no `pbxproj` edits needed for source files. Same applies to resource files (e.g., `.geojson`).
- **`SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor`** — all classes/structs default to `@MainActor`. `actor` types (APIClient, ParkingService, WebSocketClient) are exempt.
- **`@Observable` + bindings** — views that bind to `@Observable` ViewModels must declare them as `@Bindable var viewModel: SomeVM` (not plain `var`) to use `$viewModel.property` two-way bindings.

---

## File Tree (current state)

```
parkeye/
├── parkeyeApp.swift
├── App/
│   ├── AppState.swift
│   └── RootView.swift
├── Models/
│   └── Lot.swift
├── Network/
│   ├── APIClient.swift
│   ├── APIEndpoints.swift
│   └── APIError.swift
├── Services/
│   └── ParkingService.swift
├── Features/
│   ├── Auth/
│   │   ├── AuthViewModel.swift
│   │   └── SignInView.swift
│   └── Map/
│       ├── LotsListView.swift     ← dead code, can delete
│       ├── MapOverlayRenderer.swift
│       ├── MapViewModel.swift
│       ├── MainTabView.swift
│       └── ParkeyeMapView.swift
├── Core/
│   └── ColorExtension.swift
└── Resources/
    └── LotData.geojson            ← UUIDs are placeholders
```
