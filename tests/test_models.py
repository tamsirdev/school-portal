def test_create_user(db, seeded_db):
    from app import db as _db
    from app.models.user import User

    u = User(email="new@test.gov", full_name="New User", role="student")
    u.set_password("test123")
    _db.session.add(u)
    _db.session.commit()

    assert u.id is not None
    assert u.check_password("test123") is True
    assert u.check_password("wrong") is False
    assert u.is_student() is True
    assert u.is_admin() is False


def test_score_grade(db, seeded_db):
    from app.models.score import Score

    s = Score(student_id=seeded_db["student"].id, subject_id=seeded_db["subject"].id,
              term=1, exam_type="midterm", score=85, max_score=100)
    assert s.percentage() == 85.0
    assert s.grade() == "A"

    s.score = 45
    assert s.grade() == "F"
