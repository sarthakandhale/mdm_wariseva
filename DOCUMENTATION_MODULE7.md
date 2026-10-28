# WariSeva – Multilingual Smart Platform for Medical Emergency, Lost Person & Item Assistance
## Master Data Management (MDM) & Software Engineering Documentation: Module 7 – AI-Assisted Matching & Intelligent Case Recommendation

**Case Study**: Alandi–Pandharpur Dindi Wari, Maharashtra  
**System Component**: Module 7 – AI-Assisted Matching & Intelligent Case Recommendation Engine  
**Integration Status**: Fully Integrated with Module 1 (Auth, User IDs `users.id`, Session Security, RBAC, Audit Logs), Module 2 (`person_profiles`, `families`), Module 3 (`medical_cases`), Module 4 (`lost_person_cases`), Module 5 (`found_person_cases`), and Module 6 (`lost_item_cases`, `found_item_cases`)  
**Date**: August 16, 2026  
**Document Version**: 7.0.0-PROD  

---

## 1. Module Objective
Module 7 establishes an intelligent AI-assisted matching decision-support engine for WariSeva during the Alandi–Pandharpur Dindi Wari. It compares **Lost Person Cases ↔ Found Person Cases** (Pipeline A) and **Lost Item Cases ↔ Found Item Cases** (Pipeline B), generating candidate recommendations with match scores (0–100%), data quality scores, confidence scores, and human-understandable explanations.

The module operates under a strict principle:
- **Decision Support System**: The AI outputs candidate recommendations (`Potential Match`). It NEVER automatically confirms identity or authorizes reunification without human review.

---

## 2. Real-World Problem Statement
During the crowded Alandi–Pandharpur Dindi Wari, hundreds of lost person reports and found person registrations are filed at different help centers along the 250 km pilgrimage route. Manually cross-referencing descriptions, clothing, ages, and locations across multiple registration desks is slow and error-prone.

Module 7 automates candidate pairing using multi-signal weighted feature matching while leaving final verification in human hands.

---

## 3. Main Actors & Access Control

| Actor | Key Responsibilities | Access Scope |
| :--- | :--- | :--- |
| **Police Officer** | Review AI candidate match recommendations, trigger AI engine, accept matches for identity verification. | Full police AI decision desk |
| **Help Center Operator** | Review AI candidate match recommendations, view side-by-side comparisons, request verification. | Help desk AI decision desk |
| **Event Admin / Super Admin** | Monitor global AI engine performance, view precision/recall metrics, configure feature weights. | Global AI management console |

---

## 4. Functional Requirements (FR)

- **FR-7.1 Modules 1–6 Integration**: Reuses existing `users`, `roles`, `permissions`, `families`, `person_profiles`, `lost_person_cases`, `found_person_cases`, `lost_item_cases`, `found_item_cases`, and `audit_logs`. Does NOT recreate existing user or case tables.
- **FR-7.2 Two Isolated AI Pipelines**:
  - **Pipeline A**: Lost Person (`lost_person_cases`) ↔ Found Person (`found_person_cases`)
  - **Pipeline B**: Lost Item (`lost_item_cases`) ↔ Found Item (`found_item_cases`)
- **FR-7.3 Weighted Person Feature Matching**: Compares Age (15%), Gender (5%), Clothing Attire (20%), Physical Description/Height (15%), Haversine Distance (15%), Timestamp Decay (10%), Dindi Group (10%), Language (5%), Photo Similarity (5%).
- **FR-7.4 Weighted Item Feature Matching**: Compares Category (15%), Brand (15%), Model (20%), Color (10%), Description Overlap (15%), Location Distance (10%), Time Decay (5%), Photo Similarity (10%).
- **FR-7.5 Data Quality & Confidence Scoring**: Calculates data quality score based on field completeness. Adjusts confidence score accordingly: `Confidence = Match Score * (0.6 + 0.4 * (Data Quality / 100))`.
- **FR-7.6 Explainability Engine**: Generates bullet-point explanations (`✓ Similar estimated age (8 vs 8 years)`, `✓ Same Dindi group`, `✓ Nearby location`).
- **FR-7.7 Human Review Workflow**: Operator reviews candidate match (`GENERATED` ➔ `ACCEPTED_FOR_VERIFICATION` or `REJECTED` / `FALSE_MATCH`).
- **FR-7.8 Prohibit Automatic Reunification**: The API explicitly rejects attempts to declare `CONFIRMED_IDENTITY` directly from AI review.

---

## 5. Feature Engineering & Weight Specifications

### Pipeline A: Person Matching Weights
```python
PERSON_WEIGHTS = {
    'age': 0.15,
    'gender': 0.05,
    'clothing': 0.20,
    'physical': 0.15,
    'location': 0.15,
    'time': 0.10,
    'dindi': 0.10,
    'language': 0.05,
    'image': 0.05
}
```

### Pipeline B: Item Matching Weights
```python
ITEM_WEIGHTS = {
    'category': 0.15,
    'brand': 0.15,
    'model': 0.20,
    'color': 0.10,
    'description': 0.15,
    'location': 0.10,
    'time': 0.05,
    'image': 0.10
}
```

---

## 6. Database Schema (`ai_match_results`)

```sql
CREATE TABLE IF NOT EXISTS ai_match_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    match_type ENUM('PERSON', 'ITEM') NOT NULL DEFAULT 'PERSON',
    source_case_id INT NOT NULL,
    candidate_case_id INT NOT NULL,
    match_score INT NOT NULL,
    confidence_score INT NOT NULL,
    data_quality_score INT NOT NULL,
    explanation TEXT NULL,
    model_version VARCHAR(50) DEFAULT 'v1.0-Hybrid',
    status ENUM('GENERATED', 'UNDER_REVIEW', 'ACCEPTED_FOR_VERIFICATION', 'REJECTED', 'VERIFIED', 'FALSE_MATCH', 'EXPIRED') NOT NULL DEFAULT 'GENERATED',
    reviewed_by INT NULL,
    reviewed_at TIMESTAMP NULL,
    review_notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
);
```

---

## 7. REST API Specifications

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/ai/match/person/{id}` | Authorized Staff | Trigger Pipeline A person matching |
| `GET` | `/api/ai/matches/person/{id}` | Authenticated User | Get candidate person matches for a lost case |
| `POST` | `/api/ai/match/item/{id}` | Authorized Staff | Trigger Pipeline B item matching |
| `GET` | `/api/ai/matches/item/{id}` | Authenticated User | Get candidate item matches for a lost item case |
| `GET` | `/api/ai/matches/{id}` | Authenticated User | Get side-by-side comparison details & reasons |
| `PATCH` | `/api/ai/matches/{id}/review` | Police / Help Desk | Human operator review decision (`ACCEPTED_FOR_VERIFICATION` / `REJECTED`) |
| `GET` | `/api/ai/dashboard` | Authenticated User | Get AI metrics & recent match recommendations |
| `GET` | `/api/ai/evaluation` | Authorized Staff | Get model evaluation metrics (Precision, Recall, F1, Confusion Matrix) |

---

## 8. Test Cases & Validation Suite (`backend/tests/test_module7.py`)

| Test ID | Description | Input Data | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-7.1** | Haversine Distance | Lat/Lon coordinates | Distance ~17.9 km calculated | **PASSED** |
| **TC-7.2** | Age Similarity Decay | Age 8 vs 8, 8 vs 45 | Score 1.0 vs 0.0 | **PASSED** |
| **TC-7.3** | Pipeline A Person Match | Lost Case #1 | Candidates generated, HTTP 200 | **PASSED** |
| **TC-7.4** | Get Person Matches | Lost Case #1 | Recommendation list returned | **PASSED** |
| **TC-7.5** | Pipeline B Item Match | Lost Item #1 | Candidate items generated | **PASSED** |
| **TC-7.6** | Side-by-Side Details | Match ID #1 | Source & candidate cases + reasons | **PASSED** |
| **TC-7.7** | Operator Review | Decision `ACCEPTED_FOR_VERIFICATION` | Status updated to `ACCEPTED_FOR_VERIFICATION` | **PASSED** |
| **TC-7.8** | Prohibit Auto-Reunification | Decision `CONFIRMED_IDENTITY` | Rejected with HTTP 400 Bad Request | **PASSED** |
| **TC-7.9** | AI Dashboard Metrics | GET `/api/ai/dashboard` | AI metrics returned | **PASSED** |
| **TC-7.10**| Model Evaluation Metrics | GET `/api/ai/evaluation` | Precision, Recall, F1, Confusion Matrix returned | **PASSED** |
| **TC-7.11**| Audit Logging | AI match actions | Security events recorded in `audit_logs` | **PASSED** |

---

## 9. Model Performance Metrics (Evaluation Dataset)

```json
{
  "model_name": "WariSeva Hybrid Similarity Engine",
  "model_version": "v1.0-Hybrid",
  "precision": 0.918,
  "recall": 0.882,
  "f1_score": 0.900,
  "confusion_matrix": {
    "TP": 45,
    "FP": 4,
    "FN": 6,
    "TN": 120
  }
}
```

---

## 10. Security & Privacy Controls

1. **RBAC & Authorization**: Only authorized staff (Police, Help Center, Admin) can trigger AI pipelines or update review decisions.
2. **Prohibition of Auto-Identity**: Strict policy preventing automatic status changes to `REUNITED` or `RETURNED` directly from AI.
3. **Data Minimization**: AI processing uses only relevant visual, clothing, physical, and location attributes. Confidential medical notes or private contact numbers are excluded from feature vectors.
4. **Audit Logging**: All AI execution, match viewing, and operator review decisions are logged in `audit_logs`.
