"""Feature engineering shared by training and inference."""

from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = [
    "amount",
    "account_age_days",
    "transactions_last_10m",
    "transactions_last_1h",
    "failed_payments",
    "previous_avg_amount",
    "amount_deviation",
    "is_new_device",
    "is_new_location",
    "distance_from_previous_location",
    "device_transaction_count",
    "ip_transaction_count",
    "hour",
    "customer_transaction_count",
]
CATEGORICAL_FEATURES = ["country", "payment_method"]
MODEL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    for col in NUMERIC_FEATURES:
        if col not in frame:
            frame[col] = 0
    for col in CATEGORICAL_FEATURES:
        if col not in frame:
            frame[col] = "unknown"

    frame["previous_avg_amount"] = frame["previous_avg_amount"].fillna(0).clip(lower=0)
    derived_denominator = frame["previous_avg_amount"].replace(0, 1)
    if "amount_deviation" not in df.columns:
        frame["amount_deviation"] = (frame["amount"] / derived_denominator).clip(0, 100)
    else:
        frame["amount_deviation"] = frame["amount_deviation"].fillna(frame["amount"] / derived_denominator).clip(0, 100)

    return frame[MODEL_FEATURES]


def build_preprocessor(scale_numeric: bool = True) -> ColumnTransformer:
    numeric_transformer: Any = StandardScaler() if scale_numeric else "passthrough"
    return ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
