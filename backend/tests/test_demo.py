from app.models import Case

def test_demo_load_idempotency(client, db_session):
    # First load
    res1 = client.post("/api/demo/load")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["loaded_count"] == 44
    assert data1["skipped_count"] == 0

    count_after_first = db_session.query(Case).filter(Case.is_demo == True).count()
    assert count_after_first == 44

    # Second load (must be idempotent: no duplicates!)
    res2 = client.post("/api/demo/load")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["loaded_count"] == 0
    assert data2["skipped_count"] == 44

    count_after_second = db_session.query(Case).filter(Case.is_demo == True).count()
    assert count_after_second == 44

def test_demo_clear_requires_confirmation(client):
    res = client.post("/api/demo/clear", json={"confirm": False})
    assert res.status_code == 400
    assert "confirmation required" in res.json()["detail"].lower()

def test_demo_clear_deletes_only_demo_records(client, db_session):
    # Ensure demo data is loaded
    client.post("/api/demo/load")

    # Insert a real non-demo case
    real_case_res = client.post("/api/analyze/message", json={
        "content": "Alert: Your parcel order #123 is waiting. Call 9000000025",
        "subject": "Real Investigation Case"
    })
    assert real_case_res.status_code == 200
    real_case_id = real_case_res.json()["case_id"]

    # Verify counts
    demo_count = db_session.query(Case).filter(Case.is_demo == True).count()
    real_count = db_session.query(Case).filter(Case.is_demo == False).count()
    assert demo_count == 44
    assert real_count >= 1

    # Clear demo data
    clear_res = client.post("/api/demo/clear", json={"confirm": True})
    assert clear_res.status_code == 200
    assert clear_res.json()["cleared_cases"] == 44

    # Verify that demo cases are 0, but real case remains intact
    demo_after = db_session.query(Case).filter(Case.is_demo == True).count()
    real_after = db_session.query(Case).filter(Case.is_demo == False).count()
    assert demo_after == 0
    assert real_after >= 1

    # Real case can still be retrieved
    check_real = client.get(f"/api/cases/{real_case_id}")
    assert check_real.status_code == 200
    assert check_real.json()["is_demo"] is False
