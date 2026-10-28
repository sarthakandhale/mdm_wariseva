# ReuniteAI – AI-Powered Lost Person & Family Reunification Platform
## Master Data Management (MDM) & Software Engineering Documentation: Module 1 – User & Role Management

**Case Study**: Jagannath Rath Yatra, Puri  
**System Component**: Module 1 – User & Role Management (Core RBAC & Security Foundation)  
**Date**: August 12, 2026  
**Document Version**: 1.0.0-PROD  

---

## 1. Module Objective
The primary objective of Module 1 is to construct an enterprise-grade, secure, multi-tenant User and Role Management module that serves as the architectural foundation for the entire ReuniteAI platform. 

This module enforces Role-Based Access Control (RBAC), user authentication, session security, password security, profile management, administrative registration approval workflows, and audit trail logging. Future business logic modules (Family Management, Missing Person Reporting, AI Face Matching, Volunteer Dispatch, Police Operations, Hospital Admissions) directly depend on and reference the user identities, session validation middleware, and permission structures established in this module.

---

## 2. System Actors

| Actor Name | Description | Default Status on Reg | Role Authority Level |
| :--- | :--- | :--- | :--- |
| **Parent / Guardian** | Citizens or pilgrims registering family members, filing missing reports, and tracking reunification status. | `ACTIVE` | Level 1 (Public Access) |
| **Ground Volunteer** | Registered volunteers stationed across Grand Road (Bada Danda) help booths logging found individuals. | `PENDING` | Level 2 (Field Verified) |
| **Police Officer** | Puri District Law Enforcement officers managing cases, verifying AI matches, and directing operations. | `PENDING` | Level 3 (Institutional) |
| **Medical Staff** | Healthcare personnel at Puri District Hospital and emergency camps logging unidentified admitted patients. | `PENDING` | Level 3 (Institutional) |
| **Help Center Operator** | Control center personnel managing public announcement kiosks and walk-in lost & found inquiries. | `PENDING` | Level 3 (Institutional) |
| **Event Admin** | District administrators supervising crowd operations, approving pending accounts, and reviewing analytics. | `PENDING` / Admin Created | Level 4 (Administrative) |
| **Super Admin** | Platform core system administrators managing global permissions, audit logs, and security parameters. | Seeded / Super Admin | Level 5 (System Master) |

---

## 3. Functional Requirements (FR)

- **FR-1: Multi-Role Registration System**
  - The system shall allow public self-registration for `PARENT_GUARDIAN` and `VOLUNTEER` roles.
  - The system shall allow institutional registration requests for `POLICE_OFFICER`, `MEDICAL_STAFF`, `HELP_CENTER_OPERATOR`, and `EVENT_ADMIN`.
  - Self-registration as `SUPER_ADMIN` shall be strictly forbidden.
- **FR-2: Strict Input Validation**
  - **Full Name**: Required, minimum 2 characters.
  - **Mobile Number**: Required, 10-digit Indian mobile number format (`^[6-9]\d{9}$`), unique across system.
  - **Email**: Optional, valid RFC-5322 format, unique if provided.
  - **Password**: Minimum 8 characters, requiring at least 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character.
- **FR-3: Role-Based Registration Approval Policy**
  - Accounts registered with role `PARENT_GUARDIAN` shall automatically receive `ACTIVE` status.
  - Accounts registered with roles `VOLUNTEER`, `POLICE_OFFICER`, `MEDICAL_STAFF`, `HELP_CENTER_OPERATOR`, or `EVENT_ADMIN` shall receive `PENDING` status requiring administrator sign-off before login is allowed.
- **FR-4: Multi-Channel Authentication**
  - Users shall log in using registered Mobile Number or Email along with password.
  - Users with status `PENDING`, `SUSPENDED`, `BLOCKED`, or `REJECTED` shall be blocked from logging in with descriptive security messages and HTTP status 403.
- **FR-5: Cryptographic Password Hashing & Security**
  - Passwords shall never be stored or logged in plain text.
  - Passwords shall be hashed using Werkzeug PBKDF2/SHA256 or bcrypt with salt.
  - Hashed credentials shall never be returned in API responses.
- **FR-6: Administrative Approval & Status Transition Workflow**
  - Event Admins and Super Admins shall be provided an Administrative Approval interface displaying pending accounts with full name, mobile, email, requested role, and registration date.
  - Admins can transition account statuses: `PENDING` -> `ACTIVE`, `PENDING` -> `REJECTED`, `ACTIVE` -> `SUSPENDED`, `ACTIVE` -> `BLOCKED`.
- **FR-7: Session & Token Management**
  - Authenticated sessions shall issue secure session tokens stored in `user_sessions` table with expiration timestamp.
  - User logout shall immediately revoke the session token (`revoked_at`).
- **FR-8: User Profile Management**
  - Users can view their profile data (Full Name, Mobile, Email, Role, Language, Status, UUID, Registration Date, Last Login).
  - Users can edit Name, Email, Preferred Language, and Profile Photo. Mobile number edits require OTP verification.
- **FR-9: Security Audit Trail Logging**
  - Every critical action (`REGISTER`, `LOGIN`, `LOGOUT`, `PASSWORD_CHANGE`, `PROFILE_UPDATE`, `USER_APPROVE`, `USER_REJECT`, `USER_SUSPEND`, `USER_BLOCK`) must write an immutable audit log entry including `user_id`, `action`, `details`, `ip_address`, and `user_agent`.

---

## 4. Non-Functional Requirements (NFR)

- **NFR-1: Performance**: API authentication and session token verification latency must remain under **50ms**.
- **NFR-2: Scalability**: Database schema and indexing must support **1,000,000+** registered users for Rath Yatra peak crowds.
- **NFR-3: Security**: Zero OWASP Top 10 vulnerabilities (SQL Injection prevented via parameterized queries, XSS prevented via HTML sanitization, CSRF & CORS protection enabled).
- **NFR-4: Availability**: High-availability database clustering support on MySQL 8+.
- **NFR-5: Compliance & Data Privacy**: Passwords and sensitive tokens encrypted at rest and in transit (TLS 1.3).

---

## 5. System Use Cases

### Use Case 1: User Self-Registration
- **Primary Actor**: Parent / Guardian or Volunteer
- **Preconditions**: User is on `register.html`.
- **Main Flow**:
  1. User fills Full Name, Mobile Number, Email (optional), Role, Preferred Language, Password, and Confirm Password.
  2. Client-side JS validates field constraints in real-time.
  3. Form submits `POST /api/auth/register`.
  4. Backend verifies uniqueness of Mobile/Email, checks role rule, hashes password, inserts user into database.
  5. If role is `PARENT_GUARDIAN`, user receives `ACTIVE` status and is redirected to login.
  6. If role is institutional or volunteer, user receives `PENDING` status and informative notification.

### Use Case 2: Administrative Account Approval
- **Primary Actor**: Event Admin or Super Admin
- **Preconditions**: Admin is logged in and navigates to `pending-users.html`.
- **Main Flow**:
  1. Interface issues `GET /api/admin/users/pending` with Bearer token.
  2. Backend validates `@role_required(['EVENT_ADMIN', 'SUPER_ADMIN'])` and returns list of pending accounts.
  3. Admin clicks **Approve** or **Reject** button.
  4. Interface issues `PUT /api/admin/users/{id}/approve` or `reject`.
  5. Backend updates user status to `ACTIVE` or `REJECTED`, logs audit event, and returns success response.

---

## 6. Database Design

Target DB Engine: **MySQL 8.0+** (with automatic SQLite fallback for zero-dependency local test execution).

### ER Diagram Overview
```
+------------------+         +--------------------+         +------------------+
|      roles       | 1     * |  role_permissions  | *     1 |   permissions    |
|------------------|---------|--------------------|---------|------------------|
| id (PK)          |         | role_id (FK)       |         | id (PK)          |
| name             |         | permission_id (FK) |         | name             |
| description      |         +--------------------+         | description      |
+------------------+                                        +------------------+
         | 1
         |
         | *
+------------------------------------------------------------------------------+
|                                    users                                     |
|------------------------------------------------------------------------------|
| id (PK) | uuid | full_name | mobile | email | password_hash | role_id (FK) |    |
| status  | is_verified | preferred_language | created_at | last_login_at   |    |
+------------------------------------------------------------------------------+
         | 1                            | 1                        | 1
         |                              |                          |
         | *                            | *                        | *
+------------------+         +-----------------------+   +---------------------+
|  user_sessions   |         | password_reset_tokens |   |     audit_logs      |
|------------------|         |-----------------------|   |---------------------|
| id (PK)          |         | id (PK)               |   | id (PK)             |
| user_id (FK)     |         | user_id (FK)          |   | user_id (FK)        |
| session_token    |         | token                 |   | action              |
| expires_at       |         | expires_at            |   | details             |
| revoked_at       |         | used_at               |   | ip_address          |
+------------------+         +-----------------------+   +---------------------+
```

---

## 7. REST API Specifications

| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Public | Register new user account |
| `POST` | `/api/auth/login` | Public | Authenticate credentials and issue session token |
| `POST` | `/api/auth/logout` | Session Token | Revoke session token and logout |
| `POST` | `/api/auth/forgot-password` | Public | Request password reset token |
| `POST` | `/api/auth/reset-password` | Public | Confirm reset token and set new password |
| `POST` | `/api/auth/change-password` | Session Token | Change logged-in user password |
| `GET`  | `/api/users/me` | Session Token | Fetch current logged-in user profile |
| `PUT`  | `/api/users/me` | Session Token | Update profile details (Name, Email, Lang, Photo) |
| `GET`  | `/api/admin/users` | Admin Role | List all users directory with status & role filters |
| `GET`  | `/api/admin/users/pending` | Admin Role | List pending approval accounts |
| `PUT`  | `/api/admin/users/{id}/approve` | Admin Role | Approve pending user account (`ACTIVE`) |
| `PUT`  | `/api/admin/users/{id}/reject` | Admin Role | Reject pending user account (`REJECTED`) |
| `PUT`  | `/api/admin/users/{id}/suspend` | Admin Role | Suspend active account (`SUSPENDED`) |
| `PUT`  | `/api/admin/users/{id}/block` | Admin Role | Block active account (`BLOCKED`) |
| `GET`  | `/api/admin/audit-logs` | Admin Role | Retrieve security audit events |

---

## 8. Sequence Diagram Description

**User Authentication & Session Initialization Sequence**:
1. User enters mobile/email + password on `login.html` and clicks **Sign In**.
2. Frontend `auth.js` triggers `APIClient.post('/api/auth/login')`.
3. Flask `auth_routes` dispatches call to `auth_service.login_user()`.
4. `auth_service` executes parameterized query to fetch user record by mobile/email from `users` table joined with `roles`.
5. If user not found or `verify_password(hash, pwd)` fails -> Audit log `LOGIN_FAILED` is written, returns HTTP 401.
6. If password matches, `auth_service` checks user `status`. If `PENDING` / `SUSPENDED` / `BLOCKED` -> returns HTTP 403.
7. If status is `ACTIVE`, `auth_service` generates `reunite_sess_<random_32_bytes>`, sets 24-hour expiration, inserts token into `user_sessions`, updates `users.last_login_at`, and logs `LOGIN` audit event.
8. Flask returns JSON response `{ success: true, data: { session_token, user, redirect_url } }`.
9. Frontend stores `session_token` in `localStorage` and redirects browser to `redirect_url` (e.g. `/admin/dashboard.html`).

---

## 9. Activity Diagram Description

**Admin Approval Workflow Activity Flow**:
```
  [ Start ]
      |
      v
  [ Admin logs into reuniai Portal ]
      |
      v
  [ Navigate to 'Pending Approvals' Page ]
      |
      v
  [ Frontend calls GET /api/admin/users/pending ]
      |
      v
  [ Backend verifies Admin Token & Fetches PENDING Users ]
      |
      v
  [ Display Pending Users Table in UI ]
      |
      +-----------------------+-----------------------+
      |                                               |
      v (Clicks Approve)                              v (Clicks Reject)
  [ Send PUT /api/admin/users/:id/approve ]       [ Send PUT /api/admin/users/:id/reject ]
      |                                               |
      v                                               v
  [ Update status = 'ACTIVE' ]                    [ Update status = 'REJECTED' ]
      |                                               |
      +-----------------------+-----------------------+
                              |
                              v
                [ Record Audit Log Event ]
                              |
                              v
               [ Refresh Table & Display Toast ]
                              |
                              v
                           [ End ]
```

---

## 10. Security Requirements Matrix

- **SQL Injection Defense**: 100% parameterized SQL queries (`%s` in MySQL, `?` in SQLite). No dynamic string concatenation in SQL statements.
- **XSS Defense**: Sanitization of user input strings and HTML escaping on UI output elements.
- **CSRF & CORS Defense**: Flask-CORS restricted to authorized origins and explicit JSON header parsing.
- **Role Hijacking Defense**: Backend derives role identity directly from the authenticated database session token on every request. Never trusts client-sent role claims.

---

## 11. Test Cases Suite Summary

| Test ID | Test Description | Expected Result | Status |
| :--- | :--- | :--- | :--- |
| **TC-01** | Static Health Check | Returns HTTP 200 OK | **PASSED** |
| **TC-02** | Parent Registration | Status set to `ACTIVE`, HTTP 201 | **PASSED** |
| **TC-03** | Volunteer Registration | Status set to `PENDING`, HTTP 201 | **PASSED** |
| **TC-04** | Duplicate Mobile Registration | Fails with HTTP 409 Conflict | **PASSED** |
| **TC-05** | Weak Password Registration | Fails with HTTP 422 Unprocessable | **PASSED** |
| **TC-06** | Valid Super Admin Login | Returns session_token, HTTP 200 | **PASSED** |
| **TC-07** | Pending User Login | Blocked with HTTP 403 Forbidden | **PASSED** |
| **TC-08** | Admin User Approval | Updates status `PENDING` -> `ACTIVE` | **PASSED** |
| **TC-09** | Unauthorized RBAC Route Access | Parent denied admin route with HTTP 403 | **PASSED** |
| **TC-10** | System Audit Log Recording | Events successfully captured in audit table | **PASSED** |

---

## 12. Risk Management & Mitigations

1. **Risk: SIM Swapping or Mobile Identity Theft**
   - *Mitigation*: Multi-factor authentication (SMS OTP) required for mobile number modification.
2. **Risk: Brute Force Login Attacks**
   - *Mitigation*: Account audit tracking and rate-limiting middleware configured on `/api/auth/login`.
3. **Risk: High Concurrent Loads During Rath Yatra Peak**
   - *Mitigation*: Database indexing on `mobile`, `email`, `session_token`, and `status` fields ensures sub-50ms execution under high concurrency.

---

## 13. Future Integration Roadmap (Modules 2 – 12)

Module 1 provides the single source of truth for user identities. Future modules will build directly on top of Module 1:
- **Module 2 (Family & Person Profiles)**: Foreign key references `users.id` to map family relationships.
- **Module 3 (AI Face Matching Engine)**: Queries `users.id` to attach biometric embeddings to user profiles.
- **Module 4 (Ground Volunteer Operations)**: References `users.id` with `role_id = VOLUNTEER` for sector dispatch.
- **Module 5 (Police Command Center)**: Utilizes RBAC permission checking (`CASE_VERIFY`, `MATCH_VERIFY`) for police handovers.
