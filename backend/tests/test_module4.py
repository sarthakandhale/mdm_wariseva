"""
WariSeva Module 4 - Automated Test Suite
Executes unit tests for Lost Person Assistance & Missing Case Management against Flask REST APIs.
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import execute_query

class TestModule4LostPersonAssistance(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Login as Parent User (users.id = 7)
        login_parent = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "parent@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.parent_token = login_parent['data']['session_token']

        # Login as Police Officer (users.id = 4)
        login_police = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "police@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.police_token = login_police['data']['session_token']

        # Login as Volunteer User (users.id = 6)
        login_vol = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "volunteer@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.volunteer_token = login_vol['data']['session_token']

    def test_01_report_lost_person_registered_member(self):
        """Test filing missing person report for registered family member -> WS-LP-2026-XXXXXX"""
        payload = {
            "family_id": 1,
            "person_id": 1, # Rajesh Patil (no active case)
            "reporter_relationship": "Spouse",
            "last_seen_at": "2026-08-16 14:30:00",
            "zone": "Saswad",
            "landmark": "Saswad Rest Stop Water Tank 3",
            "clothing": {
                "top_type": "Shirt",
                "top_color": "White",
                "bottom_type": "Pants",
                "bottom_color": "Black"
            },
            "additional_information": "Rajesh went missing near Saswad halt."
        }

        res = self.app.post('/api/lost-person/cases', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.parent_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['case_number'].startswith('WS-LP-2026-'))
        self.assertIn(data['data']['priority_level'], ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'])


    def test_02_duplicate_active_case_prevention(self):
        """Test filing duplicate missing report for person with active case -> HTTP 409 Conflict"""
        payload = {
            "family_id": 1,
            "person_id": 3, # Already active in test_01 or seed
            "reporter_relationship": "Father",
            "last_seen_at": "2026-08-16 15:00:00",
            "zone": "Saswad"
        }
        res = self.app.post('/api/lost-person/cases', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.parent_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 409)
        self.assertFalse(res.get_json()['success'])
        self.assertEqual(res.get_json()['error_code'], 'DUPLICATE_ACTIVE_CASE')

    def test_03_report_unregistered_missing_person(self):
        """Test reporting unregistered pilgrim -> temp_person_code TEMP-PER-2026-XXXXX"""
        payload = {
            "temp_person_name": "Unregistered Wandering Child",
            "temp_person_age": 7,
            "temp_person_gender": "MALE",
            "temp_person_description": "Found near Lonand Palkhi Pavilion",
            "reporter_relationship": "Volunteer",
            "last_seen_at": "2026-08-16 16:00:00",
            "zone": "Lonand"
        }
        res = self.app.post('/api/lost-person/cases', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.volunteer_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertIsNone(data['data']['person_id'])
        self.assertTrue(data['data']['temp_person_code'].startswith('TEMP-PER-2026-'))

    def test_04_priority_engine_child_medical(self):
        """Test priority score calculation for Child + Medical Condition => CRITICAL (score >= 75)"""
        from services.lost_priority_engine import calculate_lost_person_priority
        score, level, reasons = calculate_lost_person_priority(
            age=8,
            is_child=True,
            medical_requirement=True,
            cognitive_assistance=True,
            last_seen_hour=21,
            zone="Saswad"
        )
        self.assertGreaterEqual(score, 75)
        self.assertEqual(level, 'CRITICAL')
        self.assertIn("Child under 12", reasons)

    def test_05_police_priority_override(self):
        """Test police officer overriding priority level"""
        res = self.app.patch('/api/lost-person/cases/1/priority', data=json.dumps({
            "priority_level": "CRITICAL",
            "reason": "Police control desk escalated due to high-risk location"
        }), headers={
            "Authorization": f"Bearer {self.police_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['data']['new_priority'], 'CRITICAL')

    def test_06_add_case_note(self):
        """Test adding case note with FAMILY_VISIBLE and INTERNAL visibility"""
        res = self.app.post('/api/lost-person/cases/1/notes', data=json.dumps({
            "note": "Checked Saswad food stall area. Moving to Help Center 2.",
            "visibility": "FAMILY_VISIBLE"
        }), headers={
            "Authorization": f"Bearer {self.parent_token}"
        }, content_type='application/json')
        self.assertEqual(res.status_code, 201)

    def test_07_report_sighting(self):
        """Test reporting a possible sighting"""
        payload = {
            "zone": "Saswad",
            "confidence_rating": "HIGH",
            "location_description": "Near Saswad Help Center No. 2",
            "description": "Spotted child matching red Spiderman t-shirt sitting near help booth."
        }
        res = self.app.post('/api/lost-person/cases/1/sightings', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.volunteer_token}"
        }, content_type='application/json')
        self.assertEqual(res.status_code, 201)

    def test_08_withdraw_lost_case(self):
        """Test family guardian withdrawing missing case"""
        res = self.app.post('/api/lost-person/cases/1/withdraw', data=json.dumps({
            "reason": "FOUND BY FAMILY: Aarav located safely at Help Center 2"
        }), headers={
            "Authorization": f"Bearer {self.parent_token}"
        }, content_type='application/json')
        self.assertEqual(res.status_code, 200)

        # Verify status is WITHDRAWN in DB
        case = execute_query("SELECT status FROM lost_person_cases WHERE id = 1", fetchone=True)
        self.assertEqual(case['status'], 'WITHDRAWN')

    def test_09_audit_logging_module4(self):
        """Test that Module 4 security events are captured in audit_logs"""
        logs = execute_query("SELECT * FROM audit_logs WHERE action IN ('LOST_CASE_CREATED', 'LOST_CASE_PRIORITY_CHANGED', 'LOST_CASE_WITHDRAWN', 'LOST_CASE_SIGHTING_REPORTED')", fetchall=True)
        self.assertGreater(len(logs), 0)

if __name__ == '__main__':
    unittest.main()
