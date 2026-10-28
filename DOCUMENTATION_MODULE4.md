# WariSeva – Multilingual Smart Platform for Medical Emergency, Lost Person & Item Assistance
## Master Data Management (MDM) & Software Engineering Documentation: Module 4 – Lost Person Assistance & Missing Case Management

**Case Study**: Alandi–Pandharpur Dindi Wari, Maharashtra  
**System Component**: Module 4 – Lost Person Assistance & Missing Case Management  
**Integration Status**: Fully Integrated with Module 1 (Auth, User IDs `users.id`, Session Security, RBAC, Audit Logs), Module 2 (`families`, `person_profiles`, `clothing_profiles`, `emergency_contacts`), and Module 3 (`medical_cases`)  
**Date**: August 16, 2026  
**Document Version**: 4.0.0-PROD  

---

## 1. Module Objective
Module 4 establishes the digital missing person case management workflow for WariSeva during the Alandi–Pandharpur Dindi Wari.

The module enables:
- Missing person reporting for registered family members (from Module 2) or unregistered pilgrims (`TEMP-PER-2026-XXXXX`).
- Duplicate active case detection to prevent duplicate case creation.
- Case-specific last seen location and clothing descriptions without mutating permanent `person_profiles`.
- Deterministic, rule-based missing person priority calculation (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) with authorized police priority override capabilities.
- Case status tracking (`DRAFT`, `REPORTED`, `UNDER_REVIEW`, `SEARCHING`, `POSSIBLE_SIGHTING`, `WITHDRAWN`, `CLOSED`).
- Public sighting reports and search support requests for volunteer teams.
- Role-based case notes (`INTERNAL` vs `FAMILY_VISIBLE`).

---

## 2. Real-World Problem Statement
During the Alandi–Pandharpur Dindi Wari, hundreds of thousands of Warkaris walk together over long distances. High crowd density, differing walking paces, rest stops, phone battery depletion, and disorientation among children and elderly pilgrims frequently lead to family separation.

Historically, families relied on physical announcements, asking bystanders, or visiting distant police tents. Module 4 replaces these fragmented efforts with a centralized digital case management workflow accessible by family guardians, volunteers, police officers, and help center operators.

---

## 3. Main Actors & Access Control

| Actor | Key Responsibilities | Access Scope |
| :--- | :--- | :--- |
| **Parent / Family Guardian** | File missing report for family members, view status, submit updates, request case withdrawal. | Own family's cases |
| **Volunteer** | File report for unregistered missing pilgrims (`TEMP-PER-2026-XXXXX`), report sightings. | Sighting submission & assigned cases |
| **Police Officer** | Review missing cases, override priority scores, add internal operational notes, request search support. | Full police operational access |
| **Help Center Operator** | File and review missing reports, log public sightings, update case timeline. | Help desk operational access |
| **Event Administrator** | Global operational monitoring and audit verification. | Platform-wide access |

---

## 4. Functional Requirements (FR)

- **FR-4.1 Module Integration**: Reuses existing `users`, `roles`, `permissions`, `user_sessions`, `families`, `person_profiles`, `clothing_profiles`, `emergency_contacts`, and `audit_logs`. Does NOT create duplicate user or person profile tables.
- **FR-4.2 Duplicate Active Case Prevention**: Before creating a report, checks if the person already has an active case (`REPORTED`, `UNDER_REVIEW`, `SEARCHING`, `POSSIBLE_SIGHTING`, `POSSIBLE_MATCH`, `VERIFICATION`). If active, creation is blocked with HTTP `409 Conflict`.
- **FR-4.3 Temporary Person Profiles**: For unregistered pilgrims, sets `person_id = NULL` and generates temporary profile identifier `TEMP-PER-2026-XXXXX`.
- **FR-4.4 Case ID Generation**: Backend generates immutable Case ID (`WS-LP-2026-000001`).
- **FR-4.5 Rule-Based Priority Engine**: Calculates missing person priority deterministically:
  - Child ($\le 12$): +30
  - Elderly ($\ge 60$): +25
  - Medical requirement: +25
  - Cognitive assistance required (e.g. Memory loss): +25
  - Communication difficulty / Non-verbal: +20
  - Night-time disappearance (20:00 to 06:00): +10
  - High-density route zone: +10
  - Long duration missing ($>2$ hours): +10
  - Priority levels: $0-24 \implies \text{LOW}$, $25-49 \implies \text{MEDIUM}$, $50-74 \implies \text{HIGH}$, $\ge 75 \implies \text{CRITICAL}$.
- **FR-4.6 Police Priority Override**: Authorized police officers can override calculated priority, logging original score, new priority, reason, officer ID, and timestamp.
- **FR-4.7 Case-Specific Information Preservation**: Clothing and last seen details are stored in `lost_person_clothing` and `lost_person_cases` without overwriting permanent `person_profiles`.
- **FR-4.8 Sightings & Search Requests**: Public observers can file sighting reports (`lost_person_sightings`). Operators can dispatch volunteer search requests (`lost_person_search_requests`).
- **FR-4.9 Case Withdrawal**: Family guardians can withdraw reports (`status = 'WITHDRAWN'`), storing withdrawal reasons without deleting historical records.
- **FR-4.10 AI Boundary**: AI facial recognition and matching are strictly excluded from Module 4 and isolated to Module 7.

---

## 5. Database Schema & Data Models

### Summary of New Database Tables Created:
1. `lost_person_cases`: Core case record with priority scores, status, and patient references.
2. `lost_person_locations`: Last seen zone, route section, landmark, GPS coordinates.
3. `lost_person_clothing`: Case-specific clothing worn at disappearance.
4. `lost_person_status_history`: Audit history of case status transitions.
5. `lost_person_attachments`: Photos and evidence attachments.
6. `lost_person_notes`: Case notes with `INTERNAL` vs `FAMILY_VISIBLE` visibility controls.
7. `lost_person_search_requests`: Volunteer search support requests.
8. `lost_person_sightings`: Sighting reports from public observers and volunteers.

---

## 6. REST API Specifications

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/lost-person/cases` | Authenticated User | File a new lost person missing case |
| `GET` | `/api/lost-person/cases` | Authenticated User | List lost person cases (with status, priority, zone filters) |
| `GET` | `/api/lost-person/cases/{id}` | Authenticated User | Get lost person case details, location, clothing, notes |
| `PATCH` | `/api/lost-person/cases/{id}/status` | Authenticated User | Update case status (`SEARCHING`, `UNDER_REVIEW`, etc.) |
| `PATCH` | `/api/lost-person/cases/{id}/priority` | Police / Help Center | Override missing person priority level |
| `POST` | `/api/lost-person/cases/{id}/withdraw` | Reporter / Guardian | Request case withdrawal (`WITHDRAWN`) |
| `POST` | `/api/lost-person/cases/{id}/notes` | Authenticated User | Add case note (`INTERNAL` or `FAMILY_VISIBLE`) |
| `POST` | `/api/lost-person/cases/{id}/sightings` | Authenticated User | Report possible sighting of missing person |
| `POST` | `/api/lost-person/cases/{id}/search-request` | Authenticated User | Request volunteer search support |
| `GET` | `/api/persons/{person_id}/active-lost-case` | Authenticated User | Check active missing case for person |

---

## 7. Test Cases & Validation Suite (`backend/tests/test_module4.py`)

| Test ID | Description | Input Data | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-4.1** | Report Lost Person for Family Member | `person_id=1`, `family_id=1` | Case `WS-LP-2026-XXXXXX` created, HTTP 201 | **PASSED** |
| **TC-4.2** | Duplicate Active Case Prevention | Active `person_id=3` | Creation blocked with HTTP 409 Conflict | **PASSED** |
| **TC-4.3** | Unregistered Missing Pilgrim | `temp_person_name="Child"` | `person_id=NULL`, `TEMP-PER-2026-XXXXX` generated | **PASSED** |
| **TC-4.4** | Priority Engine Engine | Child + Medical condition | Priority score $\ge 75$, Level `CRITICAL` | **PASSED** |
| **TC-4.5** | Police Priority Override | Police token, `CRITICAL` | Priority level updated, override logged | **PASSED** |
| **TC-4.6** | Add Case Note | Note payload, `FAMILY_VISIBLE` | Note saved, visible to family | **PASSED** |
| **TC-4.7** | Report Sighting | Sighting location & description | Sighting logged, status updated to `POSSIBLE_SIGHTING` | **PASSED** |
| **TC-4.8** | Withdraw Lost Case | Guardian token, withdrawal reason | Case status set to `WITHDRAWN`, HTTP 200 | **PASSED** |
| **TC-4.9** | Audit Logging | Module 4 actions | Audit events recorded in `audit_logs` | **PASSED** |

---

## 8. Security & Privacy Controls

1. **IDOR & Ownership Verification**: API endpoints verify caller permissions and ownership of `family_id` / `person_id` before granting read or edit access.
2. **Data Minimization for Children**: Public sighting portals and volunteer alerts display only necessary physical features and clothing descriptions without exposing sensitive medical or financial records.
3. **Internal Operational Notes**: Case notes marked as `INTERNAL` are restricted to Police and Help Center personnel and hidden from ordinary users.
