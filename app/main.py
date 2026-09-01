"""FastAPI entry point for AI Risk Manager."""

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .ai import analyze_risk
from .models import Risk, RiskCreate
from .risk_engine import assess_risk
from .storage import create_risk, delete_risk, get_risk, init_db, list_risks, update_recommendation

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI(title="AI Risk Manager", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/risks", response_model=list[Risk])
def risks() -> list[dict]:
    return list_risks()


@app.post("/api/risks", response_model=Risk, status_code=201)
def add_risk(payload: RiskCreate) -> dict:
    assessment = assess_risk(payload.likelihood, payload.impact, payload.control_effectiveness)
    return create_risk({**payload.model_dump(), **assessment.__dict__})


@app.get("/api/risks/{risk_id}", response_model=Risk)
def risk(risk_id: int) -> dict:
    item = get_risk(risk_id)
    if not item:
        raise HTTPException(404, "Risk not found")
    return item


@app.delete("/api/risks/{risk_id}", status_code=204)
def remove_risk(risk_id: int) -> None:
    if not delete_risk(risk_id):
        raise HTTPException(404, "Risk not found")


@app.post("/api/risks/{risk_id}/analyze", response_model=Risk)
def analyze(risk_id: int) -> dict:
    item = get_risk(risk_id)
    if not item:
        raise HTTPException(404, "Risk not found")
    recommendation = analyze_risk(item)
    return update_recommendation(risk_id, recommendation)
