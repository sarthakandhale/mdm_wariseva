# WariSeva – Multilingual Smart Platform for Medical Emergency, Lost Person & Item Assistance
## Master Data Management (MDM) & Software Engineering Documentation: Module 8 – Dindi Management & Warkari Group Coordination

**Case Study**: Alandi–Pandharpur Dindi Wari, Maharashtra  
**System Component**: Module 8 – Dindi Management & Warkari Group Coordination System  
**Integration Status**: Fully Integrated with Module 1 (Auth, User IDs `users.id`, Session Security, RBAC, Audit Logs), Module 2 (`person_profiles`, `families`), Module 3 (`medical_cases`), Module 4 (`lost_person_cases`), Module 5 (`found_person_cases`), Module 6 (`lost_item_cases`), and Module 7 (`ai_match_results`)  
**Date**: August 16, 2026  
**Document Version**: 8.0.0-PROD  

---

## 1. Module Objective
Module 8 establishes the digital Dindi group registration, leader assignment (`PRIMARY_LEADER`, `ASSISTANT_LEADER`), member enrollment (`dindi_memberships`), route schedule publishing, daily plans, Dindi-level announcements, emergency coordination shortcuts, and administrative verification system for WariSeva during the Alandi–Pandharpur Dindi Wari.

The module enables:
- Digital Dindi registration (`WS-DIN-2026-XXXXXX`) with separate internal unique code vs display Dindi number (e.g. Dindi No. 27).
- Relational membership link (`dindi_memberships`) connecting `dindis` to `person_profiles` without duplicating personal profile data.
- Leader command console for broadcasting announcements, managing daily march & rest schedules, and dispatching emergency assistance.
- Administrative Dindi verification (`VERIFIED`, `REJECTED`, `REQUIRES_UPDATE`) and document management.

---

## 2. Real-World Problem Statement
During the 250 km Alandi–Pandharpur Dindi Wari, over 250 registered Dindi groups carry Palkhis with thousands of Warkari pilgrims.

Without centralized digital Dindi management:
- Pilgrims who lose their group do not know where their Dindi is resting.
- Help desk operators cannot locate which Dindi a missing Warkari belongs to.
- Dindi leaders have no real-time roster of registered members or active emergency incidents.
- Emergency communications are delayed during crowd surges.

WariSeva Module 8 provides a structured digital Dindi coordination system.

---

## 3. Main Actors & Access Control

| Actor | Key Responsibilities | Access Scope |
| :--- | :--- | :--- |
| **Dindi Leader** | Manage Dindi members, publish daily halt schedules & announcements, trigger emergency assistance. | Own Dindi management console |
| **Assistant Leader** | Assist primary leader in member tracking, announcement publishing, and incident reporting. | Own Dindi operational console |
| **Warkari Member** | View enrolled Dindi schedule, rest points, announcements, emergency contacts. | Enrolled Dindi member view |
| **Event Admin / Super Admin** | Register new Dindis, assign primary leaders, verify Dindis, manage global route schedules. | Global Dindi admin console |

---

## 4. Functional Requirements (FR)

- **FR-8.1 Modules 1–7 Integration**: Reuses existing `users`, `roles`, `permissions`, `families`, `person_profiles`, `medical_cases`, `lost_person_cases`, `found_person_cases`, `lost_item_cases`, `found_item_cases`, `ai_match_results`, and `audit_logs`. Does NOT recreate user or profile tables.
- **FR-8.2 Identifier Generation**:
  - Dindi Code: `WS-DIN-2026-000001`
  - Display Dindi Number: `27`
- **FR-8.3 Relational Membership Architecture**: `dindis` connect to `person_profiles` via `dindi_memberships`, allowing Warkaris to belong to a Dindi without profile duplication.
- **FR-8.4 Leader Assignment**: Primary leaders and assistant leaders assigned in `dindi_leaders` table.
- **FR-8.5 Daily Schedule & Halt Plan**: Configurable march and rest schedules stored in `dindi_schedules`.
- **FR-8.6 Dindi Announcements**: Broadcast announcements stored in `dindi_announcements` with priority levels (`NORMAL`, `IMPORTANT`, `URGENT`).
- **FR-8.7 Emergency Coordination Shortcuts**: Direct API integration with Module 3 Medical, Module 4 Lost Person, Module 5 Found Person, and Module 6 Lost Item APIs passing `dindi_id`.
- **FR-8.8 Administrative Verification**: Admin verifies Dindi registration status in `dindi_verifications`.

---

## 5. Database Schema & Data Models

### Summary of New Database Tables Created (9 Tables):
1. `dindis`: Core Dindi group records.
2. `dindi_leaders`: Primary and assistant leader assignments.
3. `dindi_memberships`: Relational membership records connecting Dindi ↔ Person Profile.
4. `dindi_schedules`: Daily march, halt, and rest point schedules.
5. `dindi_announcements`: Broadcast announcements.
6. `dindi_contacts`: Public and emergency contacts.
7. `dindi_verifications`: Admin verification records.
8. `dindi_documents`: Official registration documents.
9. `dindi_route_associations`: Sequence mapping to Module 9 route framework.

---

## 6. REST API Specifications

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/dindis` | Leader / Admin | Register new Dindi group (`WS-DIN-2026-XXXXXX`) |
| `GET` | `/api/dindis` | Authenticated User | List Dindi directory with search filters |
| `GET` | `/api/dindis/{id}` | Authenticated User | Get Dindi details, leaders, schedules, announcements |
| `POST` | `/api/dindis/{id}/members` | Leader / Admin | Enroll person profile into Dindi membership |
| `GET` | `/api/dindis/{id}/members` | Leader / Admin | List enrolled Dindi members |
| `POST` | `/api/dindis/{id}/leaders` | Event Admin | Assign primary or assistant leader |
| `POST` | `/api/dindis/{id}/schedule` | Leader / Admin | Publish daily march & rest schedule |
| `POST` | `/api/dindis/{id}/announcements` | Leader / Admin | Publish broadcast announcement to members |
| `POST` | `/api/dindis/{id}/verify` | Event Admin | Verify Dindi registration (`VERIFIED`/`REJECTED`) |

---

## 7. Test Cases & Validation Suite (`backend/tests/test_module8.py`)

| Test ID | Description | Input Data | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-8.1** | Create Dindi | `dindi_number=99` | Dindi `WS-DIN-2026-000099` created, HTTP 201 | **PASSED** |
| **TC-8.2** | Duplicate Number Check | `dindi_number=27` | Duplicate rejected with HTTP 400 Bad Request | **PASSED** |
| **TC-8.3** | Get Dindi Details | Dindi ID #1 | Full details, schedules, announcements returned | **PASSED** |
| **TC-8.4** | Enroll Dindi Member | `person_id=1`, `role="MEMBER"` | Member enrolled in `dindi_memberships` | **PASSED** |
| **TC-8.5** | Duplicate Membership | `person_id=1` again | Duplicate membership rejected with HTTP 400 | **PASSED** |
| **TC-8.6** | Assign Leader | `user_id=6`, `ASSISTANT_LEADER` | Leader record created in `dindi_leaders` | **PASSED** |
| **TC-8.7** | Create Schedule | `start="Jejuri"`, `end="Lonand"` | Schedule item published, HTTP 201 | **PASSED** |
| **TC-8.8** | Create Announcement | Priority `URGENT` | Announcement published, HTTP 201 | **PASSED** |
| **TC-8.9** | Verify Dindi Status | Admin token, `VERIFIED` | Status updated to `VERIFIED` | **PASSED** |
| **TC-8.10**| Audit Logging | Module 8 actions | Security events recorded in `audit_logs` | **PASSED** |

---

## 8. Security & Privacy Controls

1. **RBAC & Authorization**: Dindi leaders can only manage member rosters and publish schedules for their assigned Dindi.
2. **Privacy Protection**: Public views display Dindi name, display number, leader name, and rest point locations. Private member contact numbers and Aadhaar/ID numbers are strictly protected.
3. **Relational Integrity**: Prevents profile duplication across Dindis.
4. **Audit Logging**: All Dindi creation, leader assignments, member enrollments, schedule updates, and verification decisions are logged in `audit_logs`.
