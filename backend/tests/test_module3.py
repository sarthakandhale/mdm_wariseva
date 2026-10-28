"""
WariSeva Module 3 - Automated Test Suite
Executes unit tests for Medical Emergency Assistance against Flask REST APIs.
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import execute_query

class TestModule3MedicalEmergencyAssistance(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Login as Parent User (users.id = 7)
        login_parent = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "parent@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.parent_token = login_parent['data']['session_token']

        # Login as Doctor Medical Staff (users.id = 5)
        login_doc = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "medical@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.doctor_token = login_doc['data']['session_token']

        # Login as Volunteer User (users.id = 6)
        login_vol = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "volunteer@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.volunteer_token = login_vol['data']['session_token']

    def test_01_report_emergency_family_member(self):
        """Test reporting emergency for registered family member -> WS-MED-2026-XXXXXX"""
        payload = {
            "patient_person_id": 4, # Sunita Patil (Elderly)
            "emergency_type": "BREATHING_DIFFICULTY",
            "reported_severity": "CRITICAL",
            "symptoms": ["Chest Pain", "Difficulty Breathing", "Dizziness"],
            "zone": "Saswad",
            "landmark": "Saswad Halt Tent 4",
            "description": "Elderly grandmother experiencing severe breathing tightness."
        }
        res = self.app.post('/api/medical/cases', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.parent_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['case_number'].startswith('WS-MED-2026-'))
        self.assertEqual(data['data']['priority_level'], 'CRITICAL')
        self.assertGreaterEqual(data['data']['priority_score'], 75)

    def test_02_report_emergency_unidentified_victim(self):
        """Test reporting emergency for unidentified victim -> patient_person_id NULL & TEMP-PAT-2026-XXXXX"""
        payload = {
            "temp_patient_name": "Unconscious Male Pilgrim",
            "temp_patient_age": 58,
            "temp_patient_gender": "MALE",
            "temp_patient_description": "Found near Pargaon bridge",
            "emergency_type": "FAINTING",
            "reported_severity": "CRITICAL",
            "symptoms": ["Unconsciousness"],
            "zone": "Lonand",
            "landmark": "Pargaon Bridge",
            "is_unconscious": True
        }
        res = self.app.post('/api/medical/cases', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.volunteer_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertIsNone(data['data']['patient_person_id'])
        self.assertTrue(data['data']['temp_patient_code'].startswith('TEMP-PAT-2026-'))
        self.assertIn(data['data']['priority_level'], ['HIGH', 'CRITICAL'])


    def test_03_priority_calculation_engine(self):
        """Test priority score calculation for Chest Pain + Unconscious + Elderly => Score >= 75 (CRITICAL)"""
        from services.priority_engine import calculate_medical_priority
        score, level, reasons = calculate_medical_priority(
            emergency_type="CHEST_PAIN",
            symptoms=["Chest Pain", "Difficulty Breathing", "Unconsciousness"],
            age=68,
            is_elderly=True,
            location_zone="Saswad",
            is_unconscious=True
        )
        self.assertGreaterEqual(score, 75)
        self.assertEqual(level, 'CRITICAL')
        self.assertIn("Unconsciousness", reasons)


    def test_04_request_and_assign_ambulance(self):
        """Test requesting and dispatching ambulance"""
        # Request ambulance as parent
        req_res = self.app.post('/api/medical/cases/1/ambulance', headers={
            "Authorization": f"Bearer {self.parent_token}"
        })
        self.assertIn(req_res.status_code, [200, 201])

        # Assign ambulance as Doctor
        assign_res = self.app.post('/api/medical/cases/1/assign', data=json.dumps({
            "ambulance_id": 1
        }), headers={
            "Authorization": f"Bearer {self.doctor_token}"
        }, content_type='application/json')
        self.assertEqual(assign_res.status_code, 200)

    def test_05_record_treatment_authorized_doctor(self):
        """Test recording treatment by authorized doctor"""
        payload = {
            "assessment": "Acute asthmatic attack with hypertension 150/90",
            "treatment_provided": "1L Normal Saline IV, Nebulization with Salbutamol",
            "medication": "Salbutamol Inhaler, Paracetamol 500mg",
            "observation": "Patient breathing stabilized"
        }
        res = self.app.post('/api/medical/cases/1/treatment', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.doctor_token}"
        }, content_type='application/json')
        self.assertEqual(res.status_code, 201)

    def test_06_unauthorized_treatment_access_volunteer(self):
        """Test volunteer attempting to record treatment -> HTTP 403 Forbidden"""
        payload = {
            "assessment": "Unauthorized treatment attempt",
            "treatment_provided": "None"
        }
        res = self.app.post('/api/medical/cases/1/treatment', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.volunteer_token}"
        }, content_type='application/json')
        self.assertEqual(res.status_code, 403)

    def test_07_record_referral(self):
        """Test creating hospital referral"""
        payload = {
            "to_facility_name": "Pandharpur Civil Hospital",
            "reason": "Requires specialized cardiac ICU monitoring",
            "ambulance_required": True
        }
        res = self.app.post('/api/medical/cases/1/referral', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.doctor_token}"
        }, content_type='application/json')
        self.assertEqual(res.status_code, 201)

    def test_08_case_status_transition(self):
        """Test transitioning case status to RESOLVED"""
        res = self.app.patch('/api/medical/cases/1/status', data=json.dumps({
            "status": "RESOLVED",
            "reason": "Patient treated successfully and discharged"
        }), headers={
            "Authorization": f"Bearer {self.doctor_token}"
        }, content_type='application/json')
        self.assertEqual(res.status_code, 200)

    def test_09_medical_facilities_and_nearby_api(self):
        """Test GET /api/medical/facilities and /api/medical/facilities/nearby"""
        res_fac = self.app.get('/api/medical/facilities')
        self.assertEqual(res_fac.status_code, 200)
        self.assertGreater(len(res_fac.get_json()['data']), 0)

        res_near = self.app.get('/api/medical/facilities/nearby?lat=18.3444&lon=74.0306')
        self.assertEqual(res_near.status_code, 200)
        self.assertGreater(len(res_near.get_json()['data']), 0)

    def test_10_ambulances_and_dashboard_api(self):
        """Test GET /api/medical/ambulances and /api/medical/dashboard"""
        res_amb = self.app.get('/api/medical/ambulances')
        self.assertEqual(res_amb.status_code, 200)

        res_dash = self.app.get('/api/medical/dashboard', headers={
            "Authorization": f"Bearer {self.doctor_token}"
        })
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn('critical_cases', res_dash.get_json()['data'])

    def test_11_audit_logging_module3(self):
        """Test that Module 3 audit logs are captured in audit_logs table"""
        logs = execute_query("SELECT * FROM audit_logs WHERE action IN ('MEDICAL_CASE_CREATED', 'AMBULANCE_REQUESTED', 'AMBULANCE_ASSIGNED', 'MEDICAL_TREATMENT_RECORDED', 'MEDICAL_REFERRAL_CREATED')", fetchall=True)
        self.assertGreater(len(logs), 0)

if __name__ == '__main__':
    unittest.main()
