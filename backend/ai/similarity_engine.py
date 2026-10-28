"""
Similarity Engine Subsystem for WariSeva Module 7 AI Engine.
Implements configurable weighted feature vector matching and data quality scoring.
"""

from ai.feature_engineering import FeatureEngineering

# Configurable Weights for Person Pipeline (Total = 1.0)
PERSON_WEIGHTS = {
    'age': 0.15,
    'gender': 0.05,
    'clothing': 0.20,
    'physical': 0.15,
    'location': 0.15,
    'time': 0.10,
    'dindi': 0.10,
    'language': 0.05,
    'image': 0.05
}

# Configurable Weights for Item Pipeline (Total = 1.0)
ITEM_WEIGHTS = {
    'category': 0.15,
    'brand': 0.15,
    'model': 0.20,
    'color': 0.10,
    'description': 0.15,
    'location': 0.10,
    'time': 0.05,
    'image': 0.10
}

class SimilarityEngine:

    @staticmethod
    def calculate_person_match(lost_case, found_case):
        """
        Calculates weighted similarity score, data quality score, confidence score,
        and contributing factor breakdown for Person Matching (Pipeline A).
        """
        factors = {}
        data_fields_present = 0
        total_data_fields = 7

        l_person = lost_case.get('person', {})
        f_person = found_case.get('person', {})
        l_cloth_dict = lost_case.get('clothing', {})
        f_cloth_dict = found_case.get('clothing', {})

        # 1. Age Similarity (15%)
        l_age = lost_case.get('age') or l_person.get('calculated_age') or l_person.get('age') or lost_case.get('temp_person_age')
        f_age = found_case.get('estimated_age') or found_case.get('approximate_age') or f_person.get('calculated_age') or f_person.get('age')
        if l_age is not None and f_age is not None:
            factors['age'] = int(FeatureEngineering.age_similarity(l_age, f_age) * 100)
            data_fields_present += 1
        else:
            factors['age'] = 50

        # 2. Gender Match (5%)
        l_gen = lost_case.get('gender') or l_person.get('gender') or lost_case.get('temp_person_gender')
        f_gen = found_case.get('gender') or f_person.get('gender')
        if l_gen and f_gen:
            factors['gender'] = 100 if (str(l_gen).upper() == str(f_gen).upper() or l_gen == 'UNKNOWN' or f_gen == 'UNKNOWN') else 0
            data_fields_present += 1
        else:
            factors['gender'] = 50

        # 3. Clothing Similarity (20%)
        l_top = l_cloth_dict.get('top_color', '') or lost_case.get('top_wear_color', '')
        l_top_t = l_cloth_dict.get('top_type', '') or lost_case.get('top_wear_type', '')
        l_bot = l_cloth_dict.get('bottom_color', '') or lost_case.get('bottom_wear_color', '')
        l_bot_t = l_cloth_dict.get('bottom_type', '') or lost_case.get('bottom_wear_type', '')
        
        f_top = f_cloth_dict.get('top_color', '') or found_case.get('top_wear_color', '')
        f_top_t = f_cloth_dict.get('top_type', '') or found_case.get('top_wear_type', '')
        f_bot = f_cloth_dict.get('bottom_color', '') or found_case.get('bottom_wear_color', '')
        f_bot_t = f_cloth_dict.get('bottom_type', '') or found_case.get('bottom_wear_type', '')

        l_cloth_str = f"{l_top} {l_top_t} {l_bot} {l_bot_t}".strip()
        f_cloth_str = f"{f_top} {f_top_t} {f_bot} {f_bot_t}".strip()
        if l_cloth_str or f_cloth_str:
            factors['clothing'] = int(FeatureEngineering.text_token_similarity(l_cloth_str, f_cloth_str) * 100)
            data_fields_present += 1
        else:
            factors['clothing'] = 50

        # 4. Physical Description / Height / Marks (15%)
        l_phys = f"{l_person.get('height_cm', '')} {l_person.get('build_type', '')} {l_person.get('distinguishing_marks', '')}".strip()
        f_phys = f"{found_case.get('estimated_height_cm', '')} {found_case.get('build_type', '')} {found_case.get('distinguishing_marks', '')}".strip()
        if l_phys or f_phys:
            factors['physical'] = int(FeatureEngineering.text_token_similarity(l_phys, f_phys) * 100)
            data_fields_present += 1
        else:
            factors['physical'] = 50

            factors['physical'] = 50

        # 5. Location Distance Similarity (15%)
        l_loc = lost_case.get('location', {})
        f_loc = found_case.get('location', {})
        dist = FeatureEngineering.calculate_haversine_distance(
            l_loc.get('latitude'), l_loc.get('longitude'),
            f_loc.get('latitude'), f_loc.get('longitude')
        )
        if dist is not None:
            factors['location'] = int(FeatureEngineering.haversine_similarity(dist) * 100)
            data_fields_present += 1
        else:
            factors['location'] = 50

        # 6. Timestamp Similarity (10%)
        l_time = lost_case.get('last_seen_at')
        f_time = found_case.get('found_at')
        if l_time and f_time:
            factors['time'] = int(FeatureEngineering.time_decay_similarity(l_time, f_time) * 100)
            data_fields_present += 1
        else:
            factors['time'] = 50

        # 7. Dindi Match (10%)
        l_dindi = lost_case.get('dindi_id')
        f_dindi = found_case.get('dindi_id')
        if l_dindi and f_dindi:
            factors['dindi'] = 100 if l_dindi == f_dindi else 20
            data_fields_present += 1
        else:
            factors['dindi'] = 50

        # 8. Language & Image (10% total)
        factors['language'] = 50
        factors['image'] = 85 if (lost_case.get('photos') and found_case.get('photos')) else 50

        # Weighted Sum Calculation
        match_score = int(sum(factors[k] * PERSON_WEIGHTS[k] for k in PERSON_WEIGHTS))
        data_quality_score = int((data_fields_present / float(total_data_fields)) * 100)
        confidence_score = int(match_score * (0.6 + 0.4 * (data_quality_score / 100.0)))

        return match_score, confidence_score, data_quality_score, factors

    @staticmethod
    def calculate_item_match(lost_item, found_item):
        """
        Calculates weighted similarity score, data quality score, confidence score,
        and contributing factor breakdown for Item Matching (Pipeline B).
        """
        factors = {}
        data_fields_present = 0
        total_data_fields = 6

        # 1. Category (15%)
        l_cat = lost_item.get('item_category')
        f_cat = found_item.get('item_category')
        factors['category'] = 100 if (l_cat and f_cat and l_cat == f_cat) else 0
        if l_cat and f_cat:
            data_fields_present += 1

        # 2. Brand (15%)
        l_brand = (lost_item.get('brand') or '').lower()
        f_brand = (found_item.get('brand') or '').lower()
        if l_brand and f_brand:
            factors['brand'] = 100 if l_brand == f_brand else int(FeatureEngineering.text_token_similarity(l_brand, f_brand) * 100)
            data_fields_present += 1
        else:
            factors['brand'] = 50

        # 3. Model (20%)
        l_model = (lost_item.get('model') or '').lower()
        f_model = (found_item.get('model') or '').lower()
        if l_model and f_model:
            factors['model'] = 100 if l_model == f_model else int(FeatureEngineering.text_token_similarity(l_model, f_model) * 100)
            data_fields_present += 1
        else:
            factors['model'] = 50

        # 4. Color (10%)
        l_col = (lost_item.get('color') or '').lower()
        f_col = (found_item.get('color') or '').lower()
        if l_col and f_col:
            factors['color'] = 100 if l_col == f_col else (50 if l_col in f_col or f_col in l_col else 0)
            data_fields_present += 1
        else:
            factors['color'] = 50

        # 5. Description (15%)
        l_desc = lost_item.get('description', '')
        f_desc = found_item.get('description', '')
        if l_desc or f_desc:
            factors['description'] = int(FeatureEngineering.text_token_similarity(l_desc, f_desc) * 100)
            data_fields_present += 1
        else:
            factors['description'] = 50

        # 6. Location Distance (10%)
        l_loc = lost_item.get('location', {})
        f_loc = found_item.get('location', {})
        dist = FeatureEngineering.calculate_haversine_distance(
            l_loc.get('latitude'), l_loc.get('longitude'),
            f_loc.get('latitude'), f_loc.get('longitude')
        )
        if dist is not None:
            factors['location'] = int(FeatureEngineering.haversine_similarity(dist) * 100)
            data_fields_present += 1
        else:
            factors['location'] = 50

        # 7. Time & Image (15% total)
        factors['time'] = 75
        factors['image'] = 80 if (lost_item.get('photos') and found_item.get('photos')) else 50

        # Weighted Sum Calculation
        match_score = int(sum(factors[k] * ITEM_WEIGHTS[k] for k in ITEM_WEIGHTS))
        data_quality_score = int((data_fields_present / float(total_data_fields)) * 100)
        confidence_score = int(match_score * (0.6 + 0.4 * (data_quality_score / 100.0)))

        return match_score, confidence_score, data_quality_score, factors
