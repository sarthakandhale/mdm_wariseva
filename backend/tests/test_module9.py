"""
WariSeva Module 9 - Automated Test Suite
Executes unit tests for Dindi Route, Location & Movement Management against Flask REST APIs.
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import execute_query
from services.route_location_service import calculate_haversine_distance

class TestModule9RouteLocationManagement(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Login as Admin User (users.id = 1)
        login_admin = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "admin@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.admin_token = login_admin['data']['session_token']

        # Login as Leader User (users.id = 2)
        login_leader = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "eventadmin@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.leader_token = login_leader['data']['session_token']

    def test_01_haversine_distance_calculation(self):
        """Test Haversine distance formula accuracy (Alandi to Pune ~ 17.9 km)"""
        dist = calculate_haversine_distance(18.6773, 73.8968, 18.5204, 73.8567)
        self.assertIsNotNone(dist)
        self.assertAlmostEqual(dist, 17.9, delta=1.5)

    def test_02_create_wari_route(self):
        """Test registering a new Wari Route -> WS-ROUTE-2026-000002"""
        payload = {
            "name": "Dehu–Pandharpur Route",
            "start_location": "Dehu",
            "destination": "Pandharpur",
            "total_distance": 250.0
        }
        res = self.app.post('/api/routes', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.admin_token}"
        }, content_type='application/json')

        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['route_code'].startswith('WS-ROUTE-2026-'))

    def test_03_add_route_section(self):
        """Test adding a route section to Route #1"""
        payload = {
            "sequence_number": 8,
            "start_location": "Pandharpur City",
            "end_location": "Vithoba Temple Ghat",
            "distance_km": 5.0,
            "estimated_duration": "2 Hours"
        }
        res = self.app.post('/api/routes/1/sections', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.admin_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.get_json()['success'])

    def test_04_add_wari_location(self):
        """Test registering a new medical camp facility location"""
        payload = {
            "name": "Jejuri Route First Aid Tent 2",
            "location_type": "MEDICAL_CAMP",
            "route_section_id": 3,
            "zone": "Jejuri",
            "latitude": 18.2750000,
            "longitude": 74.1590000,
            "description": "24/7 First aid medical post near Jejuri temple base",
            "contact_number": "+91 98220 55555"
        }
        res = self.app.post('/api/locations', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.admin_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.get_json()['success'])

    def test_05_get_nearby_locations(self):
        """Test nearby facilities search around Saswad (18.345, 74.032) within 5 km"""
        res = self.app.get('/api/locations/nearby?latitude=18.3450&longitude=74.0320&radius=5.0', headers={
            "Authorization": f"Bearer {self.leader_token}"
        })

        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['data']), 0)
        self.assertIn('distance_km', data['data'][0])

    def test_06_update_dindi_location(self):
        """Test updating current Dindi location via GPS/manual update"""
        payload = {
            "latitude": 18.3460000,
            "longitude": 74.0330000,
            "accuracy": 10.0,
            "location_source": "GPS",
            "status": "MOVING"
        }
        res = self.app.post('/api/dindis/1/location', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.leader_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.get_json()['success'])

    def test_07_get_dindi_location_history(self):
        """Test retrieving latest Dindi location and movement history"""
        res = self.app.get('/api/dindis/1/location', headers={
            "Authorization": f"Bearer {self.leader_token}"
        })

        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIn('latest_location', data['data'])
        self.assertIn('location_history', data['data'])

    def test_08_dindi_checkpoint_checkin(self):
        """Test Dindi leader checking in at Checkpoint 4"""
        payload = {
            "dindi_id": 1,
            "latitude": 18.3455000,
            "longitude": 74.0325000,
            "status": "PASSED"
        }
        res = self.app.post('/api/checkpoints/4/checkin', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.leader_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.get_json()['success'])

    def test_09_update_crowd_zone_status(self):
        """Test police/admin updating crowd zone congestion level to HIGH"""
        payload = {
            "crowd_level": "HIGH"
        }
        res = self.app.patch('/api/crowd-zones/1', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.admin_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 200)

    def test_10_publish_route_alert(self):
        """Test publishing a route alert"""
        payload = {
            "route_section_id": 2,
            "title": "Saswad Ghat Slow Traffic Alert",
            "message": "Heavy pilgrim movement on Saswad Dive Ghat ascent.",
            "priority": "IMPORTANT"
        }
        res = self.app.post('/api/routes/alerts', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.admin_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.get_json()['success'])

    def test_11_audit_logging_module9(self):
        """Test that Module 9 security events are captured in audit_logs"""
        logs = execute_query("SELECT * FROM audit_logs WHERE action IN ('ROUTE_CREATED', 'LOCATION_CREATED', 'DINDI_LOCATION_UPDATED', 'DINDI_CHECKED_IN', 'CROWD_STATUS_UPDATED')", fetchall=True)
        self.assertGreater(len(logs), 0)

if __name__ == '__main__':
    unittest.main()
