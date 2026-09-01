"""Model loading and prediction helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from .explain import explain_transaction
from .features import prepare_features

MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"


def load_artifact() -> dict[str, Any]:
    if not MODEL_PATH.exists():
        from .train import train_and_evaluate

        train_and_evaluate()
    return joblib.load(MODEL_PATH)


def risk_level(score: int) -> str:
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def recommended_action(level: str) -> str:
    return "Review transaction" if level == "HIGH" else "Monitor" if level == "MEDIUM" else "Allow with monitoring"


def predict_rows(rows: list[dict[str, Any]], threshold: float = 0.70) -> list[dict[str, Any]]:
    artifact = load_artifact()
    model = artifact["model"]
    frame = pd.DataFrame(rows)
    features = prepare_features(frame)
    probabilities = model.predict_proba(features)[:, 1]
    results = []
    for row, probability in zip(rows, probabilities):
        score = max(0, min(100, int(round(float(probability) * 100))))
        # Classification remains intentionally tied to the published 0-39/40-69/70-100 product bands.
        level = risk_level(score)
        reasons, top_features = explain_transaction(row, model, float(probability))
        result = dict(row)
        result.update(
            {
                "risk_score": score,
                "risk_level": level,
                "fraud_probability": round(float(probability), 4),
                "reasons": reasons,
                "top_features": top_features,
                "recommended_action": recommended_action(level),
                "threshold_used": threshold,
                "flagged": bool(float(probability) >= threshold),
            }
        )
        results.append(result)
    return results
