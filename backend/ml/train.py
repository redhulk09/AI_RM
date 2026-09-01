"""Train and persist the RiskLens baseline/final models.

Evaluation uses train/validation/test splits. The final test set is touched once
for final reporting and is never used for model selection or tuning.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .dataset import write_dataset
from .evaluate import classification_metrics, threshold_curve
from .features import build_preprocessor, prepare_features

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "transactions.csv"
MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"
EVAL_PATH = Path(__file__).resolve().parent / "evaluation.json"

FALSE_POSITIVE_UNIT_COST = 100.0
FALSE_NEGATIVE_COST_MULTIPLIER = 1.0


def build_models() -> tuple[Pipeline, Pipeline]:
    baseline = Pipeline(
        [
            ("preprocessor", build_preprocessor(scale_numeric=True)),
            ("model", LogisticRegression(max_iter=1200, class_weight="balanced", random_state=42)),
        ]
    )
    final = Pipeline(
        [
            ("preprocessor", build_preprocessor(scale_numeric=False)),
            ("model", RandomForestClassifier(n_estimators=180, max_depth=14, min_samples_leaf=3, class_weight="balanced_subsample", n_jobs=-1, random_state=42)),
        ]
    )
    return baseline, final


def train_and_evaluate(data_path: str | Path = DATA_PATH) -> dict:
    data_path = Path(data_path)
    if not data_path.exists():
        write_dataset(data_path)

    df = pd.read_csv(data_path)
    X = prepare_features(df)
    y = df["is_fraud"].astype(int).to_numpy()
    amounts = df["amount"].to_numpy(dtype=float)

    X_train, X_test, y_train, y_test, amount_train, amount_test = train_test_split(
        X, y, amounts, test_size=0.20, stratify=y, random_state=42
    )
    X_subtrain, X_val, y_subtrain, y_val = train_test_split(
        X_train, y_train, test_size=0.25, stratify=y_train, random_state=42
    )

    baseline, final = build_models()
    baseline.fit(X_subtrain, y_subtrain)
    final.fit(X_subtrain, y_subtrain)
    baseline_val = baseline.predict_proba(X_val)[:, 1]
    final_val = final.predict_proba(X_val)[:, 1]
    baseline_auc = roc_auc_score(y_val, baseline_val)
    final_auc = roc_auc_score(y_val, final_val)

    selected_name = "Random Forest" if final_auc >= baseline_auc else "Logistic Regression"
    selected_template = final if selected_name == "Random Forest" else baseline
    selected_template.fit(pd.concat([X_subtrain, X_val]), np.concatenate([y_subtrain, y_val]))

    test_probabilities = selected_template.predict_proba(X_test)[:, 1]
    metrics = classification_metrics(
        y_test,
        test_probabilities,
        threshold=0.50,
        amounts=amount_test,
        false_positive_cost=FALSE_POSITIVE_UNIT_COST,
        false_negative_rate_cost=FALSE_NEGATIVE_COST_MULTIPLIER,
    )
    curve = threshold_curve(y_test, test_probabilities)

    preprocessor = selected_template.named_steps["preprocessor"]
    estimator = selected_template.named_steps["model"]
    transformed_names = preprocessor.get_feature_names_out().tolist()
    transformed_importances = getattr(estimator, "feature_importances_", None)
    if transformed_importances is None:
        transformed_importances = np.abs(estimator.coef_[0])
    raw_importance: dict[str, float] = {}
    for name, value in zip(transformed_names, transformed_importances):
        raw = name.split("__", 1)[-1]
        if raw.startswith("country_"):
            raw = "country"
        elif raw.startswith("payment_method_"):
            raw = "payment_method"
        raw_importance[raw] = raw_importance.get(raw, 0.0) + float(abs(value))
    ordered_importance = [
        {"feature": name, "importance": round(value, 6)}
        for name, value in sorted(raw_importance.items(), key=lambda item: item[1], reverse=True)[:12]
    ]

    artifact = {
        "model": selected_template,
        "model_name": selected_name,
        "selected_by": "validation ROC-AUC",
        "baseline_validation_roc_auc": baseline_auc,
        "final_validation_roc_auc": final_auc,
        "feature_importance": ordered_importance,
        "threshold": 0.50,
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, MODEL_PATH)

    evaluation = {
        "model_name": selected_name,
        "test_size": int(len(y_test)),
        "fraud_prevalence": float(np.mean(y_test)),
        "metrics": metrics,
        "threshold_curve": curve,
        "feature_importance": ordered_importance,
        "baseline_validation_roc_auc": float(baseline_auc),
        "final_validation_roc_auc": float(final_auc),
        "false_positive_cost_assumption": FALSE_POSITIVE_UNIT_COST,
        "false_negative_cost_assumption": "mean fraudulent transaction amount × 1.0",
        "estimated_prevented_loss_assumption": "test fraud amount × recall; demo proxy, not realized savings",
        "evaluation_note": "Final metrics are calculated on a completely held-out test set that was not used for model selection or tuning. Demo data is synthetic.",
    }
    with EVAL_PATH.open("w", encoding="utf-8") as handle:
        json.dump(evaluation, handle, indent=2)
    return evaluation


if __name__ == "__main__":
    result = train_and_evaluate()
    print(json.dumps(result, indent=2))
