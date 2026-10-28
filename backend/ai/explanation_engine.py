"""
Explanation Engine Subsystem for WariSeva Module 7 AI Engine.
Generates human-readable explanations and contributing component factor scores for operators.
"""

class ExplanationEngine:

    @staticmethod
    def generate_person_explanation(factors, lost_case, found_case):
        """Generates bullet points explaining person match score"""
        reasons = []
        
        # Age
        if factors.get('age', 0) >= 80:
            reasons.append(f"✓ Similar estimated age ({lost_case.get('age', 'N/A')} vs {found_case.get('estimated_age', 'N/A')} years)")
        
        # Gender
        if factors.get('gender', 0) == 100:
            reasons.append(f"✓ Matching gender ({lost_case.get('gender', 'N/A')})")
        elif factors.get('gender', 0) == 50:
            reasons.append("⚠️ Gender unspecified on one case")

        # Clothing
        if factors.get('clothing', 0) >= 70:
            reasons.append("✓ Matching clothing & attire description")
        
        # Physical
        if factors.get('physical', 0) >= 70:
            reasons.append("✓ Matching physical attributes / height description")

        # Location
        if factors.get('location', 0) >= 75:
            reasons.append("✓ Nearby last-seen and found locations on Dindi route")

        # Time
        if factors.get('time', 0) >= 75:
            reasons.append("✓ Close timeframe between last seen and found timestamps")

        # Dindi
        if factors.get('dindi', 0) == 100:
            reasons.append(f"✓ Same Dindi group membership")

        if not reasons:
            reasons.append("• Moderate cumulative signal across multiple attributes")

        return {
            "reasons": reasons,
            "factors": factors
        }

    @staticmethod
    def generate_item_explanation(factors, lost_item, found_item):
        """Generates bullet points explaining item match score"""
        reasons = []

        if factors.get('category', 0) == 100:
            reasons.append(f"✓ Same item category ({lost_item.get('item_category')})")

        if factors.get('brand', 0) >= 80:
            reasons.append(f"✓ Matching brand & model ({lost_item.get('brand', '')} {lost_item.get('model', '')})")

        if factors.get('color', 0) >= 80:
            reasons.append(f"✓ Matching item color ({lost_item.get('color', 'N/A')})")

        if factors.get('description', 0) >= 70:
            reasons.append("✓ High similarity in item description & features")

        if factors.get('location', 0) >= 75:
            reasons.append("✓ Nearby lost and found locations")

        if not reasons:
            reasons.append("• Moderate cumulative similarity across item attributes")

        return {
            "reasons": reasons,
            "factors": factors
        }
