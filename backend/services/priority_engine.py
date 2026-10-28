"""
WariSeva Rule-Based Medical Priority Calculation Engine
Determines priority score, priority level, and reasoning breakdown for emergency cases.
"""

def calculate_medical_priority(emergency_type, symptoms=[], age=None, is_child=False, is_elderly=False, medical_history=None, location_zone=None, is_unconscious=False):
    score = 0
    reasons = []

    type_upper = (emergency_type or '').upper()
    symptoms_upper = [s.upper() for s in symptoms]

    # 1. Unconsciousness / Critical Signs (+40)
    if is_unconscious or type_upper == 'FAINTING' or any('UNCONSCIOUS' in s for s in symptoms_upper):
        score += 40
        reasons.append("Unconsciousness / Patient Fainted (+40)")

    # 2. Breathing difficulty / Chest pain (+35)
    if type_upper in ['BREATHING_DIFFICULTY', 'CHEST_PAIN'] or any(s in ['CHEST PAIN', 'DIFFICULTY BREATHING', 'SHORTNESS OF BREATH'] for s in symptoms_upper):
        score += 35
        reasons.append("Breathing difficulty or chest pain (+35)")

    # 3. Severe Bleeding / Accident / Fracture (+35)
    if type_upper in ['ACCIDENT', 'INJURY', 'FRACTURE'] or any(s in ['BLEEDING', 'SEVERE PAIN', 'FRACTURE'] for s in symptoms_upper):
        score += 35
        reasons.append("Accident / Fracture / Severe Bleeding (+35)")

    # 4. Dehydration / Heat Exhaustion / Allergic Reaction (+20)
    if type_upper in ['DEHYDRATION', 'HEAT_EXHAUSTION', 'ALLERGIC_REACTION']:
        score += 20
        reasons.append(f"{type_upper.replace('_', ' ').title()} emergency (+20)")

    # 5. Age Risk Factors (+15)
    if is_child or (age is not None and age <= 12):
        score += 15
        reasons.append("Child patient under 12 (+15)")
    elif is_elderly or (age is not None and age >= 60):
        score += 15
        reasons.append("Elderly patient 60+ (+15)")

    # 6. Known serious medical history (+20)
    if medical_history and any(term in str(medical_history).lower() for term in ['asthma', 'heart', 'hypertension', 'diabetes', 'allergy']):
        score += 20
        reasons.append("Known serious medical condition (+20)")

    # 7. High-risk route zone (+10)
    high_risk_zones = ['ALANDI', 'SASWAD', 'JEJURI', 'LONAND', 'PANDHARPUR']
    if location_zone and location_zone.upper() in high_risk_zones:
        score += 10
        reasons.append(f"High-density route zone ({location_zone}) (+10)")

    # Assign Priority Level
    if score >= 75:
        level = 'CRITICAL'
    elif score >= 50:
        level = 'HIGH'
    elif score >= 25:
        level = 'MEDIUM'
    else:
        level = 'LOW'

    reasons_str = " | ".join(reasons) if reasons else "Standard medical evaluation"
    return score, level, reasons_str
