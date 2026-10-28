"""
Person Matcher Subsystem for WariSeva Module 7 AI Engine.
Pipeline A: Compares Lost Person Cases against Candidate Found Person Cases.
"""

import json
import uuid
from db import execute_query
from services.lost_person_service import get_lost_person_case_details
from services.found_person_service import get_found_person_case_details
from ai.candidate_filter import CandidateFilter
from ai.similarity_engine import SimilarityEngine
from ai.explanation_engine import ExplanationEngine

class PersonMatcher:

    @staticmethod
    def match_lost_person(lost_case_id, min_score_threshold=40):
        """
        Executes Pipeline A for a lost person case.
        Retrieves candidate cases, calculates match scores, generates explanations,
        and saves ranked recommendations into `ai_match_results`.
        """
        lost_case = get_lost_person_case_details(lost_case_id)
        if not lost_case:
            return False, "Lost person case not found.", []

        candidates = CandidateFilter.filter_person_candidates(lost_case)
        generated_matches = []

        for candidate in candidates:
            cand_id = candidate['id']
            found_case = get_found_person_case_details(cand_id)
            if not found_case:
                continue

            match_score, confidence, data_quality, factors = SimilarityEngine.calculate_person_match(lost_case, found_case)

            if match_score >= min_score_threshold:
                exp_payload = ExplanationEngine.generate_person_explanation(factors, lost_case, found_case)
                explanation_json = json.dumps(exp_payload)

                # Check if recommendation already exists
                existing = execute_query("""
                SELECT id FROM ai_match_results
                WHERE match_type = 'PERSON' AND source_case_id = %s AND candidate_case_id = %s
                """, (lost_case_id, cand_id), fetchone=True)

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
                    ) VALUES (%s, 'PERSON', %s, %s, %s, %s, %s, %s, 'v1.0-Hybrid', 'GENERATED')
                    """, (match_uuid, lost_case_id, cand_id, match_score, confidence, data_quality, explanation_json), commit=True)

                generated_matches.append({
                    "match_id": match_id,
                    "candidate_case_id": cand_id,
                    "candidate_case_number": candidate['case_number'],
                    "found_person_name": candidate.get('full_name', 'Unidentified Person'),
                    "match_score": match_score,
                    "confidence_score": confidence,
                    "data_quality_score": data_quality,
                    "explanation": exp_payload
                })

        # Sort matches by match_score DESC
        generated_matches.sort(key=lambda x: x['match_score'], reverse=True)
        return True, "Person matching pipeline completed.", generated_matches
