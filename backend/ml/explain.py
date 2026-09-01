"""Human-readable, feature-importance based explanations."""

from __future__ import annotations

from typing import Any

REASON_MAP = {
    "amount": "Transaction amount is materially above the normal demo transaction range.",
    "amount_deviation": "Transaction amount is significantly above the customer's normal behavior.",
    "transactions_last_10m": "Unusually high transaction velocity detected in the last 10 minutes.",
    "transactions_last_1h": "Transaction activity is unusually high over the last hour.",
    "failed_payments": "Multiple recent payment failures detected.",
    "is_new_device": "Transaction originated from a new device.",
    "is_new_location": "Transaction originated from a new location.",
    "distance_from_previous_location": "Location differs materially from the previous transaction.",
    "device_transaction_count": "This device is associated with an unusual number of transactions.",
    "ip_transaction_count": "This IP address is associated with an unusual number of transactions.",
    "account_age_days": "Customer account is relatively new.",
    "customer_transaction_count": "Customer transaction history is atypical for this payment pattern.",
}


def raw_importance(model_pipeline: Any) -> dict[str, float]:
    preprocessor = model_pipeline.named_steps["preprocessor"]
    estimator = model_pipeline.named_steps["model"]
    names = preprocessor.get_feature_names_out()
    values = getattr(estimator, "feature_importances_", None)
    if values is None:
        values = (abs(estimator.coef_[0]) if hasattr(estimator, "coef_") else [0.0] * len(names))
    aggregate: dict[str, float] = {}
    for name, value in zip(names, values):
        raw_name = name.split("__", 1)[-1]
        raw_name = raw_name.split("_", 1)[0] if raw_name.startswith("country_") or raw_name.startswith("payment_method_") else raw_name
        aggregate[raw_name] = aggregate.get(raw_name, 0.0) + float(abs(value))
    return aggregate


def explain_transaction(row: dict[str, Any], model_pipeline: Any, probability: float) -> tuple[list[str], list[dict[str, Any]]]:
    importance = raw_importance(model_pipeline)
    candidate_scores: list[tuple[str, float, float]] = []
    checks = {
        "amount_deviation": max(float(row.get("amount_deviation", 0)) - 1.6, 0),
        "transactions_last_10m": max(float(row.get("transactions_last_10m", 0)) - 3, 0),
        "failed_payments": float(row.get("failed_payments", 0)),
        "is_new_device": float(row.get("is_new_device", 0)),
        "is_new_location": float(row.get("is_new_location", 0)),
        "distance_from_previous_location": max(float(row.get("distance_from_previous_location", 0)) - 500, 0) / 500,
        "device_transaction_count": max(float(row.get("device_transaction_count", 0)) - 8, 0),
        "ip_transaction_count": max(float(row.get("ip_transaction_count", 0)) - 6, 0),
        "transactions_last_1h": max(float(row.get("transactions_last_1h", 0)) - 12, 0),
        "account_age_days": max(30 - float(row.get("account_age_days", 0)), 0) / 30,
    }
    for feature, magnitude in checks.items():
        if magnitude > 0:
            candidate_scores.append((feature, magnitude * importance.get(feature, 0.01), magnitude))

    candidate_scores.sort(key=lambda item: item[1], reverse=True)
    top = candidate_scores[:4]
    if not top:
        top = [("amount", 0.01, float(row.get("amount", 0)))]

    reasons = [REASON_MAP.get(feature, feature.replace("_", " ").title()) for feature, _, _ in top]
    features = [{"feature": feature, "importance": round(importance.get(feature, 0.0), 4), "signal": round(magnitude, 3), "direction": "increases risk"} for feature, _, magnitude in top]
    if probability >= 0.7 and len(reasons) < 2:
        reasons.append("Multiple transaction signals combine into an elevated fraud probability.")
    return reasons[:4], features[:4]
