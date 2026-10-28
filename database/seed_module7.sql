-- ====================================================================
-- WariSeva Platform - Module 7: Seed Data
-- Case Study: Alandi–Pandharpur Dindi Wari, Maharashtra
-- ====================================================================

USE reuniteai;

-- --------------------------------------------------------------------
-- 1. SEED AI MATCH RESULTS
-- --------------------------------------------------------------------
INSERT INTO ai_match_results (
    id, uuid, match_type, source_case_id, candidate_case_id, match_score, confidence_score, data_quality_score, explanation, model_version, status
) VALUES
(1, 'aim-001', 'PERSON', 1, 1, 92, 88, 90, '{"reasons": ["✓ Similar estimated age (8 vs 8 years)", "✓ Same gender (Male)", "✓ Matching clothing (Red T-shirt & Navy shorts)", "✓ Nearby location (Saswad route halt)", "✓ Timestamp within 1 hour"], "factors": {"age": 95, "clothing": 95, "location": 90, "time": 90}}', 'v1.0-Hybrid', 'GENERATED'),
(2, 'aim-002', 'ITEM', 1, 1, 94, 90, 85, '{"reasons": ["✓ Same category (Mobile Phone)", "✓ Matching brand & series (Samsung Galaxy)", "✓ Matching color (Black)", "✓ Matching cover (Blue silicon)", "✓ Nearby lost & found spot (Saswad Water Dispenser 3)"], "factors": {"category": 100, "brand": 95, "color": 100, "location": 90}}', 'v1.0-Hybrid', 'GENERATED');
