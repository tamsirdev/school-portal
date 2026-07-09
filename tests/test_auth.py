def test_login_page(client):
    r = client.get("/auth/login")
    assert r.status_code == 200
    assert b"Sign In" in r.data


def test_login_success(client, seeded_db):
    r = client.post("/auth/login", data={
        "email": "admin@test.gov", "password": "admin123"
    }, follow_redirects=True)
    assert r.status_code == 200


def test_login_failure(client, seeded_db):
    r = client.post("/auth/login", data={
        "email": "admin@test.gov", "password": "wrong"
    }, follow_redirects=True)
    assert b"Invalid" in r.data


def test_logout(client, seeded_db):
    client.post("/auth/login", data={
        "email": "admin@test.gov", "password": "admin123"
    })
    r = client.get("/auth/logout", follow_redirects=True)
    assert b"Sign In" in r.data


def test_protected_redirects(client):
    r = client.get("/", follow_redirects=True)
    assert b"Sign In" in r.data
