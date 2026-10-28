# WariSeva – Multilingual Smart Platform for Medical Emergency, Lost Person & Item Assistance
## Master Data Management (MDM) & Software Engineering Documentation: Module 3 – Medical Emergency Assistance

**Case Study**: Alandi–Pandharpur Dindi Wari, Maharashtra  
**System Component**: Module 3 – Medical Emergency Assistance  
**Integration Status**: Fully Integrated with Module 1 (Auth, Session Security, User IDs `users.id`, RBAC, Audit Logging) and Module 2 (`person_profiles`, `families`, `emergency_contacts`)  
**Date**: August 16, 2026  
**Document Version**: 3.0.0-PROD  

---

## 1. Module Objective
Module 3 provides a centralized digital workflow for reporting, triaging, dispatching, treating, referring, and closing medical emergency cases during the Alandi–Pandharpur Dindi Wari.

The module enables:
- Fast emergency reporting for self, registered family members (from Module 2), or unidentified victims (`TEMP-PAT-2026-XXXXX`).
- Deterministic, rule-based medical priority calculation (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- Configurable Dindi route zone tracking (Alandi, Pune Route, Saswad, Jejuri, Lonand, Phaltan, Malshiras, Pandharpur).
- Medical camp and hospital capacity & service capability tracking.
- Ambulance dispatch and response tracking (`WS-AMB-2026-XXXXXX`).
- Clinical treatment and referral recording (restricted to authorized medical personnel with full audit logging).
- Multilingual foundation for Marathi, Hindi, and English UI labels.

---

## 2. Real-World Problem Statement
During the Alandi–Pandharpur Dindi Wari, hundreds of thousands of Warkaris walk over 250 kilometers under intense heat and crowded conditions. Frequent emergencies include dehydration, heat exhaustion, fainting, foot injuries, fractures, chest pain, and cardiac distress.

Historically, pilgrims faced major challenges:
- Difficulty discovering nearest operational medical camps or hospitals.
- Lack of visibility into camp capacity or available ambulances.
- Inability to quickly communicate exact locations along the moving Palkhi route.

WariSeva solves these challenges by connecting pilgrims, family members, volunteers, medical staff, ambulance drivers, and emergency coordinators through a real-time REST API platform.

---

## 3. Main Actors & Access Control

| Actor | Key Responsibilities | Access Scope |
| :--- | :--- | :--- |
| **Warkari / Pilgrim** | Report emergency for self or family, track ambulance, find nearby medical camps. | Own & family cases only |
| **Family Guardian** | Report & track emergencies for registered Module 2 family members. | Family group cases |
| **Volunteer** | Report emergency for unidentified pilgrims (`TEMP-PAT-2026-XXXXX`), assist with GPS location. | Create & view assigned cases |
| **Medical Staff (Doctor/Nurse/Paramedic)** | Perform triage, update case status, record clinical treatments & medication, initiate referrals. | Full clinical read/write |
| **Ambulance Operator** | Receive dispatch alerts, update transit status (`DISPATCHED`, `ARRIVED`, `COMPLETED`). | Ambulance assignments |
| **Emergency Coordinator / Admin** | Monitor real-time medical dashboard, assign ambulances & staff, manage camp capacities. | Platform-wide operational access |

---

## 4. Functional Requirements (FR)

- **FR-3.1 Module Integration**: Reuses existing `users`, `roles`, `permissions`, `user_sessions`, `families`, `person_profiles`, `emergency_contacts`, and `audit_logs`. Does NOT create duplicate user or authentication tables.
- **FR-3.2 Patient Selection**:
  - Registered Warkari / Self: links to `person_profiles.id` or `users.id`.
  - Registered Family Member: links to Module 2 `person_profiles.id`.
  - Unidentified / Other: sets `patient_person_id = NULL` and generates temporary patient code (`TEMP-PAT-2026-XXXXX`).
- **FR-3.3 Unique Case Numbering**: Backend generates unique Case ID (`WS-MED-2026-000001`).
- **FR-3.4 Rule-Based Priority Engine**: Calculates priority score and level without machine learning:
  - Unconsciousness / Fainting: +40
  - Breathing difficulty / Chest pain: +35
  - Severe bleeding / Accident / Fracture: +35
  - Dehydration / Heat exhaustion / Allergic reaction: +20
  - Child ($\le 12$) / Elderly ($\ge 60$): +15
  - Known serious medical condition: +20
  - High-density route zone: +10
  - Priority levels: $0-24 \implies \text{LOW}$, $25-49 \implies \text{MEDIUM}$, $50-74 \implies \text{HIGH}$, $\ge 75 \implies \text{CRITICAL}$.
- **FR-3.5 Location Capture**: Captures `zone`, `route`, `landmark`, `latitude`, `longitude`, `location_description`, and `location_source` (`GPS`, `MAP`, `MANUAL`, `VOLUNTEER`, `MEDICAL_CAMP`).
- **FR-3.6 Workflow Status Transition**: Supports `REPORTED` ➔ `TRIAGE` ➔ `ASSIGNED` ➔ `RESPONDING` ➔ `ARRIVED` ➔ `TREATMENT` ➔ `REFERRED` / `OBSERVATION` / `RESOLVED` / `CANCELLED` / `CLOSED`.
- **FR-3.7 Nearest Facility Recommendation**: Calculates Haversine distance from patient location to medical camps & hospitals, returning estimated response times and service capabilities.
- **FR-3.8 Ambulance Dispatch**: Request and assign ambulances (`WS-AMB-101`), updating status in real-time.
- **FR-3.9 Confidential Treatment Record**: Restricted to authorized medical staff (`DOCTOR`, `NURSE`, `PARAMEDIC`, `MEDICAL_COORDINATOR`, `SUPER_ADMIN`). Ordinary volunteers/Warkaris are blocked with HTTP `403 Forbidden`.
- **FR-3.10 Multilingual Foundation**: Frontend UI utilizes dictionary translation keys (`medical.report_emergency`, `medical.critical_case`, `medical.nearest_camp`) supporting English, Marathi, and Hindi.

---

## 5. Non-Functional Requirements (NFR)

- **NFR-3.1 Response Speed**: Emergency reporting API processes under **50ms**.
- **NFR-3.2 Privacy & Compliance**: Detailed medical assessments and medications are masked for non-medical roles and logged in `audit_logs`.
- **NFR-3.3 Availability**: Operates reliably under high pilgrim load along the Palkhi route.
- **NFR-3.4 Dynamic Route Configuration**: Route zones are stored in configurable database tables, allowing platform reuse in future Wari events.

---

## 6. Database Schema & Data Models

### Summary of New Database Tables Created:
1. `medical_cases`: Core case record with priority scores, status, and patient references.
2. `medical_case_locations`: Location, GPS coordinates, landmark, and Wari zone.
3. `medical_case_symptoms`: Observed symptoms and severities.
4. `medical_facilities`: Medical camps, hospitals, first aid centers, capacity, and current patient count.
5. `medical_facility_services`: Facility services (First Aid, Dehydration Treatment, Cardiac Support, Pharmacy, etc.).
6. `medical_staff`: Staff profiles, roles (`DOCTOR`, `NURSE`, `PARAMEDIC`), specialization, and assigned camp.
7. `ambulances`: Fleet list, registration number, type, driver contact, GPS position, and status.
8. `ambulance_assignments`: Case-to-ambulance dispatch assignments.
9. `medical_treatments`: Clinical diagnosis, treatment provided, medication, and observation notes.
10. `medical_referrals`: Hospital referral records with transfer reasons and ambulance requirements.
11. `medical_case_status_history`: Audit history of case status transitions.

---

## 7. REST API Specifications

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/medical/cases` | Authenticated User | File a new medical emergency case |
| `GET` | `/api/medical/cases` | Authenticated User | List cases (with status, priority, zone filters) |
| `GET` | `/api/medical/cases/{id}` | Authenticated User | Get case details, location, symptoms, timeline |
| `PATCH` | `/api/medical/cases/{id}/status` | Authenticated User | Transition case status (`TRIAGE`, `RESOLVED`, etc.) |
| `POST` | `/api/medical/cases/{id}/ambulance` | Authenticated User | Request ambulance for emergency case |
| `POST` | `/api/medical/cases/{id}/assign` | Medical Staff / Admin | Assign ambulance & dispatch driver |
| `POST` | `/api/medical/cases/{id}/treatment` | Medical Staff Only | Record clinical treatment & medication |
| `POST` | `/api/medical/cases/{id}/referral` | Medical Staff Only | Create hospital referral record |
| `GET` | `/api/medical/facilities` | Public / Auth | List medical camps & hospitals |
| `GET` | `/api/medical/facilities/nearby` | Public / Auth | Get nearby recommended camps by GPS distance |
| `GET` | `/api/medical/ambulances` | Public / Auth | List ambulance fleet status |
| `GET` | `/api/medical/dashboard` | Authenticated User | Summary metrics for medical dashboard |

---

## 8. Test Cases & Validation Suite (`backend/tests/test_module3.py`)

| Test ID | Description | Input Data | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-3.1** | Report Emergency for Family Member | `patient_person_id=4`, `BREATHING_DIFFICULTY` | Case `WS-MED-2026-XXXXXX` created, Priority `CRITICAL` ($\ge 75$) | **PASSED** |
| **TC-3.2** | Report Emergency for Unidentified Victim | `temp_patient_name="Unconscious Pilgrim"` | `patient_person_id=NULL`, `TEMP-PAT-2026-XXXXX` generated | **PASSED** |
| **TC-3.3** | Priority Calculation Engine | Chest Pain + Breathing + Elderly + Unconscious | Priority score $\ge 75$, Level `CRITICAL` | **PASSED** |
| **TC-3.4** | Request & Assign Ambulance | `case_id=1`, `ambulance_id=1` | Ambulance status updated to `ASSIGNED`, dispatch time logged | **PASSED** |
| **TC-3.5** | Record Clinical Treatment | Doctor user token, treatment payload | Record saved, status set to `TREATMENT`, HTTP 201 | **PASSED** |
| **TC-3.6** | Unauthorized Treatment Record | Volunteer user token, treatment payload | HTTP 403 Forbidden returned | **PASSED** |
| **TC-3.7** | Record Hospital Referral | Doctor user token, referral payload | Referral created, status set to `REFERRED` | **PASSED** |
| **TC-3.8** | Case Status Transition | `status="RESOLVED"` | Case closed, status history updated | **PASSED** |
| **TC-3.9** | Facilities & Nearby Finder | GPS lat/lon | Facilities sorted by Haversine distance | **PASSED** |
| **TC-3.10** | Ambulances & Dashboard APIs | Valid session token | Dashboard metrics (active, critical, camps) returned | **PASSED** |
| **TC-3.11** | Security Audit Logging | Module 3 actions | Audit events recorded in `audit_logs` | **PASSED** |

---

## 9. Security & Privacy Controls

1. **Medical Record Confidentiality**: Treatment details (`medical_treatments`) are restricted to authorized medical personnel (`DOCTOR`, `NURSE`, `PARAMEDIC`, `MEDICAL_COORDINATOR`, `SUPER_ADMIN`). Attempts by non-medical users return HTTP `403 Forbidden`.
2. **Audit Trails**: All case creations, ambulance dispatches, treatment recordings, and referrals write security entries into `audit_logs`.
3. **Data Minimization**: Family notifications and public case trackers display only high-level status without exposing confidential clinical diagnoses.
