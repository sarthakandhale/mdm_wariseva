# WariSeva – Multilingual Smart Platform for Medical Emergency, Lost Person & Item Assistance
## Master Data Management (MDM) & Software Engineering Documentation: Module 10 – Volunteer Management & Task Assignment

**Case Study**: Alandi–Pandharpur Dindi Wari, Maharashtra  
**System Component**: Module 10 – Volunteer Management & Task Assignment System  
**Integration Status**: Fully Integrated with Module 1 (Auth, User IDs `users.id`, Session Security, RBAC, Audit Logs), Module 2 (`person_profiles`, `families`), Module 3 (`medical_cases`), Module 4 (`lost_person_cases`), Module 5 (`found_person_cases`), Module 6 (`lost_item_cases`), Module 7 (`ai_match_results`), Module 8 (`dindis`), and Module 9 (`wari_locations`, `route_sections`)  
**Date**: August 16, 2026  
**Document Version**: 10.0.0-PROD  

---

## 1. Module Objective
Module 10 establishes the volunteer registration (`WS-VOL-2026-000001`), verification (`PENDING`, `VERIFIED`), skills (`FIRST_AID`, `CROWD_MANAGEMENT`, `LANGUAGE_SUPPORT`, `CHILD_ASSISTANCE`), language proficiencies, shifts, attendance check-in/out, teams, centralized task management (`WS-TASK-2026-000001`), rule-based assignment recommendation engine (100% weighted score), human-in-the-loop coordinator approval workflow, volunteer task acceptance/decline, completion verification, and workload tracking for WariSeva during the Alandi–Pandharpur Dindi Wari.

The system prevents duplicate user accounts, enforces duty location privacy, and ensures task assignments are transparently recommended to human coordinators rather than automatically dispatched without authorization.

---

## 2. Real-World Problem Statement
During the Alandi–Pandharpur Wari, thousands of volunteers assist Warkari pilgrims across medical tents, help centers, lost person searches, crowd guidance, and water distribution desks.

Without centralized volunteer coordination:
- Volunteers report to unneeded locations while emergency zones remain understaffed.
- Multiple volunteers are dispatched to the same lost child search.
- Volunteers are assigned tasks outside their skill or language capability.
- Overworked volunteers suffer fatigue while available volunteers remain idle.

WariSeva Module 10 provides structured volunteer coordination and intelligent task recommendation.

---

## 3. Main Actors & Access Control

| Actor | Key Responsibilities | Access Scope |
| :--- | :--- | :--- |
| **Volunteer** | Register skills/availability, check in/out for shifts, accept/decline tasks, submit completion notes. | Own Volunteer Desk & Assigned Tasks |
| **Volunteer Team Leader** | Oversee team members, view shift availability, dispatch internal team tasks. | Team Operational Console |
| **Volunteer Coordinator** | Review rule-based task recommendations, assign volunteers, verify task completions. | Coordinator Command Console |
| **Event Admin / Super Admin** | Approve volunteer registrations, manage skill categories, configure shifts, view capacity reports. | Global Volunteer Admin Console |

---

## 4. Functional Requirements (FR)

- **FR-10.1 Modules 1–9 Integration**: Reuses existing `users`, `roles`, `person_profiles`, `dindis`, `medical_cases`, `lost_person_cases`, `found_person_cases`, `lost_item_cases`, `found_item_cases`, `wari_locations`, and `audit_logs`. Does NOT recreate user or profile tables.
- **FR-10.2 Volunteer Code Generation**: `WS-VOL-2026-000001` (unique, backend generated).
- **FR-10.3 Task Code Generation**: `WS-TASK-2026-000001` (unique, backend generated).
- **FR-10.4 Skill & Language Matrix**: Configurable skills (`FIRST_AID`, `CROWD_MANAGEMENT`, `LANGUAGE_SUPPORT`, `CHILD_ASSISTANCE`) with proficiency levels.
- **FR-10.5 Shift & Attendance Tracking**: Shift registration and check-in/out (`ON_DUTY`, `OFF_DUTY`).
- **FR-10.6 100% Rule-Based Recommendation Engine**:
  - Skill Match: 30%
  - Zone Match: 20%
  - Availability Match: 15%
  - Language Match: 15%
  - Workload Balance: 10%
  - Experience Level: 10%
  - **Total**: 100%
  - Generates candidate suitability scores labeled **`System Recommendation`** for coordinator approval.
- **FR-10.7 Volunteer Task Acceptance**: Volunteers accept or decline tasks with reason.
- **FR-10.8 Two-Stage Completion Verification**: Volunteer submits `COMPLETED`; coordinator verifies and marks `VERIFIED`.
- **FR-10.9 Workload Cap Enforcement**: Maximum 3 active tasks per volunteer to prevent burnout.

---

## 5. Database Schema & Data Models

### Summary of New Database Tables Created (14 Tables):
1. `volunteers`: Core volunteer profile master records (`WS-VOL-2026-XXXXXX`).
2. `volunteer_skills`: Skill matrix with verification status.
3. `volunteer_languages`: Language proficiencies (`Marathi`, `Hindi`, `English`, `Odia`, etc.).
4. `volunteer_availability`: Date and time slot availability.
5. `volunteer_shifts`: Configured shifts (`SHIFT-MNG-01`, etc.).
6. `volunteer_attendance`: Shift check-in and check-out logs.
7. `volunteer_teams`: Functional teams (`MEDICAL`, `LOST_PERSON`, `HELP_CENTER`, etc.).
8. `volunteer_team_members`: Team membership mapping.
9. `volunteer_tasks`: Centralized task records (`WS-TASK-2026-XXXXXX`).
10. `volunteer_task_requirements`: Required skills, minimum level, and language for tasks.
11. `volunteer_task_assignments`: Volunteer task assignment status log (`ASSIGNED`, `ACCEPTED`, `DECLINED`, `COMPLETED`, `VERIFIED`).
12. `volunteer_task_history`: Audit state transition log.
13. `volunteer_location_updates`: Duty location updates (active ONLY while `ON_DUTY`).
14. `volunteer_recommendations`: Rule-based recommendation score breakdown records.

---

## 6. REST API Specifications

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/volunteers` | Authenticated User | Register as volunteer (`WS-VOL-2026-XXXXXX`) |
| `GET` | `/api/volunteers` | Coordinator / Admin | List volunteers with zone and status filters |
| `PATCH` | `/api/volunteers/{id}/status` | Event Admin | Verify volunteer status (`VERIFIED`/`REJECTED`) |
| `POST` | `/api/volunteers/{id}/check-in`| Volunteer | Check in for shift (`ON_DUTY`) |
| `POST` | `/api/volunteers/{id}/check-out`| Volunteer | Check out from shift (`OFFLINE`) |
| `POST` | `/api/volunteer-tasks` | Help Center / Admin | Create volunteer task (`WS-TASK-2026-XXXXXX`) |
| `GET` | `/api/volunteer-tasks/{id}/recommendations` | Coordinator | Get rule-based candidate assignment recommendations |
| `POST` | `/api/volunteer-tasks/{id}/assign` | Coordinator | Assign task to recommended volunteer |
| `POST` | `/api/volunteer-tasks/{id}/accept` | Volunteer | Accept assigned task |
| `POST` | `/api/volunteer-tasks/{id}/decline`| Volunteer | Decline assigned task with reason |
| `POST` | `/api/volunteer-tasks/{id}/complete`| Volunteer | Submit task completion notes |
| `POST` | `/api/volunteer-tasks/{id}/verify`  | Coordinator | Verify task completion |

---

## 7. Test Cases & Validation Suite (`backend/tests/test_module10.py`)

| Test ID | Description | Input Data | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-10.1**| Register Volunteer | `experience=4` | Volunteer `WS-VOL-2026-000003` created, HTTP 201 | **PASSED** |
| **TC-10.2**| Verify Volunteer | Admin token, `VERIFIED` | Status updated to `VERIFIED` | **PASSED** |
| **TC-10.3**| Shift Check-in/Out | Shift ID #1 | Attendance status updated (`ON_DUTY` -> `OFFLINE`) | **PASSED** |
| **TC-10.4**| Create Task | `Lost Child Search` | Task `WS-TASK-2026-000002` created, HTTP 201 | **PASSED** |
| **TC-10.5**| Recommendation Engine | Task ID #1 | 100% weighted suitability scores calculated | **PASSED** |
| **TC-10.6**| Assign & Accept | Vol ID #1 | Task assigned and accepted by volunteer | **PASSED** |
| **TC-10.7**| Complete & Verify | Completion notes | Task marked `COMPLETED` then `VERIFIED` | **PASSED** |
| **TC-10.8**| Decline Task Flow | Reason provided | Task declined and reverted to `UNASSIGNED` | **PASSED** |
| **TC-10.9**| Audit Logging | Module 10 actions | Security events recorded in `audit_logs` | **PASSED** |

---

## 8. Security & Privacy Controls

1. **Minimum Disclosure Policy**: Ground volunteers receive only essential task parameters (search zone, clothing description) without exposing sensitive family telephone numbers, Aadhaar IDs, or full medical histories.
2. **Duty Location Privacy**: Location updates are permitted ONLY while a volunteer is checked in (`ON_DUTY`). Off-duty tracking is strictly blocked.
3. **Human Approval**: Automated recommendations are labeled **`System Recommendation`**; coordinator review is mandatory prior to dispatch.
4. **Audit Logging**: All volunteer registrations, verifications, shift check-ins, task creations, assignments, acceptances, completions, and coordinator verifications are recorded in `audit_logs`.
