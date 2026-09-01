"""Model metrics and dashboard aggregates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from ..ml.evaluate import classification_metrics
from ..models import ModelMetric, Prediction, Transaction

EVAL_PATH = Path(__file__).resolve().parents[1] / "ml" / "evaluation.json"


def latest_model_metric(db: Session) -> ModelMetric | None:
    return db.scalars(select(ModelMetric).order_by(desc(ModelMetric.created_at))).first()


def read_evaluation() -> dict[str, Any] | None:
    if not EVAL_PATH.exists():
        return None
    with EVAL_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_evaluation_metric(db: Session, evaluation: dict[str, Any]) -> ModelMetric:
    metrics = evaluation["metrics"]
    metric = ModelMetric(
        model_name=evaluation["model_name"], test_size=evaluation["test_size"], fraud_prevalence=evaluation["fraud_prevalence"],
        threshold=metrics["threshold"], precision=metrics["precision"], recall=metrics["recall"], f1=metrics["f1"],
        roc_auc=metrics["roc_auc"], false_positive_rate=metrics["false_positive_rate"],
        false_positive_cost=metrics["false_positive_cost"], false_negative_cost=metrics["false_negative_cost"],
        estimated_prevented_loss=metrics["estimated_prevented_loss"],
        confusion_matrix=json.dumps(metrics["confusion_matrix"]), feature_importance=json.dumps(evaluation["feature_importance"]),
    )
    db.add(metric)
    db.commit()
    return metric


def metrics_response(db: Session, threshold: float | None = None) -> dict[str, Any]:
    metric = latest_model_metric(db)
    evaluation = read_evaluation()
    if metric is None and evaluation is not None:
        metric = save_evaluation_metric(db, evaluation)
    if metric is None:
        return {"status": "unavailable", "message": "Model has not been trained yet."}

    response = {
        "model_name": metric.model_name, "test_size": metric.test_size, "fraud_prevalence": metric.fraud_prevalence,
        "threshold": metric.threshold, "precision": metric.precision, "recall": metric.recall, "f1": metric.f1,
        "roc_auc": metric.roc_auc, "false_positive_rate": metric.false_positive_rate,
        "false_positive_cost": metric.false_positive_cost, "false_negative_cost": metric.false_negative_cost,
        "estimated_prevented_loss": metric.estimated_prevented_loss, "confusion_matrix": json.loads(metric.confusion_matrix),
        "feature_importance": json.loads(metric.feature_importance),
        "baseline_validation_roc_auc": evaluation.get("baseline_validation_roc_auc") if evaluation else None,
        "final_validation_roc_auc": evaluation.get("final_validation_roc_auc") if evaluation else None,
        "threshold_curve": evaluation.get("threshold_curve", []) if evaluation else [],
        "evaluation_note": evaluation.get("evaluation_note", "") if evaluation else "",
        "cost_assumptions": {
            "false_positive": "₹100 per legitimate transaction flagged (demo assumption).",
            "false_negative": "Mean fraudulent transaction amount (demo assumption).",
            "prevented_loss": "Fraud amount × recall on the held-out test set; proxy only, not realized savings.",
        },
    }
    if threshold is not None and evaluation and evaluation.get("threshold_curve"):
        closest = min(evaluation["threshold_curve"], key=lambda item: abs(item["threshold"] - threshold))
        response["threshold_view"] = closest
    return response


def dashboard_stats(db: Session) -> dict[str, Any]:
    total = db.scalar(select(func.count(Prediction.id))) or 0
    high = db.scalar(select(func.count(Prediction.id)).where(Prediction.risk_level == "HIGH")) or 0
    medium = db.scalar(select(func.count(Prediction.id)).where(Prediction.risk_level == "MEDIUM")) or 0
    low = db.scalar(select(func.count(Prediction.id)).where(Prediction.risk_level == "LOW")) or 0
    exposure = db.scalar(select(func.sum(Transaction.amount)).join(Prediction, Prediction.transaction_id == Transaction.transaction_id).where(Prediction.risk_level == "HIGH")) or 0.0
    recent = db.execute(
        select(Prediction.risk_level, func.count(Prediction.id)).group_by(Prediction.risk_level)
    ).all()
    metric = latest_model_metric(db)
    hourly = db.execute(
        select(func.strftime("%H", Prediction.created_at), func.count(Prediction.id))
        .group_by(func.strftime("%H", Prediction.created_at)).order_by(func.strftime("%H", Prediction.created_at))
    ).all()
    return {
        "transactions_analyzed": total, "high_risk": high, "medium_risk": medium, "low_risk": low,
        "estimated_loss_prevented": float(exposure) * 0.18, "estimated_high_risk_exposure": float(exposure),
        "model_precision": float(metric.precision) if metric else 0.0,
        "risk_distribution": [{"name": level, "value": count} for level, count in recent],
        "activity": [{"hour": hour, "count": count} for hour, count in hourly],
        "model_available": metric is not None,
    }
