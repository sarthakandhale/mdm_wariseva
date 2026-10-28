"""
Candidate Filtering Subsystem for WariSeva Module 7 AI Engine.
Filters candidates before deep feature extraction to maintain maximum scalability and low latency.
"""

from db import execute_query

class CandidateFilter:

    @staticmethod
    def filter_person_candidates(lost_case):
        """
        Retrieves potential candidate found_person_cases for a given lost_person_case.
        Filters by:
        - Gender (exact match or UNKNOWN)
        - Age window (+/- 15 years tolerance)
        - Excludes already CLOSED/REUNITED cases
        """
        person_obj = lost_case.get('person', {})
        lost_age = lost_case.get('age') or person_obj.get('calculated_age') or person_obj.get('age') or lost_case.get('temp_person_age') or 30
        gender = lost_case.get('gender') or person_obj.get('gender') or lost_case.get('temp_person_gender') or 'UNKNOWN'

        min_age = max(0, int(lost_age) - 15)
        max_age = int(lost_age) + 15

        query = """
        SELECT c.*, l.zone, l.route_section, l.landmark, l.latitude, l.longitude
        FROM found_person_cases c
        LEFT JOIN found_person_locations l ON c.id = l.case_id
        WHERE c.status NOT IN ('REUNITED', 'CLOSED')
        AND (c.approximate_age BETWEEN %s AND %s OR c.approximate_age IS NULL)
        """


        params = [min_age, max_age]

        if gender and gender != 'UNKNOWN':
            query += " AND (UPPER(c.gender) = UPPER(%s) OR c.gender = 'UNKNOWN' OR c.gender IS NULL)"
            params.append(gender)


        candidates = execute_query(query, tuple(params), fetchall=True) or []
        return candidates

    @staticmethod
    def filter_item_candidates(lost_item):
        """
        Retrieves candidate found_item_cases for a given lost_item_case.
        Filters by:
        - Category (exact match)
        - Excludes CLOSED / RETURNED items
        """
        category = lost_item.get('item_category', 'OTHER')

        query = """
        SELECT c.*, l.zone, l.route_section, l.landmark, l.latitude, l.longitude
        FROM found_item_cases c
        LEFT JOIN item_locations l ON c.id = l.found_item_case_id AND l.location_type = 'FOUND'
        WHERE c.status NOT IN ('RETURNED', 'CLOSED')
        AND c.item_category = %s
        """
        candidates = execute_query(query, (category,), fetchall=True) or []
        return candidates
