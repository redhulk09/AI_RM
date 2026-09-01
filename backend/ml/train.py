"""Train and persist the RiskLens baseline/final models."""

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

from .dataset import generate_dataset, write_dataset
from .evaluate import classification_metrics, threshold_curve
from .features import build_preprocessor, prepare_features

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "transactions.csv"
MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"
EVAL_PATH = Path(__file__).resolve().parent / "evaluation.json"

FALSE_POSITIVE_UNIT_COST = 100.0
FALSE_NEGATIVE_COST_MULTIPLIER = 1.0
MIN_TRAINING_ROWS = 1000


def build_models() -> tuple[Pipeline, Pipeline]:
    baseline = Pipeline([("preprocessor", build_preprocessor(scale_numeric=True)), ("model", LogisticRegression(max_iter=1200, class_weight="balanced", random_state=42))])
    final = Pipeline([("preprocessor", build_preprocessor(scale_numeric=False)), ("model", RandomForestClassifier(n_estimators=180, max_depth=14, min_samples_leaf=3, class_weight="balanced_subsample", n_jobs=-1, random_state=42))])
    return baseline, final


def train_and_evaluate(data_path: str | Path = DATA_PATH) -> dict:
    data_path = Path(data_path)
    if not data_path.exists():
        write_dataset(data_path)
    df = pd.read_csv(data_path)
    source = "provided dataset"
    if len(df) < MIN_TRAINING_ROWS or df["is_fraud"].nunique() < 2 or int(df["is_fraud"].sum()) < 20:
        df = generate_dataset(rows=12_000, seed=42)
        source = "synthetic fallback dataset generated because the committed sample is too small for honest evaluation"

    X = prepare_features(df)
    y = df["is_fraud"].astype(int).to_numpy()
    amounts = df["amount"].to_numpy(dtype=float)
    X_train, X_test, y_train, y_test, _, amount_test = train_test_split(X, y, amounts, test_size=0.20, stratify=y, random_state=42)
    X_subtrain, X_val, y_subtrain, y_val = train_test_split(X_train, y_train, test_size=0.25, stratify=y_train, random_state=42)

    baseline, final = build_models()
    baseline.fit(X_subtrain, y_subtrain)
    final.fit(X_subtrain, y_subtrain)
    baseline_auc = roc_auc_score(y_val, baseline.predict_proba(X_val)[:, 1])
    final_auc = roc_auc_score(y_val, final.predict_proba(X_val)[:, 1])
    selected_name = "Random Forest" if final_auc >= baseline_auc else "Logistic Regression"
    selected = final if selected_name == "Random Forest" else baseline
    selected.fit(pd.concat([X_subtrain, X_val]), np.concatenate([y_subtrain, y_val]))
    probabilities = selected.predict_proba(X_test)[:, 1]
    metrics = classification_metrics(y_test, probabilities, threshold=0.50, amounts=amount_test, false_positive_cost=FALSE_POSITIVE_UNIT_COST, false_negative_rate_cost=FALSE_NEGATIVE_COST_MULTIPLIER)
    curve = threshold_curve(y_test, probabilities)

    preprocessor = selected.named_steps["preprocessor"]
    estimator = selected.named_steps["model"]
    names = preprocessor.get_feature_names_out().tolist()
    importances = getattr(estimator, "feature_importances_", None)
    if importances is None:
        importances = np.abs(estimator.coef_[0])
    aggregated: dict[str, float] = {}
    for name, value in zip(names, importances):
        raw = name.split("__", 1)[-1]
        if raw.startswith("country_"):
            raw = "country"
        elif raw.startswith("payment_method_"):
            raw = "payment_method"
        aggregated[raw] = aggregated.get(raw, 0.0) + float(abs(value))
    feature_importance = [{"feature": k, "importance": round(v, 6)} for k, v in sorted(aggregated.items(), key=lambda item: item[1], reverse=True)[:12]]

    joblib.dump({"model": selected, "model_name": selected_name, "selected_by": "validation ROC-AUC", "baseline_validation_roc_auc": baseline_auc, "final_validation_roc_auc": final_auc, "feature_importance": feature_importance, "threshold": 0.50}, MODEL_PATH)
    evaluation = {"model_name": selected_name, "test_size": int(len(y_test)), "fraud_prevalence": float(np.mean(y_test)), "metrics": metrics, "threshold_curve": curve, "feature_importance": feature_importance, "baseline_validation_roc_auc": float(baseline_auc), "final_validation_roc_auc": float(final_auc), "false_positive_cost_assumption": FALSE_POSITIVE_UNIT_COST, "false_negative_cost_assumption": "mean fraudulent transaction amount × 1.0", "estimated_prevented_loss_assumption": "test fraud amount × recall; demo proxy, not realized savings", "evaluation_note": f"Final metrics use a completely held-out test set not used for selection or tuning. Data source: {source}. All demo data is synthetic."}
    with EVAL_PATH.open("w", encoding="utf-8") as handle:
        json.dump(evaluation, handle, indent=2)
    return evaluation


if __name__ == "__main__":
    print(json.dumps(train_and_evaluate(), indent=2))
