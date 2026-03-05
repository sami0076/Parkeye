# ParkEye — UX Overview (Current Version)

This document describes the user experience of the current build: what each screen does, what is fully functional, and what is not yet implemented.

---

## App Flow

```
Launch
  └── Not authenticated → Welcome Screen
        ├── Sign In
        ├── Create Account
        └── Continue with GMU (mock)
  └── Authenticated → Main Tab View
        ├── Map
        ├── Home (Find Parking)
        ├── Feedback
        └── Profile
```

---

## Auth Screens

### Welcome
The entry point. Three options:
- **Sign In** — email/password via Supabase
- **Create Account** — email/password registration via Supabase
- **Continue with GMU** — mock SSO, accepts `demo@gmu.edu` / `demo123456`

After authentication, the app routes to `MainTabView`. Supabase stores the JWT in the iOS Keychain, so users stay signed in across launches.

### Sign Up
After submitting the Create Account form, if Supabase requires email confirmation (the default), an alert appears: **"Check Your Email"** — informing the user that a confirmation link has been sent to their address and they must confirm before signing in.

> Note: The confirmation link currently redirects to localhost. This will be fixed by configuring a custom URL scheme in the Supabase dashboard.

### Permissions
Shown after sign-up. Requests location access ("When In Use") for walking distance calculations in parking recommendations.

---

## Tab: Map

The primary tab. Shows a full-screen `MKMapView` centered on GMU campus.

**What works:**
- Lot polygons loaded from `LotData.geojson` are rendered as colored overlays on the map
- Polygon color reflects live occupancy: green (< 60%), yellow (60–85%), red (> 85%)
- Occupancy updates live via WebSocket (`ws://.../ws/occupancy`) every ~30 seconds
- If the WebSocket connection drops, the app falls back to polling `GET /lots` every 30 seconds
- Tapping a polygon opens the **Lot Detail Sheet**

### Lot Detail Sheet
A bottom sheet (resizable: medium / large) that appears when a lot is tapped.

**What works:**
- Lot name in the navigation title
- Current occupancy percentage and capacity (e.g. "47% full — Capacity: 200 spaces") with color dot
- **Predictions**: Two chips showing predicted occupancy at +15 min and +30 min, each with a color dot
- **Weekly Pattern**: A Swift Charts area/line chart showing historical occupancy by hour across the week
- **Permit Types**: Lists accepted permit types (e.g. "general, faculty")

---

## Tab: Home (Find Parking)

Lets users search for recommended lots based on permit type and arrival time.

**What works:**
- Segmented picker for permit type: Any, General, West Campus, Faculty
- Date/time picker for arrival time (defaults to now)
- "Find Parking" button triggers `GET /recommendations` with the selected permit type, arrival time, and the user's current GPS location (falls back to GMU campus center if location is unavailable)
- **Changing the permit type or arrival time after a search automatically re-fetches results** — no need to tap "Find Parking" again. The auto-refresh only activates after the first manual search.
- Results list shows each recommended lot with: color dot, lot name, accepted permits, estimated walk time, and current occupancy %
- "Any" permit type returns results from all lots (no permit filter applied)
- Error and empty-state messaging

---

## Tab: Feedback

A form for submitting parking feedback after a visit.

**What works:**
- Lot picker (populated from the same lot list as the map)
- 1–5 star rating for **Accuracy** (how accurate was the occupancy prediction?)
- 1–5 star rating for **Experience** (how was the overall parking experience?)
- Optional free-text note field
- Submit button (disabled until a lot and both ratings are selected)
- Success screen with a "Submit Another" option
- Submits to `POST /feedback`

---

## Tab: Profile

A simple account screen.

**What works:**
- Displays the signed-in user's email address
- Displays app version
- **Sign Out** button — clears the Supabase session and returns to the Welcome screen

---

## What Is Not Yet Implemented

These features are planned but not present in this version:

| Feature | Description |
|---|---|
| Events | `GET /events` — campus events that affect lot occupancy are used in recommendations on the backend but not surfaced in the UI |
| Floor-level occupancy | `GET /lots/{id}/floors` — multi-level deck breakdown |
| Admin panel | `Features/Admin/` directory not yet built; requires admin JWT |
| Push notifications | APNs not configured; live updates are WebSocket-only |
| Offline mode | No local caching; requires network for all data |
| Real GMU SSO | Mock only — no Duo MFA, no real CAS integration |
| iPad layout | Designed for iPhone; no adaptive iPad layout |
