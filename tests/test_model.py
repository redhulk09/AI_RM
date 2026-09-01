import numpy as np

from backend.ml.dataset import generate_dataset
from backend.ml.predict import predict_rows, risk_level


def test_synthetic_dataset_has_imbalance_and_signal():
    df = generate_dataset(rows=1500, seed=12)
    prevalence = df["is_fraud"].mean()
    assert 0.02 < prevalence < 0.35
    assert df.groupby("is_fraud")["transactions_last_10m"].mean().loc[1] > df.groupby("is_fraud")["transactions_last_10m"].mean().loc[0]
    assert df.groupby("is_fraud")["amount_deviation"].mean().loc[1] > df.groupby("is_fraud")["amount_deviation"].mean().loc[0]


def base_row():
    return {
        "transaction_id": "TEST_TXN",
        "amount": 2200.0,
        "currency": "INR",
        "customer_id": "TEST_CUST",
        "account_age_days": 500,
        "device_id": "TEST_DEV",
        "country": "IN",
        "transactions_last_10m": 1,
        "transactions_last_1h": 3,
        "failed_payments": 0,
        "previous_transaction_amount": 2100.0,
        "previous_avg_amount": 2100.0,
        "amount_deviation": 1.05,
        "is_new_device": False,
        "is_new_location": False,
        "distance_from_previous_location": 20,
        "device_transaction_count": 2,
        "ip_transaction_count": 1,
        "payment_method": "upi",
        "hour": 13,
        "customer_transaction_count": 60,
    }


def test_prediction_shape_and_risk_bands():
    result = predict_rows([base_row()])[0]
    assert 0 <= result["risk_score"] <= 100
    assert result["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
    assert 0 <= result["fraud_probability"] <= 1
    assert result["reasons"]
    assert risk_level(10) == "LOW" if False else risk_level(70) == "HIGH"


def test_suspicious_combination_scores_above_normal_case():
    normal = base_row()
    suspicious = {**normal, "amount": 42850, "previous_avg_amount": 10100, "amount_deviation": 4.24, "transactions_last_10m": 8, "transactions_last_1h": 16, "failed_payments": 4, "is_new_device": True, "is_new_location": True, "distance_from_previous_location": 2110, "device_transaction_count": 15, "ip_transaction_count": 11, "account_age_days": 24}
    predictions = predict_rows([normal, suspicious])
    assert predictions[1]["fraud_probability"] > predictions[0]["fraud_probability"]
    assert predictions[1]["risk_score"] > predictions[0]["risk_score"]
