# WariSeva – Multilingual Smart Platform for Medical Emergency, Lost Person & Item Assistance
## Master Data Management (MDM) & Software Engineering Documentation: Module 6 – Lost & Found Item Assistance & Recovery Management

**Case Study**: Alandi–Pandharpur Dindi Wari, Maharashtra  
**System Component**: Module 6 – Lost & Found Item Assistance & Recovery Management  
**Integration Status**: Fully Integrated with Module 1 (Auth, User IDs `users.id`, Session Security, RBAC, Audit Logs), Module 2 (`person_profiles`, `families`), Module 3 (`medical_cases`), Module 4 (`lost_person_cases`), and Module 5 (`found_person_cases`)  
**Date**: August 16, 2026  
**Document Version**: 6.0.0-PROD  

---

## 1. Module Objective
Module 6 establishes the digital lost and found item reporting, secure storage placement, chain of custody tracking, owner claims submission, multi-factor verification, and formal item return workflow for WariSeva during the Alandi–Pandharpur Dindi Wari.

The module enables:
- Lost item reporting (`WS-LI-2026-XXXXXX`) across 14 predefined categories (`ELECTRONICS`, `DOCUMENT`, `MOBILE_PHONE`, `WALLET`, `BAG`, `JEWELLERY`, `CLOTHING`, `FOOTWEAR`, `KEYS`, `EYEWEAR`, `MONEY`, `MEDICAL_ITEM`, `IDENTIFICATION_CARD`, `OTHER`).
- Found item registration (`WS-FI-2026-XXXXXX`) with condition grading (`NEW`, `GOOD`, `DAMAGED`, `HEAVILY_DAMAGED`, `BROKEN`, `UNKNOWN`).
- Privacy masking on public lists for sensitive identifiers (IMEIs, serial numbers, Aadhaar/ID numbers) showing masked strings (`************1234`).
- Placement of found belongings into secure storage lockers (`item_storage_locations`) with full chain of custody tracking (`item_custody_history`).
- Owner claims submission (`CLM-2026-XXXXXX`) and multi-factor verification (`item_claim_verifications`).
- Manual item pairing (`item_matches`) for lost ↔ found items while preparing data for Module 7 AI matching.

---

## 2. Real-World Problem Statement
During the Alandi–Pandharpur Dindi Wari, thousands of pilgrims lose personal items such as mobile phones, wallets, identity cards, spectacles, keys, or bags in crowded halts.

Previously, pilgrims who found items did not know where to submit them safely, and searching owners had no centralized catalog to check. Module 6 provides a secure digital repository, chain-of-custody tracking, and verified handover process across the route.

---

## 3. Main Actors & Access Control

| Actor | Key Responsibilities | Access Scope |
| :--- | :--- | :--- |
| **Warkari / Family Member** | File lost item reports, browse found catalog, submit owner claims. | Own item reports & claims |
| **Volunteer** | Register found items, assign initial storage center placement. | Found item registration & view |
| **Police Officer** | Review claims, verify ownership, perform manual item pairing, authorize item return. | Full police operational access |
| **Help Center Operator** | Manage physical locker storage, log custody transfers, process claims. | Help desk operational access |
| **Storage Operator** | Receive, store, transfer, and release items in locker facilities. | Locker custody desk access |

---

## 4. Functional Requirements (FR)

- **FR-6.1 Module Integration**: Reuses existing `users`, `roles`, `permissions`, `user_sessions`, `families`, `person_profiles`, `emergency_contacts`, `medical_cases`, `lost_person_cases`, `found_person_cases`, and `audit_logs`. Does NOT create duplicate user or profile systems.
- **FR-6.2 Case ID Generation**:
  - Lost Item Case ID: `WS-LI-2026-000001`
  - Found Item Case ID: `WS-FI-2026-000001`
  - Claim Number: `CLM-2026-000001`
- **FR-6.3 Core Entity Separation**: Maintains strict separation between:
  1. **LOST ITEM CASE** (`lost_item_cases`)
  2. **FOUND ITEM CASE** (`found_item_cases`)
  3. **OWNER CLAIM** (`item_claims`)
- **FR-6.4 Privacy Masking**: Public lists mask sensitive serial numbers, IMEIs, and document numbers (`************1234`). Only authorized personnel and item owners can view unmasked values.
- **FR-6.5 Secure Storage & Chain of Custody**: Found physical items are assigned to locker locations (`item_storage_locations`) and every physical transfer is recorded in `item_custody_history`.
- **FR-6.6 Owner Claims & Competing Claims**: Users submit claims with proof of ownership. When one claim is approved, competing active claims for that found item automatically update to `REJECTED`.
- **FR-6.7 Manual Item Matching**: Authorized staff can manually pair Lost Item ↔ Found Item (`match_type = 'MANUAL'`).
- **FR-6.8 AI Boundary**: Exposes structured item data for future Module 7 AI matching without implementing machine learning in Module 6.

---

## 5. Database Schema & Data Models

### Summary of New Database Tables Created:
1. `lost_item_cases`: Core lost item records.
2. `found_item_cases`: Core found item records.
3. `item_photos`: Photo attachments.
4. `item_locations`: Lost, found, and storage location records.
5. `item_identifiers`: Restricted sensitive identifiers (serial numbers, IMEIs).
6. `item_claims`: Owner claim submissions (`CLM-2026-XXXXXX`).
7. `item_claim_verifications`: Multi-factor claim verification records.
8. `item_storage_locations`: Locker and cabinet storage facilities.
9. `item_custody_history`: Physical chain-of-custody transfer logs.
10. `item_status_history`: Audit history of case status transitions.
11. `item_notes`: Internal vs user-visible notes.
12. `item_matches`: Manual/AI pairing links.

---

## 6. REST API Specifications

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/lost-items` | Authenticated User | File a new lost item case |
| `GET` | `/api/lost-items` | Authenticated User | List lost items (with category, zone, status filters) |
| `GET` | `/api/lost-items/{id}` | Authenticated User | Get lost item details (masked sensitive fields for non-owners) |
| `POST` | `/api/found-items` | Authorized Staff | Register a found physical item |
| `GET` | `/api/found-items` | Authenticated User | List found items catalog |
| `GET` | `/api/found-items/{id}` | Authenticated User | Get found item details, custody chain, claims |
| `POST` | `/api/found-items/{id}/claims` | Authenticated User | Submit owner claim for found item |
| `POST` | `/api/claims/{id}/verify` | Police / Help Center | Verify & approve/reject claim |
| `POST` | `/api/item-matches/manual` | Police / Help Center | Create manual Lost Item ↔ Found Item pair |
| `POST` | `/api/found-items/{id}/release` | Police / Help Center | Perform formal return handover (`RETURNED`) |

---

## 7. Test Cases & Validation Suite (`backend/tests/test_module6.py`)

| Test ID | Description | Input Data | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-6.1** | Report Lost Item | `item_category="MOBILE_PHONE"` | Case `WS-LI-2026-XXXXXX` created, HTTP 201 | **PASSED** |
| **TC-6.2** | Report Found Item | `item_category="MOBILE_PHONE"` | Case `WS-FI-2026-XXXXXX` created, status `STORED` | **PASSED** |
| **TC-6.3** | Privacy Masking | Non-owner API call | Sensitive IMEI/Serial numbers masked | **PASSED** |
| **TC-6.4** | Submit Owner Claim | Claim proof text | Claim `CLM-2026-XXXXXX` submitted, HTTP 201 | **PASSED** |
| **TC-6.5** | Verify & Approve Claim | Police token, `APPROVED` | Claim approved, case status `VERIFICATION` | **PASSED** |
| **TC-6.6** | Manual Item Pairing | Lost & Found case IDs | Manual potential match link created | **PASSED** |
| **TC-6.7** | Release Found Item | Police token, owner name | Item released, status updated to `RETURNED` | **PASSED** |
| **TC-6.8** | Audit Logging | Module 6 actions | Security events recorded in `audit_logs` | **PASSED** |

---

## 8. Security & Privacy Controls

1. **IDOR & Ownership Verification**: API endpoints verify caller permissions and ownership of lost items / claims before granting read or edit access.
2. **Sensitive Identifier Protection**: IMEIs, serial numbers, Aadhaar numbers, and bank details are masked on public endpoints and visible only to verified owners and authorized staff.
3. **Chain of Custody Integrity**: Immutable logging of every physical handover preventing unauthorized item movement.
