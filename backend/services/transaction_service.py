"""Persistence and prediction orchestration."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..ml.predict import predict_rows
from ..models import Prediction, Transaction


def _db_transaction(result: dict[str, Any]) -> Transaction:
    timestamp = result.get("timestamp") or datetime.now(timezone.utc)
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return Transaction(
        transaction_id=result["transaction_id"], amount=result["amount"], customer_id=result["customer_id"], timestamp=timestamp,
        device_id=result["device_id"], country=result["country"], payment_method=result["payment_method"], account_age_days=result["account_age_days"],
        transactions_last_10m=result["transactions_last_10m"], transactions_last_1h=result["transactions_last_1h"], failed_payments=result["failed_payments"],
        previous_avg_amount=result["previous_avg_amount"], amount_deviation=result["amount_deviation"], is_new_device=int(result["is_new_device"]),
        is_new_location=int(result["is_new_location"]), distance_from_previous_location=result["distance_from_previous_location"],
        device_transaction_count=result["device_transaction_count"], ip_transaction_count=result["ip_transaction_count"], hour=result["hour"],
        customer_transaction_count=result["customer_transaction_count"], currency=result.get("currency", "INR"),
    )


def save_prediction(db: Session, result: dict[str, Any], commit: bool = True) -> None:
    existing = db.scalar(select(Transaction).where(Transaction.transaction_id == result["transaction_id"]))
    if existing is None:
        db.add(_db_transaction(result))
    db.add(Prediction(
        transaction_id=result["transaction_id"], risk_score=result["risk_score"], risk_level=result["risk_level"],
        fraud_probability=result["fraud_probability"], reasons=json.dumps(result["reasons"]), recommended_action=result["recommended_action"],
    ))
    if commit:
        db.commit()


def serialize_prediction(result: dict[str, Any]) -> dict[str, Any]:
    hidden = {"reasons", "top_features", "risk_score", "risk_level", "fraud_probability", "recommended_action", "threshold_used", "flagged"}
    return {
        "transaction_id": result["transaction_id"], "risk_score": result["risk_score"], "risk_level": result["risk_level"],
        "fraud_probability": result["fraud_probability"], "reasons": result["reasons"], "top_features": result["top_features"],
        "recommended_action": result["recommended_action"], "transaction": {k: v for k, v in result.items() if k not in hidden},
    }


def predict_and_save(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    payload = dict(payload)
    payload["transaction_id"] = payload.get("transaction_id") or f"TXN_{uuid.uuid4().hex[:8].upper()}"
    payload["is_new_device"] = int(bool(payload.get("is_new_device", False)))
    payload["is_new_location"] = int(bool(payload.get("is_new_location", False)))
    previous_avg = float(payload.get("previous_avg_amount", 0) or 0)
    payload["amount_deviation"] = float(payload.get("amount_deviation") or (payload["amount"] / max(previous_avg, 1)))
    result = predict_rows([payload], threshold=float(payload.get("threshold", 0.70)))[0]
    save_prediction(db, result)
    return serialize_prediction(result)


def recent_transactions(db: Session, limit: int = 20) -> list[dict[str, Any]]:
    stmt = select(Transaction, Prediction).join(Prediction, Prediction.transaction_id == Transaction.transaction_id).order_by(desc(Prediction.created_at)).limit(limit)
    rows = db.execute(stmt).all()
    seen: set[str] = set()
    output: list[dict[str, Any]] = []
    for transaction, prediction in rows:
        if transaction.transaction_id in seen:
            continue
        seen.add(transaction.transaction_id)
        output.append({
            "transaction_id": transaction.transaction_id, "amount": transaction.amount, "customer_id": transaction.customer_id,
            "country": transaction.country, "payment_method": transaction.payment_method, "risk_score": prediction.risk_score,
            "risk_level": prediction.risk_level, "fraud_probability": prediction.fraud_probability, "reasons": json.loads(prediction.reasons),
            "created_at": prediction.created_at,
        })
    return output


def transaction_detail(db: Session, transaction_id: str) -> dict[str, Any] | None:
    transaction = db.scalar(select(Transaction).where(Transaction.transaction_id == transaction_id))
    prediction = db.scalars(select(Prediction).where(Prediction.transaction_id == transaction_id).order_by(desc(Prediction.created_at))).first()
    if not transaction or not prediction:
        return None
    return {
        "transaction_id": transaction.transaction_id, "amount": transaction.amount, "customer_id": transaction.customer_id,
        "timestamp": transaction.timestamp, "device_id": transaction.device_id, "country": transaction.country,
        "payment_method": transaction.payment_method, "account_age_days": transaction.account_age_days,
        "transactions_last_10m": transaction.transactions_last_10m, "transactions_last_1h": transaction.transactions_last_1h,
        "failed_payments": transaction.failed_payments, "previous_avg_amount": transaction.previous_avg_amount,
        "amount_deviation": transaction.amount_deviation, "is_new_device": bool(transaction.is_new_device), "is_new_location": bool(transaction.is_new_location),
        "distance_from_previous_location": transaction.distance_from_previous_location, "device_transaction_count": transaction.device_transaction_count,
        "ip_transaction_count": transaction.ip_transaction_count, "customer_transaction_count": transaction.customer_transaction_count,
        "risk_score": prediction.risk_score, "risk_level": prediction.risk_level, "fraud_probability": prediction.fraud_probability,
        "reasons": json.loads(prediction.reasons), "recommended_action": prediction.recommended_action,
    }
