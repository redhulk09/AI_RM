"""Database models."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    amount: Mapped[float] = mapped_column(Float)
    customer_id: Mapped[str] = mapped_column(String(64), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    device_id: Mapped[str] = mapped_column(String(64))
    country: Mapped[str] = mapped_column(String(3))
    payment_method: Mapped[str] = mapped_column(String(32))
    account_age_days: Mapped[int] = mapped_column(Integer)
    transactions_last_10m: Mapped[int] = mapped_column(Integer)
    transactions_last_1h: Mapped[int] = mapped_column(Integer)
    failed_payments: Mapped[int] = mapped_column(Integer)
    previous_avg_amount: Mapped[float] = mapped_column(Float)
    amount_deviation: Mapped[float] = mapped_column(Float)
    is_new_device: Mapped[int] = mapped_column(Integer)
    is_new_location: Mapped[int] = mapped_column(Integer)
    distance_from_previous_location: Mapped[float] = mapped_column(Float)
    device_transaction_count: Mapped[int] = mapped_column(Integer)
    ip_transaction_count: Mapped[int] = mapped_column(Integer)
    hour: Mapped[int] = mapped_column(Integer)
    customer_transaction_count: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(64), index=True)
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(16), index=True)
    fraud_probability: Mapped[float] = mapped_column(Float)
    reasons: Mapped[str] = mapped_column(Text)
    recommended_action: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_name: Mapped[str] = mapped_column(String(64))
    test_size: Mapped[int] = mapped_column(Integer)
    fraud_prevalence: Mapped[float] = mapped_column(Float)
    threshold: Mapped[float] = mapped_column(Float)
    precision: Mapped[float] = mapped_column(Float)
    recall: Mapped[float] = mapped_column(Float)
    f1: Mapped[float] = mapped_column(Float)
    roc_auc: Mapped[float] = mapped_column(Float)
    false_positive_rate: Mapped[float] = mapped_column(Float)
    false_positive_cost: Mapped[float] = mapped_column(Float)
    false_negative_cost: Mapped[float] = mapped_column(Float)
    estimated_prevented_loss: Mapped[float] = mapped_column(Float)
    confusion_matrix: Mapped[str] = mapped_column(Text)
    feature_importance: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
