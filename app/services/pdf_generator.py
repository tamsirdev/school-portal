from flask import render_template
from weasyprint import HTML


def generate_report_card(student_id):
    from app import create_app
    app = create_app()

    with app.app_context():
        from sqlalchemy import func

        from app.models.attendance import Attendance
        from app.models.score import Score
        from app.models.subject import Subject
        from app.models.user import User

        student = User.query.get_or_404(student_id)
        subjects = Subject.query.all()
        terms = [1, 2, 3]

        report_data = []
        for subject in subjects:
            row = {"subject": subject.name}
            for term in terms:
                scores = (
                    Score.query.filter_by(
                        student_id=student_id, subject_id=subject.id, term=term
                    )
                    .with_entities(func.avg(Score.score).label("avg"))
                    .first()
                )
                row[term] = round(scores.avg, 1) if scores.avg else "-"
            report_data.append(row)

        total = Attendance.query.filter_by(student_id=student_id).count()
        present = Attendance.query.filter_by(
            student_id=student_id, status="present"
        ).count()
        att_rate = round((present / total * 100), 1) if total else 0

        html = render_template(
            "report_card_pdf.html",
            student=student,
            report_data=report_data,
            terms=terms,
            attendance_rate=att_rate,
        )
        return HTML(string=html).write_pdf()
