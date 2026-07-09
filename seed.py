"""Seed the database with demo data for development."""

import random
from datetime import date, timedelta

from app import create_app, db
from app.models.attendance import Attendance
from app.models.class_ import Class
from app.models.score import Score
from app.models.subject import Subject
from app.models.user import User

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # ── Users ──────────────────────────────────────────────────────────
    admin = User(email="admin@school.gov", full_name="Admin Sillah", role="admin")
    admin.set_password("admin123")

    teacher = User(email="teacher@school.gov", full_name="Mr. Jallow", role="teacher")
    teacher.set_password("teacher123")

    students = []
    names = [
        "Fatou Sillah", "Musa Bah", "Aminata Ceesay", "Buba Jallow",
        "Isatou Njie", "Momodou Saidy", "Kaddy Faal", "Ebou Camara",
        "Ramatou Sissoho", "Lamin Jammeh",
    ]
    for name in names:
        email = f"{name.lower().replace(' ', '.')}@student.school.gov"
        s = User(email=email, full_name=name, role="student")
        s.set_password("student123")
        students.append(s)

    parent = User(
        email="parent@school.gov", full_name="Fatima Sillah",
        role="parent", parent_id=students[0].id,
    )
    parent.set_password("parent123")

    for u in [admin, teacher, parent] + students:
        db.session.add(u)
    db.session.commit()

    # ── Classes & Subjects ─────────────────────────────────────────────
    class_ = Class(name="Grade 10A", academic_year="2025/2026", teacher_id=teacher.id)
    db.session.add(class_)
    db.session.commit()

    subjects = []
    for subj in ["Mathematics", "English", "Science", "History", "ICT"]:
        s = Subject(name=subj, class_id=class_.id)
        db.session.add(s)
        subjects.append(s)
    db.session.commit()

    # ── Attendance (60 days) ───────────────────────────────────────────
    today = date.today()
    for student in students:
        for day_offset in range(60):
            d = today - timedelta(days=day_offset)
            if d.weekday() >= 5:
                continue
            status = random.choices(
                ["present", "absent", "excused"],
                weights=[80, 15, 5],
            )[0]
            db.session.add(
                Attendance(student_id=student.id, class_id=class_.id, date=d, status=status)
            )
    db.session.commit()

    # ── Scores ─────────────────────────────────────────────────────────
    for student in students:
        for subject in subjects:
            for term in [1, 2, 3]:
                for exam_type in ["midterm", "final", "assignment"]:
                    base = random.uniform(30, 95)
                    score = max(0, min(100, base + random.gauss(0, 10)))
                    db.session.add(
                        Score(
                            student_id=student.id,
                            subject_id=subject.id,
                            term=term,
                            exam_type=exam_type,
                            score=round(score, 1),
                            max_score=100.0,
                        )
                    )
    db.session.commit()

    print("Database seeded!")
    print("  Admin:    admin@school.gov / admin123")
    print("  Teacher:  teacher@school.gov / teacher123")
    print(f"  Student:  {students[0].email} / student123")
    print("  Parent:   parent@school.gov / parent123")
    print(f"  Classes:  {class_.name}")
    print(f"  Subjects: {', '.join(s.name for s in subjects)}")
    print(f"  Students: {len(students)}")
