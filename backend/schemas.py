"""Pydantic request/response contracts."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TransactionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: str | None = Field(default=None, min_length=2, max_length=64)
    amount: float = Field(gt=0, le=100_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    customer_id: str = Field(min_length=2, max_length=64)
    account_age_days: int = Field(ge=0, le=10_000)
    device_id: str = Field(min_length=2, max_length=64)
    ip_address: str | None = Field(default=None, min_length=3, max_length=64)
    country: str = Field(min_length=2, max_length=3)
    transactions_last_10m: int = Field(ge=0, le=10_000)
    transactions_last_1h: int = Field(default=0, ge=0, le=50_000)
    failed_payments: int = Field(ge=0, le=10_000)
    previous_transaction_amount: float = Field(default=0, ge=0)
    previous_avg_amount: float = Field(default=0, ge=0)
    previous_transaction_frequency: float = Field(default=0, ge=0)
    is_new_device: bool = False
    is_new_location: bool = False
    distance_from_previous_location: float = Field(default=0, ge=0, le=50_000)
    device_transaction_count: int = Field(default=1, ge=0, le=100_000)
    ip_transaction_count: int = Field(default=1, ge=0, le=100_000)
    customer_transaction_count: int = Field(default=1, ge=0, le=100_000)
    payment_method: str = Field(default="upi", min_length=2, max_length=32)
    hour: int = Field(default=12, ge=0, le=23)
    timestamp: datetime | None = None
    threshold: float = Field(default=0.70, ge=0.01, le=0.99)


class PredictionOut(BaseModel):
    transaction_id: str
    risk_score: int
    risk_level: str
    fraud_probability: float
    reasons: list[str]
    top_features: list[dict[str, Any]]
    recommended_action: str
    transaction: dict[str, Any]


class BatchResult(BaseModel):
    filename: str
    rows_detected: int
    valid_transactions: int
    invalid_rows: int
    summary: dict[str, Any]
    results: list[PredictionOut]


class ModelMetricsOut(BaseModel):
    model_name: str
    test_size: int
    fraud_prevalence: float
    threshold: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    false_positive_rate: float
    false_positive_cost: float
    false_negative_cost: float
    estimated_prevented_loss: float
    confusion_matrix: list[list[int]]
    feature_importance: list[dict[str, Any]]
    evaluation_note: str
