"""FastAPI application entry point for RiskLens."""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path

if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.database import init_db
from backend.ml.predict import MODEL_PATH
from backend.ml.train import train_and_evaluate
from backend.services.metrics_service import save_evaluation_metric
from backend.database import SessionLocal


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    if not MODEL_PATH.exists():
        evaluation = train_and_evaluate()
        db = SessionLocal()
        try:
            save_evaluation_metric(db, evaluation)
        finally:
            db.close()
    yield


app = FastAPI(title="RiskLens API", version="1.0.0", description="Defense-only AI transaction risk intelligence for merchants.", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
