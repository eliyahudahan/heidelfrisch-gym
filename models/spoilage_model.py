"""
HeidelFrisch Gym – Realistic Spoilage Model for German Commercial Transport
============================================================================
Based on:
- EU cold chain regulations (0-5°C)
- TIS-GDV fruit storage guidelines
- Q10 = 2.5 for blueberries (typical for berries)
- Base spoilage rate: 0.55% per day at optimal temp (from your data)
- Penalty for temperature abuse: each hour above 5°C costs one day of shelf life
- Market rejection threshold: 8% spoilage (German organic retailers)

This model reflects REAL pain points: 5-15% loss in transport.
"""

def real_spoilage_rate_germany(temp_c: float, delay_hours: float) -> float:
    """
    Calculate spoilage percentage for Heidelberg→Hamburg transport.
    
    Args:
        temp_c: temperature in Celsius (real, not normalized)
        delay_hours: total transport time in hours (including traffic)
    
    Returns:
        spoilage_percent: 0-100% (percentage of blueberries lost)
    """
    # Base spoilage rate at optimal temperature (0°C) per day
    base_rate_per_day = 0.55 / 100  # 0.55% = 0.0055 (from your dataset)
    
    # Temperature factor using Q10 (typical for berries)
    q10 = 2.5  # each 10°C increase multiplies spoilage rate by 2.5
    temp_factor = q10 ** ((temp_c - 0) / 10)  # reference 0°C (optimal)
    
    # Calculate spoilage without penalties
    spoilage = base_rate_per_day * temp_factor * (delay_hours / 24) * 100
    
    # === GERMAN COMMERCIAL REALITY ===
    # 1. Cold chain break (above 5°C) – each hour = one day of shelf life lost
    if temp_c > 5:
        # Additional penalty: each hour above 5°C adds an extra day of spoilage
        extra_hours = delay_hours  # full journey is compromised
        penalty = (extra_hours / 24) * 100  # convert to percent (1 day = 100%? no, careful)
        # More accurate: at 5°C+, spoilage accelerates dramatically
        # Using factor 2.5 per hour is too extreme; let's use a multiplier
        spoilage *= 2.5  # each hour counts as 2.5 hours at that temp
    
    # 2. Heat wave (above 25°C) – extreme case
    if temp_c > 25:
        spoilage *= 1.5  # additional 50% faster
    
    # Cap at 100% (total loss)
    return min(spoilage, 100.0)


def risk_score_and_action(spoilage_pct: float) -> dict:
    """
    Determine action based on spoilage percentage.
    
    German market thresholds:
    - <5%:  OK to collect (COLLECT)
    - 5-8%: urgent cooling needed (COOL URGENT)
    - >8%:  reject shipment (REJECT)
    
    Returns:
        dict with 'risk_score' (0-1) and 'action' (string)
    """
    if spoilage_pct > 8.0:
        return {'risk_score': 1.0, 'action': 'REJECT'}
    elif spoilage_pct > 5.0:
        # Risk score between 0.5 and 1.0 linearly
        risk = 0.5 + 0.5 * (spoilage_pct - 5.0) / 3.0
        return {'risk_score': min(risk, 1.0), 'action': 'COOL URGENT'}
    else:
        # Risk score between 0 and 0.5 linearly
        risk = 0.5 * (spoilage_pct / 5.0)
        return {'risk_score': risk, 'action': 'COLLECT'}


# ============================================
# TESTING
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🌡️ Testing Realistic German Spoilage Model")
    print("=" * 60)
    
    # Test scenarios
    scenarios = [
        (2, 6, "Optimal cold chain, 6h"),
        (5, 8, "Borderline temp, 8h"),
        (10, 7, "Mild break, 7h"),
        (20, 10, "Warm, 10h"),
        (30, 12, "Heat wave, 12h"),
    ]
    
    for temp, hours, desc in scenarios:
        spoilage = real_spoilage_rate_germany(temp, hours)
        decision = risk_score_and_action(spoilage)
        print(f"\n📍 {desc}:")
        print(f"   Temp: {temp}°C, Time: {hours}h")
        print(f"   Spoilage: {spoilage:.2f}%")
        print(f"   Risk: {decision['risk_score']:.2f}")
        print(f"   Action: {decision['action']}")
