"""
ReuniteAI Module 2 - Automated Test Suite
Executes unit tests for Family & Person Profile Management against Flask REST APIs.
"""

import os
import sys
import unittest
import json
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import execute_query

class TestModule2FamilyPersonManagement(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Login as Parent Demo User (users.id = 7)
        login_res = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "parent@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.parent_token = login_res['data']['session_token']

        # Login as Volunteer User (users.id = 6) for unauthorized access tests
        login_vol = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "volunteer@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.volunteer_token = login_vol['data']['session_token']

    def test_01_create_family(self):
        """Test family creation -> RY-FAM-2026-XXXXXX generated"""
        payload = {
            "family_name": "Sharma Pilgrims",
            "primary_contact_name": "Ramesh Patnaik",
            "primary_contact_mobile": "9812345678",
            "emergency_contact_name": "Suresh Patnaik",
            "emergency_contact_mobile": "9812345679",
            "preferred_language": "or"
        }
        res = self.app.post('/api/families', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.parent_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['family_code'].startswith('RY-FAM-2026-'))
        self.created_family_id = data['data']['id']

    def test_02_add_child_member_age_calculation(self):
        """Test adding child member -> Auto Age & CHILD classification"""
        payload = {
            "full_name": "Rohan Sharma",
            "date_of_birth": "2019-06-10", # 7 years old -> CHILD
            "gender": "MALE",
            "relationship": "Son",
            "height": "3ft 8in",
            "top_type": "T-Shirt",
            "top_color": "Yellow",
            "medical_condition": "None"
        }
        res = self.app.post('/api/families/1/members', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.parent_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['age_category'], 'CHILD')
        self.assertTrue(data['data']['person_code'].startswith('RY-PER-2026-'))

    def test_03_add_elderly_member(self):
        """Test adding elderly member -> Auto Age & ELDERLY classification"""
        payload = {
            "full_name": "Kamla Devi",
            "date_of_birth": "1955-02-14", # 71 years old -> ELDERLY
            "gender": "FEMALE",
            "relationship": "Grandmother",
            "walking_assistance": True,
            "medical_condition": "Hypertension"
        }
        res = self.app.post('/api/families/1/members', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.parent_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['data']['age_category'], 'ELDERLY')

    def test_04_unauthorized_family_access(self):
        """Test user trying to access another user's family -> HTTP 403 Forbidden"""
        res = self.app.get('/api/families/1', headers={
            "Authorization": f"Bearer {self.volunteer_token}"
        })
        self.assertEqual(res.status_code, 403)

    def test_05_photo_upload_valid_and_invalid(self):
        """Test photo upload validation (accept valid image, reject text file)"""
        # 1. Invalid file format test (.txt)
        bad_data = {
            'photo': (io.BytesIO(b"fake text content"), "test.txt")
        }
        bad_res = self.app.post('/api/persons/1/photos', data=bad_data, headers={
            "Authorization": f"Bearer {self.parent_token}"
        }, content_type='multipart/form-data')
        self.assertEqual(bad_res.status_code, 400)

        # 2. Valid PNG upload test
        valid_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
        good_data = {
            'photo': (io.BytesIO(valid_png), "avatar.png")
        }
        good_res = self.app.post('/api/persons/1/photos', data=good_data, headers={
            "Authorization": f"Bearer {self.parent_token}"
        }, content_type='multipart/form-data')
        self.assertEqual(good_res.status_code, 201)
        self.assertTrue(good_res.get_json()['success'])

    def test_06_deactivate_family_member(self):
        """Test soft deactivation of family member -> status INACTIVE"""
        res = self.app.patch('/api/families/1/members/1/deactivate', headers={
            "Authorization": f"Bearer {self.parent_token}"
        })
        self.assertEqual(res.status_code, 200)

        # Verify soft deletion in DB
        person = execute_query("SELECT status FROM person_profiles WHERE id = 1", fetchone=True)
        self.assertEqual(person['status'], 'INACTIVE')

    def test_07_module2_audit_logging(self):
        """Test that Module 2 audit logs are recorded in audit_logs table"""
        logs = execute_query("SELECT * FROM audit_logs WHERE action IN ('FAMILY_CREATED', 'MEMBER_ADDED', 'MEMBER_DEACTIVATED', 'PHOTO_UPLOADED')", fetchall=True)
        self.assertGreater(len(logs), 0)

if __name__ == '__main__':
    unittest.main()
