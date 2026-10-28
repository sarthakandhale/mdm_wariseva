# WariSeva / ReuniteAI – Multilingual Smart Platform for Medical Emergency, Lost Person & Item Assistance

**Case Study**: Alandi–Pandharpur Dindi Wari & Puri Jagannath Rath Yatra  
**Technology**: Python Flask REST APIs + MySQL 8+ (with zero-config SQLite fallback) + Leaflet.js + OpenStreetMap + Vanilla HTML5/CSS3/JavaScript  

---

## 📌 Active Platform Modules
1. **Module 1 – User & Role Management**: RBAC, 7 User Roles, Authentication, Session Tokens, Admin Approvals, Audit Logging.
2. **Module 2 – Family & Person Profile Management**: Family Groups (`RY-FAM-2026-XXXXXX`), Member Registration via 6-Step Wizard, Age Calculation & Classification (`CHILD`, `MINOR`, `ADULT`, `ELDERLY`), Person Safety IDs (`RY-PER-2026-XXXXXX`), Physical & Clothing Profiles, Confidential Medical Profiles, Emergency Contacts, Photo Uploads.
3. **Module 3 – Medical Emergency Assistance**: Medical Case Filing (`WS-MED-2026-XXXXXX`), Temporary Patient Tracking (`TEMP-PAT-2026-XXXXX`), Deterministic Rule-Based Priority Engine (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), Wari Route Zones, Medical Camp Finder, Ambulance Dispatch (`WS-AMB-2026-XXXXXX`), Clinical Treatment & Referrals, Multilingual Foundation.
4. **Module 4 – Lost Person Assistance & Missing Case Management**: Missing Person Reporting (`WS-LP-2026-XXXXXX`), Active Duplicate Case Prevention, Temporary Profile Tracking (`TEMP-PER-2026-XXXXX`), Rule-Based Priority Engine, Police Priority Override, Case Clothing Details, Sightings Reporting, Volunteer Search Support, Case Notes, Case Withdrawal.
5. **Module 5 – Found Person Assistance & Safe Custody Management**: Found Person Registration (`WS-FP-2026-XXXXXX`), Temporary Found Code (`TEMP-FP-PER-2026-XXXXX`), Candidate Profile Search, Safe Assistance Location Placement, Module 3 Medical Emergency Link (`medical_case_id`), Verbal Clues, Family Contact Logs, Identity Verification, Official Handover.
6. **Module 6 – Lost & Found Item Assistance & Recovery Management**: Lost Item Reporting (`WS-LI-2026-XXXXXX`), Found Item Registration (`WS-FI-2026-XXXXXX`), 14 Item Categories, Privacy Masking on IMEIs/Serial Numbers (`************1234`), Secure Storage Locker Assignment, Chain of Custody Tracking, Owner Claims Submission (`CLM-2026-XXXXXX`), Multi-Factor Verification, Manual Item Pairing, Official Return Handover.
7. **Module 7 – AI-Assisted Matching & Intelligent Case Recommendation**: Pipeline A (Lost Person ↔ Found Person) & Pipeline B (Lost Item ↔ Found Item), Weighted Feature Similarity Engine, Data Quality & Confidence Scoring, Human-Understandable Explainability Engine, Decision Support System (No Auto-Reunification), Operator Match Review Workbench, AI Dashboard Metrics, Model Evaluation Metrics (Precision, Recall, F1, Confusion Matrix).
8. **Module 8 – Dindi Management & Warkari Group Coordination**: Dindi Registration (`WS-DIN-2026-XXXXXX`), Display Dindi Number (e.g. Dindi No. 27), Leader & Assistant Leader Assignments (`dindi_leaders`), Relational Member Enrollment (`dindi_memberships`), Daily March & Rest Schedules (`dindi_schedules`), Broadcast Announcements (`dindi_announcements`), Emergency Assistance Shortcuts (Modules 3, 4, 5, 6), Administrative Verification (`dindi_verifications`).
9. **Module 9 – Dindi Route, Location & Wari Movement Management**: Configurable Wari Route (`WS-ROUTE-2026-XXXXXX`), 7 Route Sections (Alandi → Pandharpur), Interactive Leaflet.js / OpenStreetMap Integration, Color-Coded Map Markers, Dindi GPS/Manual Movement Updates (`dindi_location_updates`), Official Checkpoint Check-ins (`dindi_checkins`), Haversine Nearby Services Search, Crowd Congestion Level Controller (`LOW`..`SEVERE`), Emergency Zones, Route Alerts.
10. **Module 10 – Volunteer Management & Task Assignment**: Volunteer Registration (`WS-VOL-2026-XXXXXX`), Verification (`PENDING`, `VERIFIED`), Skill & Language Matrix, Shift & Attendance Tracking (`ON_DUTY`/`OFF_DUTY`), Functional Teams (`volunteer_teams`), Centralized Task Management (`WS-TASK-2026-XXXXXX`), 100% Rule-Based Recommendation Engine, Coordinator Review Workbench, Task Acceptance & Completion Verification, Duty Location Privacy.

---

## 🗂️ Complete Directory Structure

```
reuniteai/
├── backend/
│   ├── app.py                     # Main Flask Application Entry & Static Server
│   ├── config.py                  # Environment & Session Configuration
│   ├── db.py                      # MySQL 8+ & SQLite Auto-Fallback Layer (Module 1-10 Tables)
│   │
│   ├── ai/
│   │   ├── candidate_filter.py    # Candidate filtering before scoring
│   │   ├── feature_engineering.py # Haversine distance, age decay, timestamp decay, text overlap
│   │   ├── explanation_engine.py  # Human-readable reason bullet points
│   │   ├── similarity_engine.py   # Person & Item Weighted Similarity Engine
│   │   ├── person_matcher.py      # Pipeline A: Lost Person ↔ Found Person
│   │   └── item_matcher.py        # Pipeline B: Lost Item ↔ Found Item
│   │
│   ├── routes/
│   │   ├── volunteer_routes.py    # REST APIs: /api/volunteers, /api/volunteer-tasks, /api/volunteer-tasks/{id}/recommendations
│   │   ├── route_location_routes.py # REST APIs: /api/routes, /api/locations, /api/dindis/{id}/location
│   │   ├── dindi_routes.py        # REST APIs: /api/dindis/*, /api/dindis/{id}/members
│   │   ├── ai_routes.py           # REST APIs: /api/ai/match/*, /api/ai/matches/*
│   │   ├── item_routes.py         # REST APIs: /api/lost-items, /api/found-items
│   │   ├── found_person_routes.py # REST APIs: /api/found-person
│   │   ├── lost_person_routes.py  # REST APIs: /api/lost-person
│   │   ├── medical_routes.py      # REST APIs: /api/medical
│   │   ├── family_routes.py       # REST APIs: /api/families
│   │   ├── person_routes.py       # REST APIs: /api/persons
│   │   └── auth_routes.py         # REST APIs: /api/auth
│   │
│   └── tests/
│       ├── test_module1.py        # Module 1 Test Suite (10 Test Cases - PASSED)
│       ├── test_module2.py        # Module 2 Test Suite (7 Test Cases - PASSED)
│       ├── test_module3.py        # Module 3 Test Suite (11 Test Cases - PASSED)
│       ├── test_module4.py        # Module 4 Test Suite (9 Test Cases - PASSED)
│       ├── test_module5.py        # Module 5 Test Suite (8 Test Cases - PASSED)
│       ├── test_module6.py        # Module 6 Test Suite (8 Test Cases - PASSED)
│       ├── test_module7.py        # Module 7 Test Suite (11 Test Cases - PASSED)
│       ├── test_module8.py        # Module 8 Test Suite (10 Test Cases - PASSED)
│       ├── test_module9.py        # Module 9 Test Suite (11 Test Cases - PASSED)
│       └── test_module10.py       # Module 10 Test Suite (9 Test Cases - PASSED)
│
├── database/
│   ├── schema_module10.sql       # Module 10 DDL Script (14 Volunteer & Task Tables)
│   └── seed_module10.sql         # Seed Data (Demo Volunteers, Skills, Tasks & Assignments)
│
├── frontend/
│   ├── volunteer/
│   │   ├── register.html         # Multi-Step Volunteer Registration Wizard
│   │   └── dashboard.html        # Volunteer Work Console & Active Tasks
│   ├── coordinator/volunteers/
│   │   └── recommendations.html  # Rule-Based Recommendation Review Desk
│   └── assets/
│       └── js/ (volunteer.js, route-map.js, dindi.js, ai-matching.js, item.js, found-person.js, lost-person.js, medical.js, family.js, person.js, api.js, auth.js)
│
├── DOCUMENTATION_MODULE10.md      # Module 10 MDM Documentation
└── README.md                      # Setup & API Testing Guide
```

---

## 🚀 Running the Application

1. Run the Flask Server:
   ```bash
   python backend/app.py
   ```
2. Open Browser at:
   👉 **`http://127.0.0.1:5000/`**

3. Demo Accounts:
   - **Volunteer Desk**: Login with **`volunteer@demo.com`** / **`Demo1234!`** ➔ Open **`/volunteer/dashboard.html`** to check in for shifts, accept assigned tasks, and submit task completion notes!
   - **Task Recommendations**: Login with **`admin@demo.com`** / **`Demo1234!`** ➔ Open **`/coordinator/volunteers/recommendations.html?task_id=1`** to review rule-based volunteer assignment suitability scores (100% weighted score matrix).
   - **Volunteer Registration**: Open **`/volunteer/register.html`** to register as a new WariSeva volunteer.

---

## 🧪 Running Automated Unit Tests

Run All Modules Test Suites:

```bash
python -c "import os; os.remove('database/reuniteai_local.db') if os.path.exists('database/reuniteai_local.db') else None" ; python backend/tests/test_module1.py
```

```bash
python -c "import os; os.remove('database/reuniteai_local.db') if os.path.exists('database/reuniteai_local.db') else None" ; python backend/tests/test_module2.py
```

```bash
python -c "import os; os.remove('database/reuniteai_local.db') if os.path.exists('database/reuniteai_local.db') else None" ; python backend/tests/test_module3.py
```

```bash
python -c "import os; os.remove('database/reuniteai_local.db') if os.path.exists('database/reuniteai_local.db') else None" ; python backend/tests/test_module4.py
```

```bash
python -c "import os; os.remove('database/reuniteai_local.db') if os.path.exists('database/reuniteai_local.db') else None" ; python backend/tests/test_module5.py
```

```bash
python -c "import os; os.remove('database/reuniteai_local.db') if os.path.exists('database/reuniteai_local.db') else None" ; python backend/tests/test_module6.py
```

```bash
python -c "import os; os.remove('database/reuniteai_local.db') if os.path.exists('database/reuniteai_local.db') else None" ; python backend/tests/test_module7.py
```

```bash
python -c "import os; os.remove('database/reuniteai_local.db') if os.path.exists('database/reuniteai_local.db') else None" ; python backend/tests/test_module8.py
```

```bash
python -c "import os; os.remove('database/reuniteai_local.db') if os.path.exists('database/reuniteai_local.db') else None" ; python backend/tests/test_module9.py
```

```bash
python -c "import os; os.remove('database/reuniteai_local.db') if os.path.exists('database/reuniteai_local.db') else None" ; python backend/tests/test_module10.py
```
