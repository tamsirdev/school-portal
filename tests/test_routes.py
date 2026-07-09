def login(client, email, password):
    return client.post("/auth/login", data={
        "email": email, "password": password
    }, follow_redirects=True)


def test_admin_dashboard(client, seeded_db):
    login(client, "admin@test.gov", "admin123")
    r = client.get("/")
    assert r.status_code == 200


def test_admin_list_users(client, seeded_db):
    login(client, "admin@test.gov", "admin123")
    r = client.get("/admin/users")
    assert r.status_code == 200
    assert b"Admin" in r.data


def test_teacher_cannot_access_admin_users(client, seeded_db):
    login(client, "teacher@test.gov", "teacher123")
    r = client.get("/admin/users")
    assert r.status_code == 403


def test_student_cannot_access_admin(client, seeded_db):
    login(client, "student@test.gov", "student123")
    r = client.get("/admin/users")
    assert r.status_code == 403


def test_teacher_dashboard(client, seeded_db):
    login(client, "teacher@test.gov", "teacher123")
    r = client.get("/")
    assert r.status_code == 200
    assert b"Test Class" in r.data


def test_attendance_page(client, seeded_db):
    login(client, "teacher@test.gov", "teacher123")
    r = client.get(f"/attendance/{seeded_db['class_'].id}")
    assert r.status_code == 200
    assert b"Student" in r.data


def test_scores_page(client, seeded_db):
    login(client, "teacher@test.gov", "teacher123")
    r = client.get(f"/scores/{seeded_db['class_'].id}/{seeded_db['subject'].id}")
    assert r.status_code == 200
    assert b"Score" in r.data
