# ReuniteAI – AI-Powered Lost Person & Family Reunification Platform
## Master Data Management (MDM) & Software Engineering Documentation: Module 2 – Family & Person Profile Management

**Case Study**: Jagannath Rath Yatra, Puri  
**System Component**: Module 2 – Family & Person Profile Management  
**Integration Status**: Fully Integrated with Module 1 RBAC, User IDs (`users.id`), Session Authentication, and Audit Logging  
**Date**: August 16, 2026  
**Document Version**: 2.0.0-PROD  

---

## 1. Module Objective
Module 2 establishes the core domain data model for family groups, travel companions, person profiles, physical descriptions, clothing profiles, optional sensitive medical/safety profiles, emergency contacts, and profile photo storage.

This module provides the necessary data foundation required by downstream operational modules:
- **Module 3**: Missing Person Case Filing
- **Module 4**: Found Person Kiosk Logging
- **Module 6**: AI Face Biometric Matching Engine
- **Module 7**: Verification & Family Reunification Handover
- **Module 11**: QR/NFC Wristband Safety ID Linking

---

## 2. Scope
Module 2 handles:
- Family group creation and management by authenticated guardians (`users.id`).
- Family member and travel companion profile registration via a 6-Step Wizard.
- Automated backend age calculation from Date of Birth and age categorization (`CHILD`, `MINOR`, `ADULT`, `ELDERLY`).
- System-generated unique Person IDs (`RY-PER-2026-XXXXXX`) and Family Codes (`RY-FAM-2026-XXXXXX`).
- Physical description recording (height, weight, hair, eye, skin tone, identification marks, glasses/aids).
- Yatra expected clothing profile recording (top, bottom, footwear, headwear, accessories).
- Optional confidential safety & medical profile recording with explicit user consent checkboxes.
- Emergency contact management.
- Photo uploads with file format & size validation.
- Soft deactivation of profiles (`status = 'INACTIVE'`).
- Strict ownership authorization checks to prevent unauthorized access across families.
- Audit event logging reusing Module 1's `audit_logs` table.

---

## 3. System Actors & Access Levels

| Actor | Access Permissions in Module 2 | Data Access Scope |
| :--- | :--- | :--- |
| **Parent / Guardian** | `OWNER` / `EDITOR` | Full CRUD on own family group and family members. Cannot view other families. |
| **Travel Companion / Relative** | `VIEWER` / `EDITOR` | View or edit assigned family members based on `family_access` level. |
| **Police Officer** | `OPERATIONAL_READ` | Read-only access to basic, physical, and clothing profiles for missing person cases. |
| **Medical Staff** | `MEDICAL_READ` | Read access to medical/safety profiles for hospital patient identification. |
| **Help Center Operator** | `KIOSK_OPERATOR` | Read access to basic profile info to assist walk-in pilgrims. |
| **Event / Super Admin** | `GLOBAL_ADMIN` | Global view and audit monitoring across all families and profiles. |

---

## 4. Functional Requirements (FR)

- **FR-2.1: Module 1 Architecture Reuse**: Must reuse `users`, `roles`, `permissions`, `user_sessions`, `audit_logs` from Module 1. Must never duplicate user records or auth systems.
- **FR-2.2: Family Group Creation**: Authenticated user can create family groups with unique code (`RY-FAM-2026-XXXXXX`), primary contact, and emergency contact details.
- **FR-2.3: Unique System Person ID**: Every person profile must be assigned a backend-generated Person ID (`RY-PER-2026-XXXXXX`).
- **FR-2.4: Backend-Enforced Age & Classification**: Age must be calculated from `date_of_birth` on the backend. Frontend overrides are strictly prohibited. Classification:
  - $0 \le \text{Age} \le 12 \implies \text{CHILD}$
  - $13 \le \text{Age} \le 17 \implies \text{MINOR}$
  - $18 \le \text{Age} \le 59 \implies \text{ADULT}$
  - $\text{Age} \ge 60 \implies \text{ELDERLY}$
- **FR-2.5: Physical & Clothing Profiles**: Optional recording of physical characteristics and expected Yatra clothing (top/bottom type & color, footwear, accessories).
- **FR-2.6: Optional Confidential Medical Profile**: Optional recording of medical conditions, medications, allergies, blood group, and cognitive aid requirements. Must require explicit consent checkbox and display privacy notice.
- **FR-2.7: Profile Photo Storage**: Upload PNG/JPG images (<= 5MB). Files saved on server with sanitized unique filenames and relative paths saved in `person_photos`.
- **FR-2.8: Soft Deactivation**: Deactivating a member sets `status = 'INACTIVE'`, preserving historical data for missing person cross-referencing.
- **FR-2.9: Ownership Authorization**: Backend must verify `authenticated_user_id` ownership of `family_id` on every API operation. Return `403 Forbidden` for unauthorized requests.

---

## 5. Non-Functional Requirements (NFR)

- **NFR-2.1: Privacy & Data Protection**: Sensitive medical information must be masked on general UI screens and logged in audit trails upon viewing.
- **NFR-2.2: Performance**: Profile retrieval APIs must execute under **40ms** using indexed foreign keys.
- **NFR-2.3: Storage Optimization**: Image uploads restricted to 5MB, stored on local disk storage outside MySQL database binaries.
- **NFR-2.4: Reliability**: Soft deactivation ensures zero data loss for active or historical reunification cases.

---

## 6. Database Design & Relationships (ER Overview)

```
[ users (Module 1) ]
       │ 1
       │
       └───< [ families ]
                 │ 1
                 │
                 └───< [ family_members ] >─── [ person_profiles ]
                                                    │
             ┌───────────────────┬──────────────────┼───────────────────┐
             ↓                   ↓                  ↓                   ↓
     [ person_photos ]  [ clothing_profiles ] [ person_safety_profiles ] [ emergency_contacts ]
```

### Table Definitions Summary:
- `families`: `id`, `uuid`, `family_code`, `family_name`, `owner_user_id` (FK -> `users.id`), `primary_contact_name`, `primary_contact_mobile`, `emergency_contact_name`, `emergency_contact_mobile`, `preferred_language`, `notes`, `status`, `created_at`, `updated_at`.
- `person_profiles`: `id`, `uuid`, `person_code`, `full_name`, `date_of_birth`, `gender`, `age_category`, `height`, `approx_weight`, `hair_color`, `eye_color`, `skin_tone`, `identification_mark`, `glasses`, `hearing_aid`, `walking_assistance`, `preferred_language`, `profile_visibility`, `status`, `created_at`, `updated_at`.
- `family_members`: `id`, `uuid`, `family_id` (FK), `person_id` (FK), `relationship_type`, `status`, `created_at`, `updated_at`.
- `person_photos`: `id`, `uuid`, `person_id` (FK), `file_path`, `file_type`, `file_size`, `is_primary`, `uploaded_by` (FK -> `users.id`), `created_at`.
- `clothing_profiles`: `id`, `person_id` (FK), `top_type`, `top_color`, `bottom_type`, `bottom_color`, `footwear`, `footwear_color`, `headwear`, `accessories`, `description`, `created_at`, `updated_at`.
- `person_safety_profiles`: `id`, `person_id` (FK), `medical_condition`, `medication_requirement`, `allergy_information`, `blood_group`, `mobility_assistance`, `communication_difficulty`, `cognitive_assistance_required`, `consent_status`, `created_at`, `updated_at`.
- `emergency_contacts`: `id`, `person_id` (FK), `contact_name`, `relationship`, `mobile`, `alternate_mobile`, `is_primary`, `created_at`, `updated_at`.
- `family_access`: `id`, `family_id` (FK), `user_id` (FK), `access_level` (`OWNER`, `EDITOR`, `VIEWER`), `status`, `created_at`.

---

## 7. REST API Specification

| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/families` | Session Token | Create a new family group |
| `GET` | `/api/families` | Session Token | List families accessible to current user |
| `GET` | `/api/families/{id}` | Session Token | Get family details & member cards |
| `PUT` | `/api/families/{id}` | Session Token | Update family details |
| `DELETE` | `/api/families/{id}` | Session Token | Deactivate family group (`INACTIVE`) |
| `POST` | `/api/families/{id}/members` | Session Token | Add a new member profile (Wizard submit) |
| `GET` | `/api/families/{id}/members` | Session Token | List all members in family |
| `GET` | `/api/families/{id}/members/{person_id}` | Session Token | Get specific family member profile |
| `PUT` | `/api/families/{id}/members/{person_id}` | Session Token | Update family member profile |
| `PATCH` | `/api/families/{id}/members/{person_id}/deactivate` | Session Token | Soft deactivate family member (`INACTIVE`) |
| `GET` | `/api/persons/{person_id}` | Session Token | Get full person profile (basic, clothing, safety, photo) |
| `PUT` | `/api/persons/{person_id}` | Session Token | Update person profile details |
| `POST` | `/api/persons/{person_id}/photos` | Session Token | Upload profile photograph |
| `DELETE` | `/api/persons/{person_id}/photos/{photo_id}` | Session Token | Delete profile photograph |
| `POST` | `/api/persons/{person_id}/emergency-contacts` | Session Token | Add emergency contact |
| `PUT` | `/api/persons/{person_id}/emergency-contacts/{id}` | Session Token | Update emergency contact |
| `DELETE` | `/api/persons/{person_id}/emergency-contacts/{id}` | Session Token | Delete emergency contact |

---

## 8. Data Flow & Sequence Diagram Description

1. **Member Profile Registration Flow**:
   - User opens `add-person.html` and fills out the 6-Step Wizard.
   - Client JS calculates real-time age preview on step 1.
   - Form submits JSON payload to `POST /api/families/{family_id}/members`.
   - `family_routes` passes request to `verify_family_access()` middleware.
   - `person_service.create_person_profile()` calculates exact age from `date_of_birth`, assigns `age_category` (`CHILD`, `MINOR`, `ADULT`, `ELDERLY`), and generates `person_code` (`RY-PER-2026-XXXXXX`).
   - Inserts records into `person_profiles`, `family_members`, `clothing_profiles`, `person_safety_profiles`, and `emergency_contacts`.
   - If photo selected, `photo_service.save_person_photo()` validates file extension/size, writes image to disk, and updates `person_photos`.
   - Logs `MEMBER_ADDED` event in `audit_logs` table.
   - Returns full person JSON payload with HTTP `201 Created`.

---

## 9. Test Cases Suite Summary (`backend/tests/test_module2.py`)

| Test ID | Test Description | Expected Result | Status |
| :--- | :--- | :--- | :--- |
| **TC-2.1** | Create Family Group | Family code `RY-FAM-2026-XXXXXX` generated, HTTP 201 | **PASSED** |
| **TC-2.2** | Add Child Member | Age calculated from DOB, category set to `CHILD`, code `RY-PER-2026-XXXXXX` generated | **PASSED** |
| **TC-2.3** | Add Elderly Member | Age calculated from DOB, category set to `ELDERLY` | **PASSED** |
| **TC-2.4** | Unauthorized Family Access | User accessing another user's family receives HTTP 403 Forbidden | **PASSED** |
| **TC-2.5** | Photo Upload Validation | Invalid format (.txt) rejected with 400; valid PNG stored with 201 | **PASSED** |
| **TC-2.6** | Deactivate Family Member | Status set to `INACTIVE` (soft delete) in DB | **PASSED** |
| **TC-2.7** | Module 2 Audit Logging | Audit events (`FAMILY_CREATED`, `MEMBER_ADDED`, `MEMBER_DEACTIVATED`, `PHOTO_UPLOADED`) logged | **PASSED** |

---

## 10. Privacy & Security Rules

1. **Sensitive Medical Info Protection**: Medical/safety profiles are marked as confidential, require explicit user consent, and trigger an audit event (`SAFETY_INFO_VIEWED`) upon access.
2. **Strict Ownership Check**: Backend middleware verifies that `request.current_user` is the owner or authorized editor of `family_id` before executing any modification or read operation.
3. **Immutable Identifiers**: `person_code` (`RY-PER-2026-XXXXXX`) and `family_code` (`RY-FAM-2026-XXXXXX`) are system-generated and cannot be altered via edit APIs.
