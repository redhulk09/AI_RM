import io

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def payload():
    return {
        "amount": 42850,
        "currency": "INR",
        "customer_id": "TEST_CUST_API",
        "account_age_days": 24,
        "device_id": "TEST_DEV_API",
        "country": "IN",
        "transactions_last_10m": 8,
        "transactions_last_1h": 16,
        "failed_payments": 4,
        "previous_transaction_amount": 10100,
        "previous_avg_amount": 10100,
        "is_new_device": True,
        "is_new_location": True,
        "distance_from_previous_location": 2100,
        "device_transaction_count": 15,
        "ip_transaction_count": 11,
        "customer_transaction_count": 18,
        "payment_method": "card",
        "hour": 2,
    }


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict():
    response = client.post("/api/predict", json=payload())
    assert response.status_code == 200
    body = response.json()
    assert set(["risk_score", "risk_level", "fraud_probability", "reasons", "recommended_action"]).issubset(body)


def test_batch_predict():
    csv_text = "transaction_id,amount,customer_id,account_age_days,device_id,country,transactions_last_10m,transactions_last_1h,failed_payments,previous_avg_amount,is_new_device,is_new_location,distance_from_previous_location,device_transaction_count,ip_transaction_count,payment_method,hour,customer_transaction_count\nTXN_BATCH_1,1200,C1,500,D1,IN,1,3,0,1100,0,0,10,2,1,upi,13,60\nTXN_BATCH_2,42000,C2,12,D2,US,9,18,3,8500,1,1,1800,14,10,card,2,12\n"
    response = client.post("/api/batch-predict", files={"file": ("demo.csv", io.BytesIO(csv_text.encode()), "text/csv")})
    assert response.status_code == 200
    body = response.json()
    assert body["valid_transactions"] == 2
    assert len(body["results"]) == 2


def test_metrics_and_dashboard():
    metrics = client.get("/api/metrics")
    assert metrics.status_code == 200
    assert metrics.json().get("test_size", 0) > 0
    dashboard = client.get("/api/dashboard")
    assert dashboard.status_code == 200
    assert dashboard.json()["transactions_analyzed"] >= 1


def test_invalid_transaction():
    bad = payload()
    bad["amount"] = 0
    response = client.post("/api/predict", json=bad)
    assert response.status_code == 422
