"""
WariSeva Module 8 - Automated Test Suite
Executes unit tests for Dindi Management & Warkari Group Coordination against Flask REST APIs.
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import execute_query

class TestModule8DindiManagement(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Login as Event Admin / Dindi Leader User (users.id = 2)
        login_leader = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "eventadmin@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.leader_token = login_leader['data']['session_token']

        # Login as Admin User (users.id = 1)
        login_admin = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "admin@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.admin_token = login_admin['data']['session_token']


    def test_01_create_dindi(self):
        """Test registering a new Dindi group -> WS-DIN-2026-000099"""
        payload = {
            "dindi_number": 99,
            "name": "Shree Mauli Dindi No. 99",
            "description": "Registered Warkari group from Alandi to Pandharpur",
            "start_location": "Alandi",
            "destination": "Pandharpur",
            "expected_member_count": 300,
            "contact_name": "Mauli Leader",
            "contact_number": "+91 98220 77777"
        }
        res = self.app.post('/api/dindis', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.leader_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['dindi_number'], 99)
        self.assertTrue(data['data']['dindi_code'].startswith('WS-DIN-2026-'))

    def test_02_prevent_duplicate_dindi_number(self):
        """Test API prevents duplicate Dindi number registration"""
        payload = {
            "dindi_number": 27, # Already exists in seed
            "name": "Duplicate Dindi 27"
        }
        res = self.app.post('/api/dindis', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.leader_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.get_json()['success'])

    def test_03_get_dindi_details(self):
        """Test retrieving full details of Dindi 27"""
        res = self.app.get('/api/dindis/1', headers={
            "Authorization": f"Bearer {self.leader_token}"
        })
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['data']['dindi_number'], 27)
        self.assertIn('schedules', data['data'])
        self.assertIn('announcements', data['data'])

    def test_04_enroll_dindi_member(self):
        """Test enrolling a person profile into Dindi membership"""
        payload = {
            "person_id": 1,
            "role": "MEMBER"
        }
        # First ensure person 1 is not already in dindi 2
        res = self.app.post('/api/dindis/2/members', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.leader_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])

    def test_05_prevent_duplicate_dindi_membership(self):
        """Test API prevents enrolling duplicate membership in same Dindi"""
        payload = {
            "person_id": 1,
            "role": "MEMBER"
        }
        res = self.app.post('/api/dindis/1/members', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.leader_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 400)

    def test_06_assign_dindi_leader(self):
        """Test admin assigning assistant leader to a Dindi"""
        payload = {
            "user_id": 6,
            "role": "ASSISTANT_LEADER"
        }
        res = self.app.post('/api/dindis/1/leaders', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.admin_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.get_json()['success'])

    def test_07_create_dindi_schedule(self):
        """Test leader publishing daily halt and march schedule"""
        payload = {
            "schedule_date": "2026-07-04",
            "start_location": "Jejuri",
            "end_location": "Lonand",
            "expected_start_time": "05:30 AM",
            "expected_arrival_time": "06:00 PM",
            "rest_point": "Valha Rest Tent",
            "notes": "Halt at Valha water station"
        }
        res = self.app.post('/api/dindis/1/schedule', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.leader_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.get_json()['success'])

    def test_08_create_dindi_announcement(self):
        """Test publishing an announcement to Dindi members"""
        payload = {
            "title": "Medical Camp Support Available",
            "message": "Free medical checkup tent active at Saswad halt.",
            "priority": "URGENT"
        }
        res = self.app.post('/api/dindis/1/announcements', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.leader_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.get_json()['success'])

    def test_09_verify_dindi_status(self):
        """Test admin verifying a Dindi registration"""
        payload = {
            "status": "VERIFIED",
            "verification_notes": "Official registration documents verified."
        }
        res = self.app.post('/api/dindis/1/verify', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.admin_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 200)

    def test_10_audit_logging_module8(self):
        """Test that Module 8 security events are captured in audit_logs"""
        logs = execute_query("SELECT * FROM audit_logs WHERE action IN ('DINDI_CREATED', 'DINDI_VERIFIED', 'DINDI_MEMBER_ADDED', 'DINDI_ANNOUNCEMENT_CREATED')", fetchall=True)
        self.assertGreater(len(logs), 0)

if __name__ == '__main__':
    unittest.main()
