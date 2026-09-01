"""Deterministic risk scoring and classification."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskAssessment:
    base_score: int
    adjusted_score: int
    severity: str
    priority: str


def assess_risk(likelihood: int, impact: int, control_effectiveness: int = 0) -> RiskAssessment:
    """Calculate adjusted score and severity for a 1-5 likelihood/impact risk."""
    if not 1 <= likelihood <= 5:
        raise ValueError("likelihood must be between 1 and 5")
    if not 1 <= impact <= 5:
        raise ValueError("impact must be between 1 and 5")
    if not 0 <= control_effectiveness <= 100:
        raise ValueError("control_effectiveness must be between 0 and 100")

    base_score = likelihood * impact
    adjusted_score = round(base_score * (1 - control_effectiveness / 100))
    adjusted_score = max(0, min(base_score, adjusted_score))

    if adjusted_score <= 4:
        level = "Low"
    elif adjusted_score <= 9:
        level = "Medium"
    elif adjusted_score <= 16:
        level = "High"
    else:
        level = "Critical"

    return RiskAssessment(base_score, adjusted_score, level, level)
