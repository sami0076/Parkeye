# ParkEye iOS Frontend

Native iOS app for GMU parking — Swift + SwiftUI + Supabase Auth.

**Stack:** Swift 5.10 · SwiftUI · MapKit · Swift Charts · URLSession WebSocket · Supabase Swift SDK (only external dependency)
**No local database.** All persistent state lives in Supabase. The app authenticates, fetches, and displays — stateless between launches.

---

## Project Status (as of March 4, 2026)

All core MVP screens are implemented and wired to the backend. The app is functional end-to-end for the primary user journey: sign up → find parking → view map → tap lot → see predictions → submit feedback → sign out.

| Area | Status |
|---|---|
| Auth (Sign In / Sign Up / GMU Mock / Permissions) | Done |
| Map with live occupancy overlays + WebSocket | Done |
| Lot Detail Sheet (occupancy, predictions, history chart) | Done |
| Home — Find Parking with auto-refresh on filter change | Done |
| Feedback (lot picker, star ratings, submission) | Done |
| Profile (email, sign out with full state reset) | Done |
| Admin panel | Not started |
| Floor-level deck views | Not started |
| Events surfaced in UI | Not started |

### Recent Fixes (March 4)
- `POST /feedback` was returning 401 for authenticated users — fixed in backend `auth.py`
- Stale state (previous user's feedback/recommendations/email) persisted after sign-out — all ViewModels now reset on sign-out
- Sign-up had no confirmation feedback — "Check Your Email" alert now shown after Supabase sends confirmation link
- Changing permit type or arrival time in Home tab now auto-refreshes results

---

## 4-Week Plan: March 4 → April 1

### Week 1 — March 4–10: Stabilize & Verify End-to-End

**Goal:** The existing feature set works reliably on a real device against the deployed backend.

| Task | Owner | Notes |
|---|---|---|
| Build verification — fix any compiler errors | Both | Run `xcodebuild` against iPhone 17 Simulator |
| Align `LotData.geojson` UUIDs with `mock/lots.json` | Both | Most likely integration bug — verify Day 1 |
| Point `Info.plist` at deployed backend URL (Render/Railway) | Both | `API_BASE_URL` + `WS_BASE_URL` |
| Smoke test full user flow on physical device | Both | Follow the 10-step sequence in `checkpoint03042026.md` |
| Fix Supabase confirmation redirect URL | Solo | Set Site URL + Redirect URLs in Supabase dashboard → `io.parkeye://` |
| Seed `demo@gmu.edu / demo123456` in Supabase Auth | Solo | Required before `MockGMULoginView` works end-to-end |
| Verify `POST /feedback` works with real signed-in user | Solo | Auth fix is deployed — confirm in app |

---

### Week 2 — March 11–17: Admin Panel + Polish Pass

**Goal:** Admin status overrides work and propagate to the map. Core screens get loading/error state polish.

#### Admin Panel (Features/Admin/)

The admin tab is only shown when `AppState.currentUser.role == "admin"`. Set the admin role manually in the Supabase dashboard before building.

| File to Create | Purpose |
|---|---|
| `Features/Admin/AdminDashboardView.swift` | List all lots with live status chips |
| `Features/Admin/LotStatusEditorView.swift` | Popup: open / limited / closed + until date + reason |
| `Features/Admin/AdminDashboardViewModel.swift` | `fetchLots()` + `patchStatus()` via `PATCH /admin/lots/{id}/status` |

Flow: Admin taps a lot → selects new status → backend updates → next WebSocket broadcast (≤30s) reflects the change on the map in red/yellow/green.

#### Loading & Error State Polish
- `MapViewModel` — show a loading overlay while `loadLots()` is in flight; show a retry banner if the initial fetch fails
- `HomeView` — skeleton shimmer rows while `findParking()` is loading (currently shows a spinner only)
- `LotDetailSheet` — handle 404 (lot not found) gracefully with an error message instead of a blank sheet
- `FeedbackView` — if submission fails, surface the error inline (currently done) and allow retry without losing entered data

---

### Week 3 — March 18–24: Deck Views + Events + UX Refinements

**Goal:** Multi-level deck breakdown visible in the app. Campus events surfaced in lot detail. UX gaps closed.

#### Floor-Level Deck Views

| File to Create | Purpose |
|---|---|
| `Features/Map/DeckDetailSheet.swift` | Bottom sheet variant for parking decks showing per-floor occupancy |
| `Features/Map/FloorOccupancyView.swift` | Grid of sections per floor with occupancy color coding |

Wire to `GET /lots/{id}/floors`. `LotDetailSheet` should detect `lot.isDeck == true` and render the floor slider instead of the standard occupancy view.

#### Campus Events in Lot Detail
- Add `Models/CampusEvent.swift` — `id`, `title`, `startTime`, `endTime`, `impactLevel`
- Add `fetchEvents(lotId:)` to `ParkingService` → `GET /events?lot_id={id}`
- Surface in `LotDetailSheet` as a collapsible "Upcoming Events" section below the history chart

#### UX Refinements
- **Map tab:** Add an occupancy legend (green / yellow / red) as a floating overlay in the bottom-left corner — users currently have no key for the colors
- **Home tab:** If the user has no location permission, show an inline note that results are based on campus center coordinates, not their actual position
- **Feedback tab:** Pre-select the lot if the user just tapped a lot on the map (pass `selectedLotId` from `MapViewModel` into `FeedbackViewModel` on tab switch)
- **Profile tab:** Add a "Permit Type" preference row (stored in UserDefaults) so the Home tab defaults to their permit on launch

---

### Week 4 — March 25–April 1: Demo Build

**Goal:** A polished, stable TestFlight build pointed at production. Demo dry-run on physical devices. No new features — only polish and hardening.

#### Demo Checklist

| Item | By |
|---|---|
| Point `Info.plist` at final production Render URL | March 25 |
| Full demo dry-run on physical iPhone (not simulator) | March 27 |
| TestFlight build uploaded and installed on demo device | March 28 |
| Verify all 10 smoke-test steps pass on demo device | March 29 |
| Confirm WebSocket color update visible within 30s on map | March 29 |
| Admin override test: set a lot to "closed" → map turns red | March 30 |
| Final demo rehearsal — full user journey, no stopping | March 31 |

#### Polish Items (Week 4 only if time permits)
- App icon + launch screen finalized
- Navigation titles and tab bar labels reviewed for consistency
- Haptic feedback on feedback submission success
- `OccupancyHistoryChart` X-axis label formatting (day-of-week abbreviations)
- Sign-up form: dismiss keyboard on submit
- `MockGMULoginView`: add a visible "Demo Mode" badge so it's clear during the presentation this is a stub

---

## Key Risks

| Risk | Mitigation |
|---|---|
| `LotData.geojson` UUIDs don't match backend | Verify Day 1, Week 1 — this blocks the entire map feature |
| Supabase JWT secret mismatch causes silent 401s on feedback | Auth fix deployed; test with real signed-in user in Week 1 |
| WebSocket drops on Render's free tier (sleeps after 15 min inactivity) | Use paid tier for demo week or keep the backend warm with a cron ping |
| Admin JWT claim not set before Week 2 | Set `role = admin` manually in Supabase dashboard for the test account |
| Demo device has never run the app before | TestFlight install + full dry-run by March 29 at the latest |

---

## Build Commands

```bash
# Build
xcodebuild -project parkeye.xcodeproj -scheme parkeye \
  -destination 'platform=iOS Simulator,name=iPhone 17' build

# Run unit tests
xcodebuild -project parkeye.xcodeproj -scheme parkeye \
  -destination 'platform=iOS Simulator,name=iPhone 17' test
```

`Info.plist` is gitignored — copy `Info.plist.example` and fill in your keys before building.

---

## Docs

| File | Contents |
|---|---|
| `CLAUDE.md` | Architecture rules, build commands, tech stack reference |
| `checkpoint03042026.md` | Detailed implementation log with all session changes |
| `UX.md` | Screen-by-screen UX description of the current build |
| `plan.md` | Original Day 1–7 implementation plan |
