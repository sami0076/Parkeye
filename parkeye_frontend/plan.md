# ParkEye iOS — Week 1 Plan

## Goal
By end of week: a working iOS app that authenticates via Supabase, displays GMU parking lots on a live map with occupancy colors, and lets a user get a parking recommendation.

---

## Day 1 — Core Plumbing + GET /lots

**Deliverable:** App launches → sign in → lots list appears (no map yet).

- [ ] `App/AppState.swift` — `@Observable` class, `isAuthenticated`, `currentUser`
- [ ] `App/RootView.swift` — routes to `SignInView` or `MainTabView` based on `isAuthenticated`; listens to `supabase.auth.onAuthStateChange`
- [ ] `App/parkeyeApp.swift` — wire up `SupabaseClient` from `Info.plist`, inject into environment
- [ ] `Models/Lot.swift` — `Codable` struct mirroring `GET /lots` JSON
- [ ] `Network/APIError.swift` — error enum
- [ ] `Network/APIEndpoints.swift` — reads `API_BASE_URL` from bundle, defines `.lots`
- [ ] `Network/APIClient.swift` — generic `get<T>` using `URLSession`, injects `Authorization: Bearer` from `supabase.auth.session?.accessToken`
- [ ] `Services/ParkingService.swift` — `fetchLots() async throws -> [Lot]`
- [ ] `Features/Auth/AuthViewModel.swift` — `signIn`, `signUp` via `supabase.auth`
- [ ] `Features/Auth/SignInView.swift` — email + password form
- [ ] `Features/Map/MapViewModel.swift` — `@Observable`, `var lots: [Lot]`, `loadLots()`
- [ ] `Features/Map/LotsListView.swift` — placeholder `List` view showing lot name + occupancy

---

## Day 2 — Map + Polygon Overlays

**Deliverable:** Lots rendered as colored polygons on `MKMapView`, centered on GMU.

- [ ] `Resources/LotData.geojson` — GMU lot boundary polygons (verify lot IDs match backend UUIDs)
- [ ] `Features/Map/ParkeyeMapView.swift` — `UIViewRepresentable` wrapping `MKMapView`
- [ ] `Features/Map/MapOverlayRenderer.swift` — `MKOverlayRenderer` subclass, colors polygons by `occupancy_pct`
- [ ] Wire `MapViewModel.lots` → overlay colors on the map
- [ ] `Features/Map/MainTabView.swift` — tab bar shell (Map tab + Home tab placeholder)

---

## Day 3 — Live Occupancy (WebSocket)

**Deliverable:** Overlay colors update in real-time every 30s.

- [ ] `Network/WebSocketClient.swift` — wraps `URLSessionWebSocketTask`, publishes via `AsyncStream<[OccupancyUpdate]>`
- [ ] `Models/OccupancyUpdate.swift` — `{lot_id, occupancy_pct, color}` Codable struct
- [ ] `Network/APIEndpoints.swift` — add `wsOccupancy` URL using `WS_BASE_URL` from bundle
- [ ] `MapViewModel` — connect WebSocket on `.task`, update lots; fall back to 30s `GET /lots` poll on disconnect

---

## Day 4 — Lot Detail Sheet + Occupancy History

**Deliverable:** Tap a lot → bottom sheet with occupancy chart and predictions.

- [ ] `Models/OccupancyHistory.swift`, `Models/Prediction.swift`
- [ ] `Features/Map/LotDetailViewModel.swift` — fetches `/lots/{id}`, `/lots/{id}/history`, `/predictions/{lot_id}`
- [ ] `Features/Map/LotDetailSheet.swift` — name, current occupancy, `OccupancyHistoryChart`, t+15/t+30 prediction chips
- [ ] `Features/Map/OccupancyHistoryChart.swift` — Swift Charts 7-day bar/line chart

---

## Day 5 — Home + Recommendations

**Deliverable:** "Find Parking" flow returns recommended lots.

- [ ] `Models/Recommendation.swift`
- [ ] `Features/Home/HomeViewModel.swift` — permit picker state, calls `GET /recommendations`
- [ ] `Features/Home/HomeView.swift` — permit type picker, "Find Parking" button, results list
- [ ] `Services/ParkingService.swift` — add `fetchRecommendations(permit:) async throws -> [Recommendation]`

---

## Day 6 — Auth Polish + Permissions

**Deliverable:** Full auth flow including sign-up, mock GMU SSO screen, location permission.

- [ ] `Features/Auth/WelcomeView.swift` — landing screen with Sign In / Sign Up / Continue with GMU
- [ ] `Features/Auth/SignUpView.swift`
- [ ] `Features/Auth/MockGMULoginView.swift` — fake GMU SSO screen (hardcoded success)
- [ ] `Features/Auth/PermissionsView.swift` — prompt for location permission
- [ ] `Services/LocationService.swift` — `CLLocationManager` wrapper, publishes current location

---

## Day 7 — Feedback + Profile + Buffer

**Deliverable:** Working feedback submission; profile tab; end-to-end smoke test.

- [ ] `Models/FeedbackRequest.swift`
- [ ] `Features/Feedback/FeedbackViewModel.swift` + `FeedbackView.swift` — star rating + POST /feedback
- [ ] `Features/Profile/ProfileViewModel.swift` + `ProfileView.swift` — display email, sign out
- [ ] Wire all tabs into `MainTabView` (Map, Home, Profile)
- [ ] End-to-end smoke test: launch → sign in → map loads → tap lot → see detail → find parking → submit feedback

---

## Out of scope for Week 1
- Admin dashboard (requires admin JWT)
- APNs push notifications
- Real geofence / background location
- iPad layout
- Real GMU SSO / Duo MFA
