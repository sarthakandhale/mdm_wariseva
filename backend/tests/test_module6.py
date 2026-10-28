"""
WariSeva Module 6 - Automated Test Suite
Executes unit tests for Lost & Found Item Assistance & Recovery Management against Flask REST APIs.
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import execute_query

class TestModule6ItemAssistance(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Login as Parent User (users.id = 7)
        login_parent = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "parent@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.parent_token = login_parent['data']['session_token']

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

    def test_01_report_lost_item(self):
        """Test reporting a lost item -> WS-LI-2026-XXXXXX"""
        payload = {
            "item_category": "MOBILE_PHONE",
            "item_name": "iPhone 13 Pro",
            "brand": "Apple",
            "model": "13 Pro",
            "color": "Sierra Blue",
            "approximate_value": 75000,
            "serial_number": "SN-APP-776655",
            "imei": "358910293847561",
            "description": "Lost near Jejuri temple halt",
            "zone": "Jejuri",
            "landmark": "Jejuri Temple Arch"
        }
        res = self.app.post('/api/lost-items', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.parent_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['case_number'].startswith('WS-LI-2026-'))

    def test_02_report_found_item(self):
        """Test registering a found physical item -> WS-FI-2026-XXXXXX"""
        payload = {
            "item_category": "MOBILE_PHONE",
            "item_name": "Sierra Blue Smartphone",
            "brand": "Apple",
            "color": "Blue",
            "condition": "GOOD",
            "description": "Found near Jejuri temple arch steps",
            "zone": "Jejuri",
            "landmark": "Jejuri Temple Arch",
            "facility_name": "Jejuri Police Post Locker Desk"
        }
        res = self.app.post('/api/found-items', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.volunteer_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['case_number'].startswith('WS-FI-2026-'))

    def test_03_privacy_masking_sensitive_fields(self):
        """Test that IMEI and serial numbers are masked for non-owner public views"""
        res = self.app.get('/api/lost-items/1', headers={
            "Authorization": f"Bearer {self.volunteer_token}"
        })
        data = res.get_json()['data']
        self.assertTrue(data['imei'].startswith('****'))
        self.assertTrue(data['serial_number'].startswith('****'))

    def test_04_submit_owner_claim(self):
        """Test submitting owner claim for a found item -> CLM-2026-XXXXXX"""
        payload = {
            "claim_description": "This is my Samsung Galaxy phone. Wallpaper has picture of Vitthal temple."
        }
        res = self.app.post('/api/found-items/1/claims', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.parent_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['data']['claim_number'].startswith('CLM-2026-'))

    def test_05_verify_and_approve_claim(self):
        """Test officer approving claim and auto-rejecting competing claims"""
        payload = {
            "status": "APPROVED",
            "notes": "Claimant provided correct wallpaper description and matching model."
        }
        res = self.app.post('/api/claims/1/verify', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.police_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 200)

        # Verify found item status is VERIFICATION
        fi = execute_query("SELECT status FROM found_item_cases WHERE id = 1", fetchone=True)
        self.assertEqual(fi['status'], 'VERIFICATION')

    def test_06_manual_item_matching(self):
        """Test manual pairing of Lost Item ↔ Found Item"""
        payload = {
            "lost_item_case_id": 1,
            "found_item_case_id": 1,
            "match_reason": "Matching Samsung Galaxy A54 phone lost and found at Saswad water dispenser."
        }
        res = self.app.post('/api/item-matches/manual', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.police_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.get_json()['success'])

    def test_07_release_found_item(self):
        """Test formal return handover of physical item to verified owner"""
        payload = {
            "returned_to": "Rajesh Patil (Owner)",
            "return_location": "Saswad Help Center Storage Tent 2",
            "notes": "Verified ID document and claim proof before release."
        }
        res = self.app.post('/api/found-items/1/release', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.police_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 200)

        # Verify status is RETURNED
        fi = execute_query("SELECT status FROM found_item_cases WHERE id = 1", fetchone=True)
        self.assertEqual(fi['status'], 'RETURNED')

    def test_08_audit_logging_module6(self):
        """Test that Module 6 security events are captured in audit_logs"""
        logs = execute_query("SELECT * FROM audit_logs WHERE action IN ('LOST_ITEM_CREATED', 'FOUND_ITEM_CREATED', 'CLAIM_APPROVED', 'ITEM_RELEASED')", fetchall=True)
        self.assertGreater(len(logs), 0)

if __name__ == '__main__':
    unittest.main()
