# RiskLens

**AI Risk Manager — stop the merchant losing money to fraud, returns and chargebacks.**

RiskLens is a **defense-only** transaction risk intelligence platform for merchants. It validates a payment, engineers behavioral features, runs a real scikit-learn model, returns a 0–100 risk score with human-readable reasons, stores the decision, and surfaces aggregate risk and model performance in a premium Next.js dashboard.

All demo customer IDs, transactions, and fraud labels are synthetic. **All demo data is synthetic and metrics are not representative of production performance.**

## 1. Problem

Merchants need to make faster payment decisions while balancing two expensive failure modes: false positives create customer friction and lost conversion; false negatives let fraud pass through and create direct loss.

RiskLens turns transaction signals into a review queue rather than silently rejecting payments.

## 2. Solution

The product flow is:

```text
Merchant transaction
        ↓
Validation
        ↓
Feature engineering
        ↓
ML model probability
        ↓
0–100 risk score
        ↓
LOW / MEDIUM / HIGH
        ↓
Human-readable reasons
        ↓
Merchant review decision
        ↓
SQLite + dashboard aggregates
```

## 3. Architecture

```text
Next.js + React + TypeScript + Tailwind
                ↓
             FastAPI
                ↓
          Risk Engine / API
                ↓
        scikit-learn Pipeline
                ↓
             SQLite
```

The database layer uses SQLAlchemy so the persistence boundary can later move to PostgreSQL with minimal application changes.

## 4. Project structure

```text
risklens/
├── backend/
│   ├── api/routes.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── main.py
│   ├── ml/
│   │   ├── dataset.py
│   │   ├── features.py
│   │   ├── train.py
│   │   ├── predict.py
│   │   ├── evaluate.py
│   │   └── explain.py
│   ├── services/
│   │   ├── metrics_service.py
│   │   └── transaction_service.py
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── analyze/page.tsx
│   │   ├── transactions/page.tsx
│   │   ├── transactions/[id]/page.tsx
│   │   └── model/page.tsx
│   ├── components/
│   └── lib/api.ts
├── data/transactions.csv
├── scripts/
│   ├── generate_data.py
│   ├── train_model.py
│   └── seed_demo.py
├── tests/
│   ├── test_api.py
│   └── test_model.py
├── docker-compose.yml
└── README.md
```

## 5. ML methodology

RiskLens generates a synthetic transaction population with meaningful behavioral relationships instead of assigning fraud completely at random. Fraud likelihood increases with combinations such as high velocity, abnormal amount deviation, new device, new location, multiple recent failures, and suspicious shared-device/IP activity.

The training pipeline uses three stratified partitions:

- **60% train** — model fitting.
- **20% validation** — baseline/final model selection by ROC-AUC.
- **20% test** — completely held out until final reporting.

The test set is not used for tuning or selecting the final model.

### Baseline

Logistic Regression with a shared preprocessing pipeline.

### Final candidate

Random Forest with balanced classes and conservative depth/leaf constraints for fast hackathon inference.

The pipeline selects the better candidate by validation ROC-AUC, refits that selected model on train + validation, then evaluates once on test.

## 6. Dataset

`data/transactions.csv` is a small committed synthetic sample for inspection. `scripts/generate_data.py` can generate the larger demo dataset automatically.

Features include:

`transaction_id`, `amount`, `account_age_days`, `transactions_last_10m`, `transactions_last_1h`, `failed_payments`, `previous_avg_amount`, `amount_deviation`, `is_new_device`, `is_new_location`, `distance_from_previous_location`, `device_transaction_count`, `ip_transaction_count`, `payment_method`, `hour`, `country`, `customer_transaction_count`, `is_fraud`.

## 7. Feature engineering

Numeric inputs are passed through a shared preprocessing definition. Categorical country/payment-method values use one-hot encoding with unknown-category handling.

For live prediction, `amount_deviation` is derived from amount / previous average amount when it is not explicitly supplied.

## 8. Risk score and explainability

The model probability is converted to a product score:

```text
risk_score = round(fraud_probability × 100)

0–39  LOW
40–69 MEDIUM
70–100 HIGH
```

The response includes `fraud_probability`, `risk_score`, `risk_level`, `reasons`, `top_features`, and a recommended review action.

Explanations translate feature importance into merchant language, for example:

- `amount_deviation` → Transaction amount is significantly above the customer's normal behavior.
- `transactions_last_10m` → Unusually high transaction velocity detected in the last 10 minutes.
- `is_new_device` → Transaction originated from a new device.
- `failed_payments` → Multiple recent payment failures detected.

These are decision-support explanations, not proof of fraud.

## 9. Evaluation methodology

The model page exposes the actual calculated held-out metrics:

- test set size
- fraud prevalence
- precision
- recall
- F1
- ROC-AUC
- false-positive rate
- confusion matrix
- model feature importance
- threshold curve

It also compares the validation ROC-AUC of the Logistic Regression baseline and Random Forest candidate.

### Threshold tradeoff

The product includes a configurable review threshold. Lower thresholds generally increase recall while also increasing the number of legitimate payments sent for review. The UI shows precision, recall, and F1 across threshold values rather than pretending one cutoff is universally correct.

## 10. Business cost assumptions

The demo uses explicit configurable assumptions:

- **False-positive cost:** ₹100 per legitimate transaction flagged.
- **False-negative cost:** mean fraudulent transaction amount.
- **Estimated prevented loss:** fraudulent transaction amount × recall on the held-out test set, used only as a demo proxy.

The dashboard therefore labels the figure as an estimate rather than realized savings.

## 11. API documentation

FastAPI automatically exposes OpenAPI/Swagger at `/docs`.

Core endpoints:

```text
GET  /api/health
POST /api/predict
POST /api/batch-predict
GET  /api/metrics
GET  /api/dashboard
GET  /api/transactions
GET  /api/transactions/{id}
GET  /api/transactions/export
POST /api/train
POST /api/demo/seed
```

Single prediction example:

```json
{
  "amount": 42850,
  "currency": "INR",
  "customer_id": "DEMO_CUSTOMER",
  "account_age_days": 24,
  "device_id": "DEMO_DEVICE",
  "country": "IN",
  "transactions_last_10m": 8,
  "transactions_last_1h": 16,
  "failed_payments": 4,
  "previous_avg_amount": 10100,
  "is_new_device": true,
  "is_new_location": true,
  "distance_from_previous_location": 2100,
  "device_transaction_count": 15,
  "ip_transaction_count": 11,
  "customer_transaction_count": 18,
  "payment_method": "card",
  "hour": 2
}
```

Expected response shape:

```json
{
  "transaction_id": "TXN_...",
  "risk_score": 87,
  "risk_level": "HIGH",
  "fraud_probability": 0.87,
  "reasons": ["..."],
  "top_features": [{"feature": "...", "importance": 0.12, "signal": 3.2, "direction": "increases risk"}],
  "recommended_action": "Review transaction",
  "transaction": {"amount": 42850}
}
```

## 12. Demo instructions

### Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
cd ..
python scripts/generate_data.py
python scripts/train_model.py
python scripts/seed_demo.py
uvicorn backend.main:app --reload
```

Open `http://localhost:8000/docs` for the API.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

### One-click demo

Use **Load demo** on `/dashboard` to seed the memorable demo scenarios: normal transaction, high amount, velocity spike, new device, multiple failures, unusual location, and combined suspicious behavior.

### Docker

```bash
docker compose up --build
```

Frontend: `http://localhost:3000`  
Backend: `http://localhost:8000`

## 13. Limitations

This is a hackathon MVP using synthetic data, not a production fraud model. Real merchants need temporal validation, leakage controls, richer customer/device/IP histories, calibration, drift monitoring, investigation feedback loops, model governance, privacy/compliance controls, and production-grade authentication and authorization.

No payment credentials are accepted or stored. RiskLens does not store card numbers, CVVs, OTPs, secrets, or real customer identities.

## 14. Future improvements

Move persistence to PostgreSQL; add proper temporal cross-validation; calibrate probabilities; add merchant-specific cost curves; monitor data/model drift; use SHAP or a similarly governed explanation layer; add authenticated analyst workflows; add audit trails; and support model versions with reproducible artifacts.

## 15. Defense-only safety boundary

RiskLens is designed only to detect and review potentially fraudulent payments. It does **not** generate fraud, provide evasion tactics, bypass payment controls, steal credentials, manipulate identity, or optimize attacks.

## License

MIT. See [`LICENSE`](LICENSE).

## Current dependency notes

The current package pins/ranges were checked against public package indexes during the update. Generated model artifacts are intentionally created by `scripts/train_model.py` and ignored from source control because the GitHub file interface used for this build only supports UTF-8 text writes, while a real scikit-learn pickle is binary.
