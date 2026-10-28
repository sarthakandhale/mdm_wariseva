"""
ReuniteAI Module 1 - Automated Test Suite
Executes positive and negative test cases against Flask REST APIs & SQLite/MySQL DB.
"""

import os
import sys
import unittest
import json
from datetime import datetime

# Adjust Python path to import app and modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import get_db_connection, execute_query

class TestModule1UserRoleManagement(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_01_health_check(self):
        """Test server static root route"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_02_registration_parent_auto_active(self):
        """Test PARENT_GUARDIAN registration -> Auto ACTIVE status"""
        payload = {
            "full_name": "Test Parent User",
            "mobile": "9998887766",
            "email": "testparent@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "role": "PARENT_GUARDIAN",
            "preferred_language": "or"
        }
        response = self.app.post('/api/auth/register', data=json.dumps(payload), content_type='application/json')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['status'], 'ACTIVE')

    def test_03_registration_volunteer_pending(self):
        """Test VOLUNTEER registration -> PENDING administrative approval"""
        payload = {
            "full_name": "Test Volunteer User",
            "mobile": "9998887755",
            "email": "testvolunteer@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "role": "VOLUNTEER",
            "preferred_language": "en"
        }
        response = self.app.post('/api/auth/register', data=json.dumps(payload), content_type='application/json')
        data = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['status'], 'PENDING')

    def test_04_duplicate_mobile_validation(self):
        """Test duplicate mobile registration -> 409 Conflict"""
        payload = {
            "full_name": "Duplicate Mobile User",
            "mobile": "9998887766", # Registered in test 02
            "email": "unique123@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "role": "PARENT_GUARDIAN"
        }
        response = self.app.post('/api/auth/register', data=json.dumps(payload), content_type='application/json')
        data = response.get_json()

        self.assertEqual(response.status_code, 409)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'AUTH_DUPLICATE_MOBILE')

    def test_05_weak_password_validation(self):
        """Test weak password registration -> 422 Unprocessable Entity"""
        payload = {
            "full_name": "Weak Pwd User",
            "mobile": "9991112233",
            "email": "weak@example.com",
            "password": "simple",
            "confirm_password": "simple",
            "role": "PARENT_GUARDIAN"
        }
        response = self.app.post('/api/auth/register', data=json.dumps(payload), content_type='application/json')
        data = response.get_json()

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data['success'])

    def test_06_login_success_super_admin(self):
        """Test Super Admin login with seed credentials"""
        payload = {
            "identifier": "admin@demo.com",
            "password": "Demo1234!"
        }
        response = self.app.post('/api/auth/login', data=json.dumps(payload), content_type='application/json')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('session_token', data['data'])
        self.assertEqual(data['data']['user']['role'], 'SUPER_ADMIN')

    def test_07_login_pending_account_blocked(self):
        """Test login attempt for PENDING status account -> 403 Forbidden"""
        payload = {
            "identifier": "9998887755", # Volunteer registered in test 03
            "password": "Password123!"
        }
        response = self.app.post('/api/auth/login', data=json.dumps(payload), content_type='application/json')
        data = response.get_json()

        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'AUTH_ACCOUNT_PENDING')

    def test_08_admin_approve_user(self):
        """Test Admin approving pending user account"""
        # 1. Login as Super Admin to get token
        login_res = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "admin@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()

        admin_token = login_res['data']['session_token']

        # 2. Get pending user ID
        user = execute_query("SELECT id FROM users WHERE mobile = '9998887755'", fetchone=True)
        pending_id = user['id']

        # 3. Approve user via API
        approve_res = self.app.put(f'/api/admin/users/{pending_id}/approve', headers={
            "Authorization": f"Bearer {admin_token}"
        })
        data = approve_res.get_json()

        self.assertEqual(approve_res.status_code, 200)
        self.assertTrue(data['success'])

        # 4. Verify user can now login
        login_again = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "9998887755",
            "password": "Password123!"
        }), content_type='application/json').get_json()

        self.assertTrue(login_again['success'])

    def test_09_rbac_unauthorized_access(self):
        """Test Parent user trying to access Admin pending users endpoint -> 403 Forbidden"""
        # Login as Parent
        parent_token = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "parent@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()['data']['session_token']

        # Try to access admin route
        res = self.app.get('/api/admin/users/pending', headers={
            "Authorization": f"Bearer {parent_token}"
        })
        self.assertEqual(res.status_code, 403)

    def test_10_audit_logging_recorded(self):
        """Test that audit log records security events"""
        logs = execute_query("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 5", fetchall=True)
        self.assertGreater(len(logs), 0)

if __name__ == '__main__':
    unittest.main()
