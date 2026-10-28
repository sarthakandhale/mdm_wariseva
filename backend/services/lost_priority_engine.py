"""
WariSeva Rule-Based Missing Person Priority Calculation Engine
Determines priority score, level, and reasons for lost person cases.
"""

def calculate_lost_person_priority(age=None, is_child=False, is_elderly=False, medical_requirement=False, cognitive_assistance=False, communication_difficulty=False, last_seen_hour=14, zone=None, duration_hours=0):
    score = 0
    reasons = []

    # 1. Age Vulnerability
    if is_child or (age is not None and age <= 12):
        score += 30
        reasons.append("Child under 12 (+30)")
    elif is_elderly or (age is not None and age >= 60):
        score += 25
        reasons.append("Elderly person 60+ (+25)")

    # 2. Medical Requirement (+25)
    if medical_requirement:
        score += 25
        reasons.append("Urgent medical requirement / condition (+25)")

    # 3. Cognitive Assistance Required (+25)
    if cognitive_assistance:
        score += 25
        reasons.append("Cognitive assistance required / Memory loss (+25)")

    # 4. Communication Difficulty (+20)
    if communication_difficulty:
        score += 20
        reasons.append("Communication difficulty / Non-verbal (+20)")

    # 5. Night-time Disappearance (+10)
    if last_seen_hour is not None and (last_seen_hour >= 20 or last_seen_hour < 6):
        score += 10
        reasons.append("Night-time disappearance (+10)")

    # 6. High-density route zone (+10)
    high_risk_zones = ['ALANDI', 'SASWAD', 'JEJURI', 'LONAND', 'PANDHARPUR']
    if zone and zone.upper() in high_risk_zones:
        score += 10
        reasons.append(f"High-density route zone ({zone}) (+10)")

    # 7. Long duration missing (>2 hours) (+10)
    if duration_hours and duration_hours >= 2:
        score += 10
        reasons.append("Missing for over 2 hours (+10)")

    # Assign Priority Level
    if score >= 75:
        level = 'CRITICAL'
    elif score >= 50:
        level = 'HIGH'
    elif score >= 25:
        level = 'MEDIUM'
    else:
        level = 'LOW'

    reasons_str = " | ".join(reasons) if reasons else "Standard missing person evaluation"
    return score, level, reasons_str
