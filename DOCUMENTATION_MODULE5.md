# WariSeva – Multilingual Smart Platform for Medical Emergency, Lost Person & Item Assistance
## Master Data Management (MDM) & Software Engineering Documentation: Module 5 – Found Person Assistance & Safe Custody Management

**Case Study**: Alandi–Pandharpur Dindi Wari, Maharashtra  
**System Component**: Module 5 – Found Person Assistance & Safe Custody Management  
**Integration Status**: Fully Integrated with Module 1 (Auth, User IDs `users.id`, Session Security, RBAC, Audit Logs), Module 2 (`person_profiles`, `families`), Module 3 (`medical_cases`, `medical_facilities`), and Module 4 (`lost_person_cases`)  
**Date**: August 16, 2026  
**Document Version**: 5.0.0-PROD  

---

## 1. Module Objective
Module 5 establishes the digital found person registration and safe custody management workflow for WariSeva during the Alandi–Pandharpur Dindi Wari.

The module enables:
- Registration of found persons categorized into `IDENTIFIED_PERSON`, `PARTIALLY_IDENTIFIED_PERSON`, or `UNIDENTIFIED_PERSON`.
- Generation of temporary found-person profile identifiers (`TEMP-FP-PER-2026-XXXXX`) without creating permanent user or profile records.
- Placement of found pilgrims at authorized safe assistance locations (`HELP_CENTER`, `POLICE_POST`, `MEDICAL_CAMP`, `DINDI_CAMP`) with arrival and custody tracking.
- Seamless medical integration with Module 3 if the found person requires medical treatment (`medical_case_id`).
- Recording of verbal clues (`found_person_identification_clues`), family contact attempts (`found_person_family_contacts`), identity verification (`found_person_verifications`), and formal human-verified reunification handovers (`found_person_reunifications`).
- Structured data preparation for future Module 7 AI matching without implementing facial recognition inside Module 5.

---

## 2. Real-World Problem Statement
During the Alandi–Pandharpur Dindi Wari, lost children, disoriented elderly pilgrims, or non-verbal individuals are frequently discovered by volunteers, Dindi leaders, or police patrols.

Previously, found persons were brought to local police tents or makeshift help desks without centralized records, making it difficult for searching families to locate them across different halts. Module 5 provides a unified digital registry and safe custody workflow accessible to authorized personnel across the route.

---

## 3. Main Actors & Access Control

| Actor | Key Responsibilities | Access Scope |
| :--- | :--- | :--- |
| **Volunteer** | Report found person, record verbal clues, assign initial help center placement. | Found person case creation & view |
| **Police Officer** | Review cases, perform identity verification, authorize official reunification handover. | Full police operational access |
| **Help Center Operator** | Manage safe custody placement, log family contact attempts, update status. | Help desk operational access |
| **Medical Staff** | Assess medical needs, link Module 3 medical cases if medical attention is required. | Clinical triage & case access |
| **Dindi Leader** | Provide Dindi confirmation and companion verification. | Dindi group operational access |

---

## 4. Functional Requirements (FR)

- **FR-5.1 Module Integration**: Reuses existing `users`, `roles`, `permissions`, `user_sessions`, `families`, `person_profiles`, `emergency_contacts`, `medical_cases`, `lost_person_cases`, and `audit_logs`. Does NOT create duplicate user or person profile tables.
- **FR-5.2 Found Case ID Generation**: Backend generates immutable Case ID (`WS-FP-2026-000001`).
- **FR-5.3 Temporary Found Person Profile**: Unidentified or partially identified pilgrims receive a temporary profile identifier `TEMP-FP-PER-2026-XXXXX` (`linked_person_id = NULL`). Permanent profiles are NOT created automatically.
- **FR-5.4 Candidate Profile Search**: Operators can search permanent `person_profiles` by name, mobile, family code, or age to identify potential matches.
- **FR-5.5 Safe Assistance Location Assignment**: Tracks person placement at authorized safe facilities (`HELP_CENTER`, `POLICE_POST`, `MEDICAL_CAMP`, `DINDI_CAMP`) with arrival timestamps and status (`AT_HELP_CENTER`, `IN_TRANSIT`, `WITH_DINDI`, `REUNITED`).
- **FR-5.6 Module 3 Medical Integration**: If `medical_attention_required = True`, links or creates a medical case in Module 3 (`medical_case_id`).
- **FR-5.7 Identification Clues**: Stores verbal statements (stated name, Dindi #, village, guardian name) with confidence rating and verification status.
- **FR-5.8 Human-Verified Reunification**: Requires identity verification (`found_person_verifications`) and authorized officer approval (`found_person_reunifications`) before updating case status to `REUNITED`.
- **FR-5.9 AI Boundary**: Exposes structured found person data for future Module 7 AI matching without implementing AI/facial recognition in Module 5.

---

## 5. Database Schema & Data Models

### Summary of New Database Tables Created:
1. `found_person_cases`: Core case record with temporary ID, identification status, communication status, and medical link.
2. `found_person_locations`: Found zone, route section, landmark, GPS coordinates.
3. `found_person_clothing`: Clothing descriptions worn when found.
4. `found_person_photos`: Photograph attachments.
5. `found_person_identification_clues`: Verbal clues and confidence ratings.
6. `found_person_safe_locations`: Safe help center placement and custody tracking.
7. `found_person_family_contacts`: Family contact attempt logs.
8. `found_person_verifications`: Identity verification records.
9. `found_person_reunifications`: Formal reunification handover records.
10. `found_person_status_history`: Audit history of case status transitions.
11. `found_person_notes`: Case notes with `INTERNAL` vs `FAMILY_VISIBLE` visibility controls.

---

## 6. REST API Specifications

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/found-person/cases` | Authorized Staff | Register a new found person case |
| `GET` | `/api/found-person/cases` | Authenticated User | List found person cases (with filters) |
| `GET` | `/api/found-person/cases/{id}` | Authenticated User | Get found person case details, clues, safe placement |
| `PATCH` | `/api/found-person/cases/{id}/status` | Authenticated User | Update case status |
| `GET` | `/api/found-person/cases/search-profiles` | Authorized Staff | Search permanent profiles for candidate matches |
| `POST` | `/api/found-person/cases/{id}/identification-clues` | Authorized Staff | Record identification clue (verbal statement) |
| `POST` | `/api/found-person/cases/{id}/safe-location` | Authorized Staff | Assign / transfer safe help center placement |
| `POST` | `/api/found-person/cases/{id}/family-contact` | Authorized Staff | Log family contact attempt |
| `POST` | `/api/found-person/cases/{id}/verification` | Police / Help Center | Perform identity verification |
| `POST` | `/api/found-person/cases/{id}/reunification` | Police / Help Center | Perform formal reunification handover (`REUNITED`) |

---

## 7. Test Cases & Validation Suite (`backend/tests/test_module5.py`)

| Test ID | Description | Input Data | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-5.1** | Report Found Person (Unidentified) | `approximate_name="Child"` | Case `WS-FP-2026-XXXXXX` created, `TEMP-FP-PER-2026-XXXXX` generated | **PASSED** |
| **TC-5.2** | Search Existing Profiles | `q="Aarav"` | Candidate profiles returned from Module 2 | **PASSED** |
| **TC-5.3** | Add Identification Clue | `clue_type="DINDI_NUMBER"` | Clue saved with confidence rating, HTTP 201 | **PASSED** |
| **TC-5.4** | Assign Safe Location | `location_name="Help Center 2"` | Placement updated, status `AT_HELP_CENTER` | **PASSED** |
| **TC-5.5** | Log Family Contact | `contact_name="Rajesh"` | Family contact logged, status set to `FAMILY_CONTACTED` | **PASSED** |
| **TC-5.6** | Identity Verification | Police token, `VERIFIED` | Verification recorded, status `IDENTITY_CONFIRMED` | **PASSED** |
| **TC-5.7** | Perform Reunification Handover | Police token, handover notes | Handover recorded, status `REUNITED`, HTTP 200 | **PASSED** |
| **TC-5.8** | Audit Logging | Module 5 actions | Security events recorded in `audit_logs` | **PASSED** |

---

## 8. Security & Privacy Controls

1. **IDOR Prevention**: Verifies authorization tokens and role permissions before granting access to found person case records.
2. **Privacy Protection for Vulnerable Persons**: Found person photographs, exact custody locations, and medical assessments are kept strictly confidential and accessible only to authorized staff.
3. **Internal Operational Notes**: Case notes marked as `INTERNAL` are restricted to Police and Help Center personnel.
