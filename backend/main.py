"""FastAPI application entry point for RiskLens."""

from __future__ import annotations

import os
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
from backend.database import SessionLocal, init_db
from backend.ml.predict import MODEL_PATH
from backend.ml.train import train_and_evaluate
from backend.services.metrics_service import save_evaluation_metric


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
origins = [origin.strip() for origin in os.getenv("RISK_LENS_FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.include_router(router)
