"""Seed RiskLens with memorable demo scenarios and additional synthetic traffic."""

from pathlib import Path
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.database import SessionLocal, init_db  # noqa: E402
from backend.ml.dataset import generate_dataset  # noqa: E402
from backend.ml.predict import load_artifact  # noqa: E402
from backend.services.transaction_service import predict_and_save  # noqa: E402


def scenario(transaction_id: str, amount: float, previous_avg: float, velocity: int, failed: int, new_device: bool, new_location: bool, distance: float, device_count: int, ip_count: int, customer_count: int, hour: int, payment_method: str, country: str = "IN") -> dict:
    return {
        "transaction_id": transaction_id, "amount": amount, "currency": "INR", "customer_id": f"DEMO_{transaction_id[-4:]}",
        "account_age_days": 420 if not new_device else 24, "device_id": f"DEMO_DEV_{transaction_id[-4:]}", "country": country,
        "transactions_last_10m": velocity, "transactions_last_1h": velocity * 2, "failed_payments": failed,
        "previous_transaction_amount": previous_avg, "previous_avg_amount": previous_avg, "previous_transaction_frequency": 2.0,
        "is_new_device": new_device, "is_new_location": new_location, "distance_from_previous_location": distance,
        "device_transaction_count": device_count, "ip_transaction_count": ip_count, "customer_transaction_count": customer_count,
        "payment_method": payment_method, "hour": hour, "timestamp": datetime.now(timezone.utc).isoformat(), "threshold": 0.70,
        "amount_deviation": amount / max(previous_avg, 1),
    }


def main() -> None:
    init_db()
    load_artifact()
    rows = [
        scenario("DEMO_NORMAL", 1299, 1250, 1, 0, False, False, 12, 2, 1, 48, 13, "upi"),
        scenario("DEMO_HIGH_AMOUNT", 38500, 8200, 2, 0, False, False, 40, 3, 2, 35, 19, "card"),
        scenario("DEMO_VELOCITY", 2400, 2200, 9, 0, False, False, 20, 12, 9, 72, 20, "upi"),
        scenario("DEMO_NEW_DEVICE", 8900, 3200, 2, 0, True, False, 80, 2, 2, 26, 16, "card"),
        scenario("DEMO_FAILURES", 6200, 5100, 4, 4, False, False, 25, 3, 3, 65, 11, "wallet"),
        scenario("DEMO_LOCATION", 7200, 6800, 2, 1, False, True, 1840, 3, 2, 44, 3, "netbanking", "AE"),
        scenario("DEMO_COMBINED", 42850, 10100, 8, 4, True, True, 2110, 15, 11, 18, 2, "card", "US"),
    ]
    synthetic = generate_dataset(rows=180, seed=7).drop(columns=["is_fraud"])
    rows.extend(synthetic.to_dict("records"))
    db = SessionLocal()
    try:
        for row in rows:
            try:
                predict_and_save(db, row)
            except Exception as exc:  # noqa: BLE001 - demo seeding should continue past duplicate rows.
                db.rollback()
                print(f"Skipped {row.get('transaction_id')}: {exc}")
    finally:
        db.close()
    print(f"Seeded {len(rows)} demo transactions.")


if __name__ == "__main__":
    main()
