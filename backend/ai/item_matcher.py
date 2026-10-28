"""
Item Matcher Subsystem for WariSeva Module 7 AI Engine.
Pipeline B: Compares Lost Item Cases against Candidate Found Item Cases.
"""

import json
import uuid
from db import execute_query
from services.item_service import get_lost_item_details, get_found_item_details
from ai.candidate_filter import CandidateFilter
from ai.similarity_engine import SimilarityEngine
from ai.explanation_engine import ExplanationEngine

class ItemMatcher:

    @staticmethod
    def match_lost_item(lost_item_id, min_score_threshold=40):
        """
        Executes Pipeline B for a lost item case.
        Retrieves candidate item cases, calculates match scores, generates explanations,
        and saves recommendations into `ai_match_results`.
        """
        lost_item = get_lost_item_details(lost_item_id)
        if not lost_item:
            return False, "Lost item case not found.", []

        candidates = CandidateFilter.filter_item_candidates(lost_item)
        generated_matches = []

        for candidate in candidates:
            cand_id = candidate['id']
            found_item = get_found_item_details(cand_id)
            if not found_item:
                continue

            match_score, confidence, data_quality, factors = SimilarityEngine.calculate_item_match(lost_item, found_item)

            if match_score >= min_score_threshold:
                exp_payload = ExplanationEngine.generate_item_explanation(factors, lost_item, found_item)
                explanation_json = json.dumps(exp_payload)

                # Check if recommendation already exists
                existing = execute_query("""
                SELECT id FROM ai_match_results
                WHERE match_type = 'ITEM' AND source_case_id = %s AND candidate_case_id = %s
                """, (lost_item_id, cand_id), fetchone=True)

                if existing:
                    execute_query("""
                    UPDATE ai_match_results
                    SET match_score = %s, confidence_score = %s, data_quality_score = %s, explanation = %s, updated_at = NOW()
                    WHERE id = %s
                    """, (match_score, confidence, data_quality, explanation_json, existing['id']), commit=True)
                    match_id = existing['id']
                else:
                    match_uuid = f"aim-{uuid.uuid4().hex[:12]}"
                    match_id = execute_query("""
                    INSERT INTO ai_match_results (
                        uuid, match_type, source_case_id, candidate_case_id,
                        match_score, confidence_score, data_quality_score, explanation, model_version, status
                    ) VALUES (%s, 'ITEM', %s, %s, %s, %s, %s, %s, 'v1.0-Hybrid', 'GENERATED')
                    """, (match_uuid, lost_item_id, cand_id, match_score, confidence, data_quality, explanation_json), commit=True)

                generated_matches.append({
                    "match_id": match_id,
                    "candidate_case_id": cand_id,
                    "candidate_case_number": candidate['case_number'],
                    "found_item_name": candidate['item_name'],
                    "match_score": match_score,
                    "confidence_score": confidence,
                    "data_quality_score": data_quality,
                    "explanation": exp_payload
                })

        generated_matches.sort(key=lambda x: x['match_score'], reverse=True)
        return True, "Item matching pipeline completed.", generated_matches
