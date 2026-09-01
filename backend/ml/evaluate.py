"""Held-out evaluation and threshold trade-off helpers."""

from __future__ import annotations

import json
from typing import Any

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score


def classification_metrics(y_true: np.ndarray, probabilities: np.ndarray, threshold: float = 0.5, amounts: np.ndarray | None = None, false_positive_cost: float = 100.0, false_negative_rate_cost: float = 1.0) -> dict[str, Any]:
    predictions = (probabilities >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, predictions, labels=[0, 1]).ravel()
    precision = precision_score(y_true, predictions, zero_division=0)
    recall = recall_score(y_true, predictions, zero_division=0)
    f1 = f1_score(y_true, predictions, zero_division=0)
    roc_auc = roc_auc_score(y_true, probabilities) if len(np.unique(y_true)) > 1 else 0.0
    fpr = fp / max(fp + tn, 1)
    fn_cost = float(np.mean(amounts[y_true == 1]) if amounts is not None and np.any(y_true == 1) else 1_000.0) * false_negative_rate_cost
    prevented = float(np.sum(amounts[y_true == 1])) if amounts is not None else 0.0
    prevented *= recall
    total_cost = fp * false_positive_cost + fn * fn_cost
    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(roc_auc),
        "false_positive_rate": float(fpr),
        "false_positive_cost": float(fp * false_positive_cost),
        "false_negative_cost": float(fn * fn_cost),
        "estimated_prevented_loss": prevented,
        "total_error_cost": float(total_cost),
        "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
        "threshold": float(threshold),
    }


def threshold_curve(y_true: np.ndarray, probabilities: np.ndarray, thresholds: list[float] | None = None) -> list[dict[str, float]]:
    thresholds = thresholds or [round(x, 2) for x in np.linspace(0.1, 0.9, 9)]
    return [
        {"threshold": threshold, "precision": classification_metrics(y_true, probabilities, threshold)["precision"], "recall": classification_metrics(y_true, probabilities, threshold)["recall"], "f1": classification_metrics(y_true, probabilities, threshold)["f1"]}
        for threshold in thresholds
    ]


def dump_json(payload: dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
