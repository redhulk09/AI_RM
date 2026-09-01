"""Train the demo model from the repository root."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.database import init_db, SessionLocal  # noqa: E402
from backend.ml.train import train_and_evaluate  # noqa: E402
from backend.services.metrics_service import save_evaluation_metric  # noqa: E402


if __name__ == "__main__":
    init_db()
    evaluation = train_and_evaluate()
    db = SessionLocal()
    try:
        save_evaluation_metric(db, evaluation)
    finally:
        db.close()
    print(f"Trained {evaluation['model_name']} on a held-out test set of {evaluation['test_size']} rows.")
