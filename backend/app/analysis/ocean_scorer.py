from typing import Dict, List, Any

def calculate_ocean_scores(
    raw_scores: Dict[str, float]
) -> Dict[str, float]:
    """
    Validates and bounds OCEAN Big Five personality dimensions to [0.0, 100.0].
    """
    dimensions = [
        "ocean_openness",
        "ocean_conscientiousness",
        "ocean_extraversion",
        "ocean_agreeableness",
        "ocean_neuroticism",
    ]
    normalized = {}
    for dim in dimensions:
        val = raw_scores.get(dim, 50.0)
        normalized[dim] = max(0.0, min(100.0, float(val)))
    return normalized
