"""REST endpoints for prediction, batch analysis, dashboards, and training."""

from __future__ import annotations

import csv
import io
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..ml.predict import predict_rows
from ..ml.train import train_and_evaluate
from ..models import Prediction
from ..schemas import BatchResult, ModelMetricsOut, PredictionOut, TransactionInput
from ..services.metrics_service import dashboard_stats, metrics_response, save_evaluation_metric
from ..services.transaction_service import predict_and_save, recent_transactions, transaction_detail

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/predict", response_model=PredictionOut)
def predict(payload: TransactionInput, db: Session = Depends(get_db)):
    try:
        return predict_and_save(db, payload.model_dump())
    except (ValueError, SQLAlchemyError, FileNotFoundError) as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/batch-predict", response_model=BatchResult)
def batch_predict(file: UploadFile = File(...), threshold: float = Query(0.70, ge=0.01, le=0.99), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")
    raw = file.file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="The uploaded CSV is empty.")
    try:
        text = raw.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise HTTPException(status_code=400, detail="CSV header row is missing.")
        rows = list(reader)
        if not rows:
            raise HTTPException(status_code=400, detail="The uploaded CSV contains no transactions.")
        valid: list[dict[str, Any]] = []
        invalid = 0
        for index, row in enumerate(rows, start=2):
            try:
                normalized = _csv_row_to_transaction(row)
                valid.append(normalized)
            except (KeyError, TypeError, ValueError):
                invalid += 1
        if not valid:
            raise HTTPException(status_code=422, detail="No valid transaction rows were found in the CSV.")
        predictions = predict_rows(valid, threshold=threshold)
        for result in predictions:
            from ..services.transaction_service import save_prediction
            save_prediction(db, result)
        high = sum(item["risk_level"] == "HIGH" for item in predictions)
        medium = sum(item["risk_level"] == "MEDIUM" for item in predictions)
        low = len(predictions) - high - medium
        exposure = sum(item["amount"] for item in predictions if item["risk_level"] == "HIGH")
        return {
            "filename": file.filename, "rows_detected": len(rows), "valid_transactions": len(valid), "invalid_rows": invalid,
            "summary": {"total_analyzed": len(predictions), "high_risk": high, "medium_risk": medium, "low_risk": low, "estimated_exposure": exposure},
            "results": [
                {"transaction_id": item["transaction_id"], "risk_score": item["risk_score"], "risk_level": item["risk_level"], "fraud_probability": item["fraud_probability"], "reasons": item["reasons"], "top_features": item["top_features"], "recommended_action": item["recommended_action"], "transaction": {k: v for k, v in item.items() if k not in {"risk_score", "risk_level", "fraud_probability", "reasons", "top_features", "recommended_action", "threshold_used", "flagged"}}}
                for item in predictions
            ],
        }
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded.") from exc


def _csv_row_to_transaction(row: dict[str, str]) -> dict[str, Any]:
    def integer(name: str, default: int = 0) -> int:
        return int(float(row.get(name, default)))

    def number(name: str, default: float = 0) -> float:
        return float(row.get(name, default))

    amount = number("amount")
    if amount <= 0:
        raise ValueError("amount must be positive")
    previous_avg = number("previous_avg_amount")
    return {
        "transaction_id": row.get("transaction_id") or None, "amount": amount, "currency": row.get("currency", "INR"),
        "customer_id": row["customer_id"], "account_age_days": integer("account_age_days"), "device_id": row.get("device_id", "demo-device"),
        "country": row.get("country", "IN"), "transactions_last_10m": integer("transactions_last_10m"),
        "transactions_last_1h": integer("transactions_last_1h"), "failed_payments": integer("failed_payments"),
        "previous_transaction_amount": number("previous_transaction_amount"), "previous_avg_amount": previous_avg,
        "previous_transaction_frequency": number("previous_transaction_frequency"), "is_new_device": bool(int(float(row.get("is_new_device", 0)))),
        "is_new_location": bool(int(float(row.get("is_new_location", 0)))), "distance_from_previous_location": number("distance_from_previous_location"),
        "device_transaction_count": integer("device_transaction_count", 1), "ip_transaction_count": integer("ip_transaction_count", 1),
        "customer_transaction_count": integer("customer_transaction_count", 1), "payment_method": row.get("payment_method", "upi"),
        "hour": integer("hour", 12), "threshold": 0.70,
        "amount_deviation": number("amount_deviation", amount / max(previous_avg, 1)),
    }


@router.get("/metrics")
def metrics(threshold: float | None = Query(default=None, ge=0.01, le=0.99), db: Session = Depends(get_db)):
    try:
        return metrics_response(db, threshold=threshold)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Unable to read model metrics.") from exc


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)) -> dict[str, Any]:
    return dashboard_stats(db) | {"recent_transactions": recent_transactions(db, 8)}


@router.get("/transactions")
def transactions(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    return recent_transactions(db, limit)


@router.get("/transactions/{transaction_id}")
def transaction(transaction_id: str, db: Session = Depends(get_db)):
    result = transaction_detail(db, transaction_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result


@router.post("/train")
def train(db: Session = Depends(get_db)):
    try:
        evaluation = train_and_evaluate()
        save_evaluation_metric(db, evaluation)
        return evaluation
    except Exception as exc:  # noqa: BLE001 - API boundary converts training failures to a clean response.
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Model training failed: {exc}") from exc


@router.get("/transactions/export")
def export_transactions(limit: int = Query(5000, ge=1, le=10000), db: Session = Depends(get_db)):
    rows = recent_transactions(db, limit)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["transaction_id", "amount", "risk_score", "risk_level", "fraud_probability", "reason"])
    for row in rows:
        writer.writerow([row["transaction_id"], row["amount"], row["risk_score"], row["risk_level"], row["fraud_probability"], "; ".join(row["reasons"])])
    buffer.seek(0)
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=risklens-results.csv"})
