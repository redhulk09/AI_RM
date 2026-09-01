# AI Risk Manager (AI_RM)

A lightweight, runnable Risk Manager MVP built with FastAPI and SQLite. It provides a small REST API and browser UI for creating, scoring, reviewing, and monitoring project/business risks.

> **Note:** The shared ChatGPT conversation linked for this project was not machine-readable from the available access path, so this implementation is a best-effort MVP based on the repository name and the visible conversation title, **"Build Risk Manager MVP Prompt"**. The project is intentionally modular so a more specific workflow or AI provider can be plugged in without rewriting the core risk engine.

## Features

- Create, list, retrieve, and delete risks.
- Deterministic risk scoring from likelihood × impact.
- Automatic priority bands: Low, Medium, High, Critical.
- Optional control effectiveness adjustment.
- AI-assisted recommendations using a deterministic local analyzer (no API key required).
- SQLite persistence with a small, dependency-light codebase.
- Browser dashboard served directly by FastAPI.
- Automated tests for the core risk engine.

## Project structure

```text
AI_RM/
├── app/
│   ├── __init__.py
│   ├── ai.py
│   ├── main.py
│   ├── models.py
│   ├── risk_engine.py
│   └── storage.py
├── static/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── tests/
│   └── test_risk_engine.py
├── .env.example
├── .gitignore
├── Dockerfile
├── LICENSE
├── README.md
└── requirements.txt
```

## Run locally

### 1. Create an environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the API

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 for the dashboard or http://127.0.0.1:8000/docs for Swagger UI.

The database defaults to `risk_manager.db`. Override it with `RISK_MANAGER_DB`.

## API examples

Create a risk:

```bash
curl -X POST http://127.0.0.1:8000/api/risks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Third-party API outage",
    "description": "A critical vendor API could become unavailable.",
    "category": "Technology",
    "owner": "Platform Team",
    "likelihood": 4,
    "impact": 5,
    "control_effectiveness": 40
  }'
```

Analyze a risk:

```bash
curl -X POST http://127.0.0.1:8000/api/risks/1/analyze
```

## Risk scoring

The default score is:

```text
base score = likelihood × impact
adjusted score = round(base score × (1 - control_effectiveness / 100))
```

Severity is derived from the adjusted score:

- 1–4: Low
- 5–9: Medium
- 10–16: High
- 17–25: Critical

Likelihood and impact are integers from 1 to 5. Control effectiveness is a percentage from 0 to 100.

## Testing

```bash
pytest -q
```

## Extending the MVP

The `app/ai.py` module exposes a small analyzer boundary. A hosted LLM provider, local model, retrieval system, or organization-specific policy engine can replace the deterministic analyzer while the API and storage layers remain stable.
