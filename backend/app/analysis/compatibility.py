from typing import Dict, Any, Optional

def calculate_founder_complementarity_index(
    candidate_ocean: Dict[str, float],
    founder_ocean: Optional[Dict[str, float]] = None,
) -> float:
    """
    Computes Founder Complementarity Index (FCI: 0-100).
    Evaluates:
    - Vision Alignment: Shared baseline openness & drive
    - Execution Complementarity: Balance in conscientiousness & focus
    - Conflict Resilience: Emotional stability (100 - neuroticism)
    - Cognitive Diversity: Complementary traits rather than identical echo chamber
    """
    if not founder_ocean:
        # Default baseline founder: high openness (80), high conscientiousness (75)
        founder_ocean = {
            "ocean_openness": 80.0,
            "ocean_conscientiousness": 75.0,
            "ocean_extraversion": 65.0,
            "ocean_agreeableness": 60.0,
            "ocean_neuroticism": 35.0,
        }

    c_o = candidate_ocean.get("ocean_openness", 50.0)
    c_c = candidate_ocean.get("ocean_conscientiousness", 50.0)
    c_e = candidate_ocean.get("ocean_extraversion", 50.0)
    c_a = candidate_ocean.get("ocean_agreeableness", 50.0)
    c_n = candidate_ocean.get("ocean_neuroticism", 50.0)

    f_o = founder_ocean.get("ocean_openness", 75.0)
    f_c = founder_ocean.get("ocean_conscientiousness", 70.0)
    f_e = founder_ocean.get("ocean_extraversion", 60.0)
    f_a = founder_ocean.get("ocean_agreeableness", 60.0)
    f_n = founder_ocean.get("ocean_neuroticism", 40.0)

    # 1. Vision Alignment (Shared high openness / curiosity)
    vision_alignment = 100.0 - abs(c_o - f_o)

    # 2. Execution Complementarity (High combined conscientiousness)
    execution_power = (c_c + f_c) / 2.0

    # 3. Conflict Resilience (Low neuroticism + constructive agreeableness)
    emotional_stability = 100.0 - ((c_n + f_n) / 2.0)
    healthy_conflict = 100.0 - abs(c_a - 60.0)  # neither pushover nor toxic
    resilience = (emotional_stability * 0.6) + (healthy_conflict * 0.4)

    # 4. Cognitive Diversity (Complementary extraversion / domain roles)
    diversity = min(100.0, 50.0 + abs(c_e - f_e) * 0.8)

    # Weighted composite index
    fci = (
        (vision_alignment * 0.25)
        + (execution_power * 0.35)
        + (resilience * 0.25)
        + (diversity * 0.15)
    )

    return round(max(0.0, min(100.0, float(fci))), 1)
