"""
WariSeva Module 5 - Automated Test Suite
Executes unit tests for Found Person Assistance & Safe Custody Management against Flask REST APIs.
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import execute_query

class TestModule5FoundPersonAssistance(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Login as Volunteer User (users.id = 6)
        login_vol = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "volunteer@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.volunteer_token = login_vol['data']['session_token']

        # Login as Police Officer (users.id = 4)
        login_police = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "police@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.police_token = login_police['data']['session_token']

    def test_01_report_found_person_unidentified(self):
        """Test reporting an unidentified found pilgrim -> WS-FP-2026-XXXXXX and TEMP-FP-PER-2026-XXXXX"""
        payload = {
            "identification_status": "UNIDENTIFIED_PERSON",
            "approximate_name": "Unidentified Wandering Pilgrim",
            "approximate_age": 70,
            "gender": "MALE",
            "language": "Kannada",
            "communication_status": "CANNOT_COMMUNICATE",
            "zone": "Lonand",
            "landmark": "Lonand Palkhi Pavilion Stage 2",
            "safe_location_name": "Lonand Help Center No. 1",
            "facility_type": "HELP_CENTER",
            "clothing": {
                "top_type": "Kurta",
                "top_color": "White",
                "bottom_type": "Pyjama",
                "bottom_color": "White"
            }
        }
        res = self.app.post('/api/found-person/cases', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.volunteer_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['case_number'].startswith('WS-FP-2026-'))
        self.assertTrue(data['data']['temporary_person_id'].startswith('TEMP-FP-PER-2026-'))

    def test_02_search_existing_profiles(self):
        """Test searching existing Module 2 person profiles for candidate matches"""
        res = self.app.get('/api/found-person/cases/search-profiles?q=Aarav', headers={
            "Authorization": f"Bearer {self.volunteer_token}"
        })

        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['data']), 0)
        self.assertEqual(data['data'][0]['full_name'], 'Aarav Patil')

    def test_03_add_identification_clue(self):
        """Test adding a verbal identification clue"""
        payload = {
            "clue_type": "DINDI_NUMBER",
            "clue_value": "Dindi 27",
            "source": "Verbal statement",
            "confidence": "HIGH"
        }
        res = self.app.post('/api/found-person/cases/1/identification-clues', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.volunteer_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.get_json()['success'])

    def test_04_assign_safe_location(self):
        """Test assigning / transferring person to a safe help center"""
        payload = {
            "location_name": "Saswad Help Center No. 2",
            "facility_type": "HELP_CENTER",
            "status": "AT_HELP_CENTER"
        }
        res = self.app.post('/api/found-person/cases/1/safe-location', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.volunteer_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 201)

    def test_05_log_family_contact(self):
        """Test logging a family contact attempt"""
        payload = {
            "contact_name": "Rajesh Patil",
            "contact_number": "9876543210",
            "relationship": "Father",
            "result": "Contacted father via phone. Father is arriving at Saswad Help Center 2."
        }
        res = self.app.post('/api/found-person/cases/1/family-contact', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.volunteer_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 201)

    def test_06_perform_identity_verification(self):
        """Test identity verification by authorized officer"""
        payload = {
            "verification_status": "VERIFIED",
            "verification_method": "PERSONAL_INFORMATION",
            "verification_notes": "Father confirmed child identity and safety wristband code."
        }
        res = self.app.post('/api/found-person/cases/1/verification', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.police_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 200)

    def test_07_perform_reunification_handover(self):
        """Test performing official reunification handover"""
        payload = {
            "reunited_with": "Rajesh Patil (Father)",
            "reunification_location": "Saswad Help Center No. 2",
            "notes": "Handed over Aarav Patil to father Rajesh Patil after identity verification."
        }
        res = self.app.post('/api/found-person/cases/1/reunification', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.police_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 200)

        # Verify DB status is REUNITED
        c = execute_query("SELECT status FROM found_person_cases WHERE id = 1", fetchone=True)
        self.assertEqual(c['status'], 'REUNITED')

    def test_08_audit_logging_module5(self):
        """Test that Module 5 security events are captured in audit_logs"""
        logs = execute_query("SELECT * FROM audit_logs WHERE action IN ('FOUND_CASE_CREATED', 'FOUND_CASE_SAFE_LOCATION_UPDATED', 'FOUND_CASE_VERIFIED', 'FOUND_CASE_REUNITED')", fetchall=True)
        self.assertGreater(len(logs), 0)

if __name__ == '__main__':
    unittest.main()
