import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.models import User
from app.auth import hash_password, create_access_token
from app.database import get_db

@pytest.fixture
def auth_test_client(db_session):
    """Clean TestClient with NO auth dependency overrides."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()

def test_registration_success(auth_test_client):
    payload = {
        "username": "new_citizen_user",
        "password": "StrongPassword123!",
        "display_name": "Ramesh Kumar"
    }
    res = auth_test_client.post("/api/auth/register", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "new_citizen_user"
    assert data["user"]["role"] == "citizen"
    assert "access_token" in res.cookies

def test_registration_duplicate_username(auth_test_client):
    payload = {
        "username": "duplicate_user",
        "password": "StrongPassword123!",
        "display_name": "First User"
    }
    res1 = auth_test_client.post("/api/auth/register", json=payload)
    assert res1.status_code == 200

    # Second attempt with same username
    res2 = auth_test_client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already registered" in res2.json()["detail"].lower()

def test_registration_short_password(auth_test_client):
    payload = {
        "username": "short_pwd_user",
        "password": "123",  # < 8 chars
        "display_name": "Test"
    }
    res = auth_test_client.post("/api/auth/register", json=payload)
    assert res.status_code in (400, 422)

def test_registration_role_elevation_prevented(auth_test_client):
    # Even if an attacker supplies role="officer" in the payload, server forces "citizen"
    payload = {
        "username": "hacker_wannabe",
        "password": "Password12345!",
        "display_name": "Fake Officer",
        "role": "officer"
    }
    res = auth_test_client.post("/api/auth/register", json=payload)
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "citizen"

def test_login_success(auth_test_client, db_session):
    # Seed a user
    user = User(
        id="test-user-uuid-1",
        username="login_test_user",
        display_name="Test Citizen",
        password_hash=hash_password("ValidPassword99!"),
        role="citizen",
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()

    res = auth_test_client.post("/api/auth/login", json={
        "username": "login_test_user",
        "password": "ValidPassword99!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["username"] == "login_test_user"
    assert "access_token" in res.cookies

def test_login_invalid_password(auth_test_client, db_session):
    user = User(
        id="test-user-uuid-2",
        username="wrong_pwd_user",
        display_name="Test User",
        password_hash=hash_password("CorrectPassword123!"),
        role="citizen",
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()

    res = auth_test_client.post("/api/auth/login", json={
        "username": "wrong_pwd_user",
        "password": "WrongPassword999!"
    })
    assert res.status_code == 400
    assert "invalid username or password" in res.json()["detail"].lower()

def test_account_lockout_after_5_failures(auth_test_client, db_session):
    user = User(
        id="test-user-uuid-3",
        username="lockout_user",
        display_name="Lockout Target",
        password_hash=hash_password("CorrectPassword123!"),
        role="citizen",
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()

    # Fail 4 times
    for i in range(4):
        res = auth_test_client.post("/api/auth/login", json={
            "username": "lockout_user",
            "password": f"BadPassword{i}"
        })
        assert res.status_code == 400
        assert "invalid username or password" in res.json()["detail"].lower()

    # 5th failure triggers lock
    res5 = auth_test_client.post("/api/auth/login", json={
        "username": "lockout_user",
        "password": "BadPassword5"
    })
    assert res5.status_code == 400

    # 6th attempt even with correct password is locked
    res6 = auth_test_client.post("/api/auth/login", json={
        "username": "lockout_user",
        "password": "CorrectPassword123!"
    })
    assert res6.status_code == 400
    assert "locked" in res6.json()["detail"].lower()

def test_unauthenticated_access_rejected(auth_test_client):
    # Unauthenticated officer endpoints return 401
    assert auth_test_client.get("/api/dashboard/stats").status_code == 401
    assert auth_test_client.get("/api/cases").status_code == 401
    assert auth_test_client.get("/api/intelligence/graph").status_code == 401
    assert auth_test_client.get("/api/intelligence/heatlist").status_code == 401
    assert auth_test_client.post("/api/analyze/message", json={"content": "test"}).status_code == 401
    assert auth_test_client.get("/api/auth/me").status_code == 401

def test_citizen_access_and_data_isolation(auth_test_client, db_session):
    # Register citizen
    reg_res = auth_test_client.post("/api/auth/register", json={
        "username": "citizen_sam",
        "password": "SamPassword123!",
        "display_name": "Sam Citizen"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Citizen can access /api/auth/me
    me_res = auth_test_client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["role"] == "citizen"

    # Citizen can access /api/public/awareness
    aware_res = auth_test_client.get("/api/public/awareness", headers=headers)
    assert aware_res.status_code == 200
    data = aware_res.json()
    assert "total_cases" in data
    assert "categories" in data
    assert "safety_advisory" in data

    # Citizen can analyze messages
    msg_res = auth_test_client.post("/api/analyze/message", headers=headers, json={
        "content": "Urgent: Your SBI account is suspended! Update at http://demo-scam.test/kyc",
        "subject": "Citizen Report"
    })
    assert msg_res.status_code == 200
    res_data = msg_res.json()
    assert res_data["risk_level"] == "HIGH"
    # IMPORTANT: Citizen must NOT see other cases' similarity matches (data isolation)
    assert res_data["similarity_matches"] == []

    # Citizen is FORBIDDEN from officer intelligence workspaces
    assert auth_test_client.get("/api/dashboard/stats", headers=headers).status_code == 403
    assert auth_test_client.get("/api/cases", headers=headers).status_code == 403
    assert auth_test_client.get("/api/intelligence/graph", headers=headers).status_code == 403
    assert auth_test_client.get("/api/intelligence/heatlist", headers=headers).status_code == 403
    assert auth_test_client.post("/api/assistant/ask", headers=headers, json={"question": "stats"}).status_code == 403
    assert auth_test_client.post("/api/demo/load", headers=headers).status_code == 403

def test_officer_full_access(auth_test_client, db_session):
    officer = User(
        id="officer-uuid-super",
        username="officer_rajesh",
        display_name="Inspector Rajesh",
        password_hash=hash_password("SuperSecretOfficerPassword!"),
        role="officer",
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(officer)
    db_session.commit()

    # Login as officer
    login_res = auth_test_client.post("/api/auth/login", json={
        "username": "officer_rajesh",
        "password": "SuperSecretOfficerPassword!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Officer can access all workspaces
    assert auth_test_client.get("/api/dashboard/stats", headers=headers).status_code == 200
    assert auth_test_client.get("/api/cases", headers=headers).status_code == 200
    assert auth_test_client.get("/api/intelligence/graph", headers=headers).status_code == 200
    assert auth_test_client.get("/api/intelligence/heatlist", headers=headers).status_code == 200
    assert auth_test_client.get("/api/public/awareness", headers=headers).status_code == 200

def test_logout(auth_test_client):
    res = auth_test_client.post("/api/auth/logout")
    assert res.status_code == 200
    assert res.json()["status"] == "success"
