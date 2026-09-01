"""Generate the synthetic demo dataset."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.ml.dataset import write_dataset  # noqa: E402


if __name__ == "__main__":
    path = write_dataset(ROOT / "data" / "transactions.csv", rows=12_000, seed=42)
    print(f"Wrote synthetic dataset to {path}")
