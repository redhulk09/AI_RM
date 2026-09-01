"""Synthetic, demo-only transaction dataset generator."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

COUNTRIES = ["IN", "AE", "SG", "US", "GB"]
PAYMENT_METHODS = ["upi", "card", "netbanking", "wallet"]


def generate_dataset(rows: int = 12_000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    customer_count = max(500, rows // 8)
    customers = np.array([f"CUST_{i:05d}" for i in range(customer_count)])
    devices = np.array([f"DEV_{i:05d}" for i in range(rows // 2 + 50)])

    customer_id = rng.choice(customers, rows)
    account_age_days = np.clip(rng.gamma(shape=3.2, scale=150, size=rows).astype(int), 0, 5000)
    previous_avg = np.clip(rng.lognormal(mean=7.0, sigma=0.85, size=rows), 100, 250_000)
    amount_multiplier = np.exp(rng.normal(0, 0.42, rows))
    amount = np.clip(previous_avg * amount_multiplier, 50, 500_000)

    velocity = rng.poisson(1.8, rows)
    velocity += (rng.random(rows) < 0.035) * rng.integers(5, 16, rows)
    velocity = velocity.astype(int)
    transactions_last_1h = velocity + rng.poisson(4, rows)
    failed = rng.poisson(0.35, rows) + (rng.random(rows) < 0.015) * rng.integers(2, 6, rows)
    failed = failed.astype(int)

    is_new_device = (rng.random(rows) < 0.12).astype(int)
    is_new_location = (rng.random(rows) < 0.07).astype(int)
    distance = np.where(is_new_location, rng.gamma(2.4, 520, rows), rng.gamma(1.3, 35, rows))
    device_tx_count = rng.poisson(2.4, rows) + is_new_device
    ip_tx_count = rng.poisson(1.8, rows) + (velocity >= 7)
    customer_tx_count = rng.poisson(18, rows) + 1
    hour = rng.integers(0, 24, rows)
    country = rng.choice(COUNTRIES, rows, p=[0.73, 0.08, 0.07, 0.07, 0.05])
    payment_method = rng.choice(PAYMENT_METHODS, rows, p=[0.53, 0.28, 0.11, 0.08])

    amount_deviation = amount / np.maximum(previous_avg, 1)
    logit = (
        -5.2
        + 0.33 * np.minimum(velocity, 14)
        + 0.21 * np.minimum(transactions_last_1h, 30)
        + 0.48 * failed
        + 1.15 * is_new_device
        + 1.05 * is_new_location
        + 0.0014 * np.minimum(distance, 2500)
        + 1.35 * np.clip(amount_deviation - 1.6, 0, 4)
        + 0.03 * np.maximum(1 - account_age_days / 100, 0)
        + 0.19 * np.log1p(ip_tx_count)
        + 0.06 * np.maximum(device_tx_count - 8, 0)
        + 0.18 * ((velocity >= 7) & (is_new_device == 1))
        + 0.34 * ((failed >= 3) & (velocity >= 5))
        + 0.22 * ((amount_deviation >= 3) & (is_new_location == 1))
    )
    fraud_probability = 1 / (1 + np.exp(-logit))
    is_fraud = (rng.random(rows) < fraud_probability).astype(int)

    frame = pd.DataFrame(
        {
            "transaction_id": [f"TXN_{i:06d}" for i in range(rows)],
            "amount": amount.round(2),
            "account_age_days": account_age_days,
            "transactions_last_10m": velocity,
            "transactions_last_1h": transactions_last_1h,
            "failed_payments": failed,
            "previous_avg_amount": previous_avg.round(2),
            "amount_deviation": amount_deviation.round(3),
            "is_new_device": is_new_device,
            "is_new_location": is_new_location,
            "distance_from_previous_location": distance.round(2),
            "device_transaction_count": device_tx_count,
            "ip_transaction_count": ip_tx_count,
            "payment_method": payment_method,
            "hour": hour,
            "country": country,
            "customer_transaction_count": customer_tx_count,
            "is_fraud": is_fraud,
        }
    )
    return frame


def write_dataset(path: str | Path, rows: int = 12_000, seed: int = 42) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    generate_dataset(rows=rows, seed=seed).to_csv(destination, index=False)
    return destination


if __name__ == "__main__":
    write_dataset(Path(__file__).resolve().parents[2] / "data" / "transactions.csv")
