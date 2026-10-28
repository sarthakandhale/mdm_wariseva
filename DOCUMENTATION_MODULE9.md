# WariSeva – Multilingual Smart Platform for Medical Emergency, Lost Person & Item Assistance
## Master Data Management (MDM) & Software Engineering Documentation: Module 9 – Dindi Route, Location & Wari Movement Management

**Case Study**: Alandi–Pandharpur Dindi Wari, Maharashtra  
**System Component**: Module 9 – Dindi Route, Location & Wari Movement Management System  
**Integration Status**: Fully Integrated with Module 1 (Auth, User IDs `users.id`, Session Security, RBAC, Audit Logs), Module 2 (`person_profiles`, `families`), Module 3 (`medical_cases`), Module 4 (`lost_person_cases`), Module 5 (`found_person_cases`), Module 6 (`lost_item_cases`), Module 7 (`ai_match_results`), and Module 8 (`dindis`, `dindi_schedules`)  
**Date**: August 16, 2026  
**Document Version**: 9.0.0-PROD  

---

## 1. Module Objective
Module 9 establishes the geographical route model (`WS-ROUTE-2026-000001`), configurable route sections (Alandi → Pune → Saswad → Jejuri → Lonand → Phaltan → Malshiras → Pandharpur), Leaflet.js / OpenStreetMap interactive mapping, Dindi movement updates (`dindi_location_updates`), official checkpoint check-ins (`dindi_checkins`), nearby services search via Haversine distance, crowd congestion level tracking (`LOW`, `MODERATE`, `HIGH`, `SEVERE`), emergency zone markers, and route alert publishing for WariSeva during the Alandi–Pandharpur Dindi Wari.

The module provides location intelligence without performing invasive individual Warkari GPS tracking in the MVP.

---

## 2. Real-World Problem Statement
During the 250 km Alandi–Pandharpur Dindi Wari, over 250 registered Dindis and hundreds of thousands of Warkari pilgrims move across rural corridors.

Without centralized map and location intelligence:
- Pilgrims and families do not know where their Dindi is currently located.
- Warkaris in distress cannot find nearby medical camps or drinking water dispensers.
- Help desk operators cannot pinpoint emergency locations along route sections.
- Traffic and crowd bottlenecks at narrow ghat passes (e.g. Dive Ghat) create safety hazards.

WariSeva Module 9 provides a centralized map-based location intelligence system.

---

## 3. Main Actors & Access Scopes

| Actor | Key Responsibilities | Access Scope |
| :--- | :--- | :--- |
| **Warkari Pilgrim / Public** | View route map, find nearby medical/water/rest facilities, check crowd levels & alerts. | Public Wari Map & Nearby Services View |
| **Dindi Leader** | Submit Dindi GPS/manual location updates, check in at official checkpoints. | Dindi Location & Checkpoint Console |
| **Police / Security Officer**| Update crowd zone congestion levels (`LOW` -> `SEVERE`), publish route alerts. | Crowd Control & Alert Console |
| **Event Admin / Super Admin** | Configure Wari routes, add route sections & checkpoints, manage emergency zones. | Global Route Command Console |

---

## 4. Functional Requirements (FR)

- **FR-9.1 Modules 1–8 Integration**: Reuses existing `users`, `roles`, `permissions`, `families`, `person_profiles`, `dindis`, `medical_cases`, `lost_person_cases`, `found_person_cases`, `lost_item_cases`, `found_item_cases`, `ai_match_results`, and `audit_logs`.
- **FR-9.2 Configurable Wari Route**: Route `WS-ROUTE-2026-000001` with 7 configurable route sections spanning Alandi to Pandharpur.
- **FR-9.3 Interactive Leaflet.js Map**: Renders OpenStreetMap tiles, route polyline, and color-coded markers (Blue: Route, Green: Medical, Orange: Help Center, Cyan: Water, Purple: Dindi, Red: Emergency).
- **FR-9.4 Dindi Movement Updates**: Dindi leaders submit location updates (`GPS`, `MANUAL`, `CHECKPOINT`) stored in `dindi_location_updates`.
- **FR-9.5 Checkpoint Check-in**: Official passage check-ins stored in `dindi_checkins` (`PASSED`, `HALTED`, `DELAYED`).
- **FR-9.6 Haversine Nearby Facilities Search**: `GET /api/locations/nearby` calculates straight-line distance to nearby medical camps, help desks, water points, and rest spots.
- **FR-9.7 Crowd Congestion Levels**: Congestion levels tracked in `crowd_zones` (`LOW`, `MODERATE`, `HIGH`, `SEVERE`).
- **FR-9.8 Route Alerts & Emergency Zones**: Real-time route notices and emergency zone markers.

---

## 5. Database Schema & Data Models

### Summary of New Database Tables Created (9 Tables):
1. `wari_routes`: Wari route master records (`WS-ROUTE-2026-XXXXXX`).
2. `route_sections`: Route section breakdown with distance & duration.
3. `route_points`: GPS waypoints defining the route polyline.
4. `wari_locations`: Physical facilities, camps, water points, checkpoints.
5. `dindi_location_updates`: Dindi GPS/manual movement update history.
6. `dindi_checkins`: Official checkpoint check-in log.
7. `route_alerts`: Route notices and warning alerts.
8. `crowd_zones`: Crowd congestion level tracking by zone.
9. `emergency_zones`: Temporary emergency zone markers.

---

## 6. REST API Specifications

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/routes` | Event Admin | Create new Wari route (`WS-ROUTE-2026-XXXXXX`) |
| `GET` | `/api/routes` | Authenticated User | List all Wari routes and total distance |
| `POST` | `/api/routes/{id}/sections` | Event Admin | Add route section (e.g. Pune → Saswad) |
| `POST` | `/api/locations` | Event Admin / Police | Register facility location or checkpoint |
| `GET` | `/api/locations/nearby` | Authenticated User | Haversine nearby facilities search by lat/lon/radius |
| `POST` | `/api/dindis/{id}/location` | Leader / Admin | Submit Dindi location update (`GPS`/`MANUAL`) |
| `GET` | `/api/dindis/{id}/location` | Authenticated User | Get latest Dindi location and movement history |
| `POST` | `/api/checkpoints/{id}/checkin`| Leader / Admin | Check in at official route checkpoint |
| `PATCH` | `/api/crowd-zones/{id}` | Police / Admin | Update crowd congestion level (`LOW`..`SEVERE`) |
| `POST` | `/api/routes/alerts` | Police / Admin | Publish route notice or warning alert |

---

## 7. Test Cases & Validation Suite (`backend/tests/test_module9.py`)

| Test ID | Description | Input Data | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-9.1** | Haversine Distance | Alandi ↔ Pune | Calculated ~17.9 km accurately | **PASSED** |
| **TC-9.2** | Create Route | `Dehu->Pandharpur` | Route `WS-ROUTE-2026-000002` created, HTTP 201 | **PASSED** |
| **TC-9.3** | Add Route Section | Section `SEC-01-08` | Section added to route, HTTP 201 | **PASSED** |
| **TC-9.4** | Add Wari Location | `Jejuri Medical Tent` | Facility registered in `wari_locations` | **PASSED** |
| **TC-9.5** | Nearby Facilities Search | Saswad (18.345, 74.032) | Nearby facilities sorted by distance returned | **PASSED** |
| **TC-9.6** | Dindi Location Update | `GPS` coordinates | Record created in `dindi_location_updates` | **PASSED** |
| **TC-9.7** | Get Dindi History | Dindi ID #1 | Latest location and history timeline returned | **PASSED** |
| **TC-9.8** | Checkpoint Check-in | Checkpoint ID #4 | Check-in logged in `dindi_checkins` | **PASSED** |
| **TC-9.9** | Crowd Zone Status | `crowd_level="HIGH"`| Status updated in `crowd_zones` | **PASSED** |
| **TC-9.10**| Publish Route Alert | Priority `IMPORTANT` | Alert created in `route_alerts` | **PASSED** |
| **TC-9.11**| Audit Logging | Module 9 actions | Security events recorded in `audit_logs` | **PASSED** |

---

## 8. Security & Privacy Controls

1. **Location Privacy Protection**: Individual Warkari pilgrims are NOT tracked via continuous GPS. Dindi location updates are submitted at group-level by authorized Dindi leaders.
2. **Access Control**: Only authorized leaders and administrators can submit location updates and checkpoint check-ins.
3. **Haversine Distance**: Computes straight-line proximity for emergency facility discovery without storing personal tracking traces.
4. **Audit Logging**: All route creations, location updates, checkpoint check-ins, crowd level updates, and route alerts are recorded in `audit_logs`.
