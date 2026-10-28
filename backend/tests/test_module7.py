"""
WariSeva Module 7 - Automated Test Suite
Executes unit tests for AI-Assisted Matching & Recommendation Engine against Flask REST APIs.
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import execute_query
from ai.feature_engineering import FeatureEngineering
from ai.candidate_filter import CandidateFilter
from ai.similarity_engine import SimilarityEngine
from ai.explanation_engine import ExplanationEngine

class TestModule7AIMatching(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Login as Police Officer (users.id = 4)
        login_police = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "police@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.police_token = login_police['data']['session_token']

        # Login as Parent User (users.id = 7)
        login_parent = self.app.post('/api/auth/login', data=json.dumps({
            "identifier": "parent@demo.com",
            "password": "Demo1234!"
        }), content_type='application/json').get_json()
        self.parent_token = login_parent['data']['session_token']

    def test_01_haversine_distance_calculation(self):
        """Test Haversine geographical distance calculation accuracy"""
        # Distance between Alandi (18.677, 73.897) and Pune (18.520, 73.856) ~ 17.9 km
        dist = FeatureEngineering.calculate_haversine_distance(18.677, 73.897, 18.520, 73.856)
        self.assertIsNotNone(dist)
        self.assertAlmostEqual(dist, 17.9, delta=2.0)

    def test_02_age_similarity_fuzzy_decay(self):
        """Test age similarity fuzzy decay score"""
        score_exact = FeatureEngineering.age_similarity(8, 8)
        score_close = FeatureEngineering.age_similarity(8, 10)
        score_far = FeatureEngineering.age_similarity(8, 45)

        self.assertEqual(score_exact, 1.0)
        self.assertEqual(score_close, 0.95)
        self.assertEqual(score_far, 0.0)

    def test_03_trigger_person_matching_pipeline_a(self):
        """Test executing Pipeline A: Lost Person ↔ Found Person"""
        res = self.app.post('/api/ai/match/person/1', headers={
            "Authorization": f"Bearer {self.police_token}"
        })
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['data']), 1)

    def test_04_get_person_matches(self):
        """Test retrieving generated person candidate matches"""
        res = self.app.get('/api/ai/matches/person/1', headers={
            "Authorization": f"Bearer {self.police_token}"
        })
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_05_trigger_item_matching_pipeline_b(self):
        """Test executing Pipeline B: Lost Item ↔ Found Item"""
        res = self.app.post('/api/ai/match/item/1', headers={
            "Authorization": f"Bearer {self.police_token}"
        })
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['data']), 1)

    def test_06_get_match_side_by_side_details(self):
        """Test retrieving side-by-side comparison details for an AI match"""
        res = self.app.get('/api/ai/matches/1', headers={
            "Authorization": f"Bearer {self.police_token}"
        })
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['data']['id'], 1)
        self.assertIn('source_case', data['data'])
        self.assertIn('candidate_case', data['data'])

    def test_07_human_review_accept_for_verification(self):
        """Test human operator accepting recommendation for verification"""
        payload = {
            "decision": "ACCEPTED_FOR_VERIFICATION",
            "notes": "Verified strong clothing and location match."
        }
        res = self.app.patch('/api/ai/matches/1/review', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.police_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 200)
        rec = execute_query("SELECT status FROM ai_match_results WHERE id = 1", fetchone=True)
        self.assertEqual(rec['status'], 'ACCEPTED_FOR_VERIFICATION')

    def test_08_prohibit_automatic_identity_confirmation(self):
        """Test API prohibits setting CONFIRMED_IDENTITY directly from AI review"""
        payload = {
            "decision": "CONFIRMED_IDENTITY"
        }
        res = self.app.patch('/api/ai/matches/1/review', data=json.dumps(payload), headers={
            "Authorization": f"Bearer {self.police_token}"
        }, content_type='application/json')

        self.assertEqual(res.status_code, 400)

    def test_09_ai_dashboard_metrics(self):
        """Test AI Dashboard metrics endpoint"""
        res = self.app.get('/api/ai/dashboard', headers={
            "Authorization": f"Bearer {self.police_token}"
        })
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIn('total_matches', data['data']['metrics'])

    def test_10_model_evaluation_metrics(self):
        """Test model evaluation endpoint (Precision, Recall, F1, Confusion Matrix)"""
        res = self.app.get('/api/ai/evaluation', headers={
            "Authorization": f"Bearer {self.police_token}"
        })
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIn('precision', data['data'])
        self.assertIn('confusion_matrix', data['data'])

    def test_11_audit_logging_module7(self):
        """Test that Module 7 security events are captured in audit_logs"""
        logs = execute_query("SELECT * FROM audit_logs WHERE action IN ('AI_MATCH_REQUESTED', 'AI_MATCH_GENERATED', 'AI_MATCH_ACCEPTED')", fetchall=True)
        self.assertGreater(len(logs), 0)

if __name__ == '__main__':
    unittest.main()
