"""Provider-neutral recommendation engine.

This local implementation intentionally requires no API key. Replace
`analyze_risk` with an LLM-backed implementation when desired.
"""


def analyze_risk(risk: dict) -> str:
    severity = risk["severity"]
    score = risk["adjusted_score"]
    category = risk["category"]

    if severity == "Critical":
        return f"Immediate action required: assign an accountable owner, define a mitigation plan, and review the {category} risk within 24 hours. Current adjusted score: {score}."
    if severity == "High":
        return f"Prioritize mitigation: document preventive and contingency controls, assign a deadline, and review the {category} risk weekly. Current adjusted score: {score}."
    if severity == "Medium":
        return f"Monitor and improve controls: record an owner and next review date, and address the most practical mitigation for this {category} risk. Current adjusted score: {score}."
    return f"Accept with monitoring: retain the current controls and revisit the {category} risk during the next routine review. Current adjusted score: {score}."
