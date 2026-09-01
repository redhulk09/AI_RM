import io

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def payload():
    return {"amount": 42850, "currency": "INR", "customer_id": "TEST_CUST_API", "account_age_days": 24, "device_id": "TEST_DEV_API", "country": "IN", "transactions_last_10m": 8, "transactions_last_1h": 16, "failed_payments": 4, "previous_transaction_amount": 10100, "previous_avg_amount": 10100, "is_new_device": True, "is_new_location": True, "distance_from_previous_location": 2100, "device_transaction_count": 15, "ip_transaction_count": 11, "customer_transaction_count": 18, "payment_method": "card", "hour": 2}


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_persists_transaction_and_prediction():
    transaction_id = "TEST_PERSISTED_API"
    body = payload() | {"transaction_id": transaction_id}
    response = client.post("/api/predict", json=body)
    assert response.status_code == 200
    result = response.json()
    assert result["transaction_id"] == transaction_id
    assert {"risk_score", "risk_level", "fraud_probability", "reasons", "recommended_action"}.issubset(result)
    assert 0 <= result["risk_score"] <= 100
    assert 0 <= result["fraud_probability"] <= 1
    detail = client.get(f"/api/transactions/{transaction_id}")
    assert detail.status_code == 200
    assert detail.json()["amount"] == body["amount"]


def test_batch_predict():
    csv_text = "transaction_id,amount,customer_id,account_age_days,device_id,country,transactions_last_10m,transactions_last_1h,failed_payments,previous_avg_amount,is_new_device,is_new_location,distance_from_previous_location,device_transaction_count,ip_transaction_count,payment_method,hour,customer_transaction_count\nTXN_BATCH_1,1200,C1,500,D1,IN,1,3,0,1100,0,0,10,2,1,upi,13,60\nTXN_BATCH_2,42000,C2,12,D2,US,9,18,3,8500,1,1,1800,14,10,card,2,12\n"
    response = client.post("/api/batch-predict", files={"file": ("demo.csv", io.BytesIO(csv_text.encode()), "text/csv")})
    assert response.status_code == 200
    body = response.json()
    assert body["valid_transactions"] == 2
    assert len(body["results"]) == 2


def test_batch_predict_skips_invalid_rows():
    csv_text = "transaction_id,amount,customer_id,account_age_days,device_id,country,transactions_last_10m,transactions_last_1h,failed_payments,previous_avg_amount,is_new_device,is_new_location,distance_from_previous_location,device_transaction_count,ip_transaction_count,payment_method,hour,customer_transaction_count\nGOOD,1200,C1,500,D1,IN,1,3,0,1100,0,0,10,2,1,upi,13,60\nBAD,-5,C2,12,D2,US,9,18,3,8500,1,1,1800,14,10,card,2,12\n"
    response = client.post("/api/batch-predict", files={"file": ("mixed.csv", io.BytesIO(csv_text.encode()), "text/csv")})
    assert response.status_code == 200
    body = response.json()
    assert body["rows_detected"] == 2
    assert body["valid_transactions"] == 1
    assert body["invalid_rows"] == 1


def test_batch_predict_rejects_malformed_binary_flags():
    csv_text = "transaction_id,amount,customer_id,account_age_days,device_id,country,transactions_last_10m,transactions_last_1h,failed_payments,previous_avg_amount,is_new_device,is_new_location,distance_from_previous_location,device_transaction_count,ip_transaction_count,payment_method,hour,customer_transaction_count\nBADFLAG,1200,C1,500,D1,IN,1,3,0,1100,2,0,10,2,1,upi,13,60\n"
    response = client.post("/api/batch-predict", files={"file": ("flags.csv", io.BytesIO(csv_text.encode()), "text/csv")})
    assert response.status_code == 422


def test_metrics_and_dashboard():
    metrics = client.get("/api/metrics")
    assert metrics.status_code == 200
    assert metrics.json().get("test_size", 0) >= 1000
    for threshold in (0.01, 0.5, 0.99):
        response = client.get("/api/metrics", params={"threshold": threshold})
        assert response.status_code == 200
        assert response.json()["threshold_curve"]
    dashboard = client.get("/api/dashboard")
    assert dashboard.status_code == 200
    assert dashboard.json()["transactions_analyzed"] >= 1


def test_invalid_transaction():
    bad = payload()
    bad["amount"] = 0
    response = client.post("/api/predict", json=bad)
    assert response.status_code == 422


def test_invalid_csv_and_size_limit():
    bad_type = client.post("/api/batch-predict", files={"file": ("demo.txt", io.BytesIO(b"x"), "text/plain")})
    assert bad_type.status_code == 400
    empty = client.post("/api/batch-predict", files={"file": ("empty.csv", io.BytesIO(b""), "text/csv")})
    assert empty.status_code == 400
    large = client.post("/api/batch-predict", files={"file": ("large.csv", io.BytesIO(b"x" * (5 * 1024 * 1024 + 1)), "text/csv")})
    assert large.status_code == 413


def test_transaction_not_found_and_export():
    missing = client.get("/api/transactions/DOES_NOT_EXIST")
    assert missing.status_code == 404
    export = client.get("/api/transactions/export")
    assert export.status_code == 200
    assert "text/csv" in export.headers["content-type"]


def test_demo_seed_is_idempotent():
    first = client.post("/api/demo/seed")
    second = client.post("/api/demo/seed")
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["seeded"] >= 0
    assert second.json()["seeded"] == 0
