import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app
from app import db as _db


@pytest.fixture(scope="function")
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "testing"  # noqa: S105

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db


@pytest.fixture
def seeded_db(app, db):
    from app.models.class_ import Class
    from app.models.subject import Subject
    from app.models.user import User

    admin = User(email="admin@test.gov", full_name="Admin", role="admin")
    admin.set_password("admin123")
    teacher = User(email="teacher@test.gov", full_name="Teacher", role="teacher")
    teacher.set_password("teacher123")
    student = User(email="student@test.gov", full_name="Student", role="student")
    student.set_password("student123")

    for u in [admin, teacher, student]:
        db.session.add(u)
    db.session.commit()

    class_ = Class(name="Test Class", academic_year="2025", teacher_id=teacher.id)
    db.session.add(class_)
    db.session.commit()

    subject = Subject(name="Math", class_id=class_.id)
    db.session.add(subject)
    db.session.commit()

    yield {
        "admin": admin,
        "teacher": teacher,
        "student": student,
        "class_": class_,
        "subject": subject,
    }
