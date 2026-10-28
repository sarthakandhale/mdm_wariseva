"""
Feature Engineering & Normalization Subsystem for WariSeva Module 7 AI Engine.
Includes Haversine geographical distance calculation, age decay, timestamp decay, text overlap, and clothing vector comparison.
"""

import math
from datetime import datetime

class FeatureEngineering:

    @staticmethod
    def calculate_haversine_distance(lat1, lon1, lat2, lon2):
        """Calculates distance in kilometers between two GPS coordinates"""
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return None

        R = 6371.0 # Radius of earth in km
        dlat = math.radians(float(lat2) - float(lat1))
        dlon = math.radians(float(lon2) - float(lon1))
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def haversine_similarity(dist_km):
        """Converts distance in km to similarity score (0.0 to 1.0)"""
        if dist_km is None:
            return 0.5 # Neutral fallback if coordinates missing
        if dist_km <= 0.5:
            return 1.0
        elif dist_km <= 2.0:
            return 0.9
        elif dist_km <= 5.0:
            return 0.75
        elif dist_km <= 15.0:
            return 0.5
        elif dist_km <= 50.0:
            return 0.2
        return 0.05

    @staticmethod
    def age_similarity(age1, age2):
        """Calculates age similarity using fuzzy tolerance decay"""
        if age1 is None or age2 is None:
            return 0.5
        diff = abs(int(age1) - int(age2))
        if diff == 0:
            return 1.0
        elif diff <= 2:
            return 0.95
        elif diff <= 5:
            return 0.8
        elif diff <= 10:
            return 0.5
        elif diff <= 20:
            return 0.2
        return 0.0

    @staticmethod
    def time_decay_similarity(dt1, dt2):
        """Calculates time decay similarity score based on elapsed hours"""
        if not dt1 or not dt2:
            return 0.5
        try:
            if isinstance(dt1, str):
                dt1 = datetime.strptime(dt1[:19].replace('T', ' '), "%Y-%m-%d %H:%M:%S")
            if isinstance(dt2, str):
                dt2 = datetime.strptime(dt2[:19].replace('T', ' '), "%Y-%m-%d %H:%M:%S")
            hours = abs((dt1 - dt2).total_seconds()) / 3600.0
            if hours <= 1.0:
                return 1.0
            elif hours <= 4.0:
                return 0.9
            elif hours <= 12.0:
                return 0.75
            elif hours <= 24.0:
                return 0.5
            elif hours <= 72.0:
                return 0.25
            return 0.1
        except Exception:
            return 0.5

    @staticmethod
    def text_token_similarity(s1, s2):
        """Calculates token overlap Jaccard similarity between two text strings"""
        if not s1 or not s2:
            return 0.5
        tokens1 = set(str(s1).lower().replace(',', ' ').split())
        tokens2 = set(str(s2).lower().replace(',', ' ').split())
        if not tokens1 or not tokens2:
            return 0.5
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        return len(intersection) / float(len(union))
