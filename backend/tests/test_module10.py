"""
WariSeva Module 10 - Automated Test Suite
Executes unit tests for Volunteer Management & Task Assignment against Flask REST APIs.
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import execute_query

class TestModule10VolunteerManagement(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Login as Admin User (users.id = 1)
        login_admin = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "admin@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.admin_token = login_admin['data']['session_token']

        # Login as Volunteer User (users.id = 6)
        login_vol = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "volunteer@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.vol_token = login_vol['data']['session_token']

    def test_01_register_volunteer(self):
        """Test registering a new volunteer -> WS-VOL-2026-000003"""
        payload = {
            "experience_years": 4,
            "preferred_zone": "Jejuri",
            "emergency_contact": "+91 98220 88776",
            "skills": [{"skill_name": "FIRST_AID", "skill_level": "CERTIFIED"}],
            "languages": ["Marathi", "English"]
        }
        res = self.app.post('/api/volunteers', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.vol_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['volunteer_code'].startswith('WS-VOL-2026-'))

    def test_02_verify_volunteer_status(self):
        """Test admin verifying a volunteer's registration status"""
        payload = {
            "status": "VERIFIED",
            "verification_notes": "Identity documents verified."
        }
        res = self.app.patch('/api/volunteers/1/status', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.admin_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 200)

    def test_03_volunteer_checkin_checkout(self):
        """Test shift check-in and check-out tracking"""
        res_in = self.app.post('/api/volunteers/1/check-in', data=json.dumps({"shift_id": 1}), headers={
            "Authorization": f"Bearer {self.vol_token}"
        }, content_type='application/json')
        self.assertEqual(res_in.status_code, 201)

        res_out = self.app.post('/api/volunteers/1/check-out', data=json.dumps({}), headers={
            "Authorization": f"Bearer {self.vol_token}"
        }, content_type='application/json')
        self.assertEqual(res_out.status_code, 200)

    def test_04_create_volunteer_task(self):
        """Test creating a new volunteer task -> WS-TASK-2026-000002"""
        payload = {
            "title": "Water Point Assistance at Saswad Halt 3",
            "description": "Distribute drinking water to arriving Dindis at Saswad",
            "task_type": "ROUTE_ASSISTANCE",
            "priority": "MEDIUM",
            "source_module": "MODULE_9",
            "zone": "Saswad",
            "required_skill": "GENERAL",
            "required_language": "Marathi"
        }
        res = self.app.post('/api/volunteer-tasks', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.admin_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['task_code'].startswith('WS-TASK-2026-'))

    def test_05_get_task_recommendations(self):
        """Test 100% weighted rule-based assignment recommendation engine"""
        res = self.app.get('/api/volunteer-tasks/1/recommendations', headers={
            "Authorization": f"Bearer {self.admin_token}"
        })

        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['data']), 0)
        self.assertIn('total_score', data['data'][0])

    def test_06_assign_and_accept_task(self):
        """Test coordinator assigning task and volunteer accepting"""
        assign_res = self.app.post('/api/volunteer-tasks/1/assign', data=json.dumps({"volunteer_id": 1}), headers={
            "Authorization": f"Bearer {self.admin_token}"
        }, content_type='application/json')
        self.assertEqual(assign_res.status_code, 200)

        accept_res = self.app.post('/api/volunteer-tasks/1/accept', data=json.dumps({"volunteer_id": 1}), headers={
            "Authorization": f"Bearer {self.vol_token}"
        }, content_type='application/json')
        self.assertEqual(accept_res.status_code, 200)

    def test_07_complete_and_verify_task(self):
        """Test volunteer completing task and coordinator verifying completion"""
        comp_res = self.app.post('/api/volunteer-tasks/1/complete', data=json.dumps({"volunteer_id": 1, "completion_notes": "Child reunited with family."}), headers={
            "Authorization": f"Bearer {self.vol_token}"
        }, content_type='application/json')
        self.assertEqual(comp_res.status_code, 200)

        ver_res = self.app.post('/api/volunteer-tasks/1/verify', data=json.dumps({}), headers={
            "Authorization": f"Bearer {self.admin_token}"
        }, content_type='application/json')
        self.assertEqual(ver_res.status_code, 200)

    def test_08_decline_task_flow(self):
        """Test volunteer declining assigned task with reason"""
        self.app.post('/api/volunteer-tasks/2/assign', data=json.dumps({"volunteer_id": 1}), headers={
            "Authorization": f"Bearer {self.admin_token}"
        }, content_type='application/json')

        dec_res = self.app.post('/api/volunteer-tasks/2/decline', data=json.dumps({"volunteer_id": 1, "decline_reason": "Assigned to medical emergency"}), headers={
            "Authorization": f"Bearer {self.vol_token}"
        }, content_type='application/json')
        self.assertEqual(dec_res.status_code, 200)

    def test_09_audit_logging_module10(self):
        """Test that Module 10 security events are captured in audit_logs"""
        logs = execute_query("SELECT * FROM audit_logs WHERE action IN ('VOLUNTEER_REGISTERED', 'VOLUNTEER_VERIFIED', 'TASK_CREATED', 'TASK_ASSIGNED', 'TASK_ACCEPTED', 'TASK_COMPLETED', 'TASK_VERIFIED')", fetchall=True)
        self.assertGreater(len(logs), 0)

if __name__ == '__main__':
    unittest.main()
