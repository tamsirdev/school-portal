from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import func

from app.models.attendance import Attendance
from app.models.score import Score
from app.models.subject import Subject
from app.models.user import User

reports_bp = Blueprint(
    "reports", __name__, url_prefix="/reports",
    template_folder="../templates/reports",
)


@reports_bp.route("/<int:student_id>")
@login_required
def student_report(student_id):
    user = User.query.get_or_404(student_id)

    if current_user.is_student() and current_user.id != student_id:
        return "Forbidden", 403
    if current_user.is_parent() and current_user.id != user.parent_id:
        return "Forbidden", 403

    subjects = Subject.query.all()
    terms = [1, 2, 3]

    report_data = []
    for subject in subjects:
        row = {"subject": subject.name}
        for term in terms:
            scores = (
                Score.query.filter_by(student_id=student_id, subject_id=subject.id, term=term)
                .with_entities(func.avg(Score.score).label("avg"))
                .first()
            )
            row[term] = round(scores.avg, 1) if scores.avg else None
        report_data.append(row)

    total_days = Attendance.query.filter_by(student_id=student_id).count()
    present_days = Attendance.query.filter_by(student_id=student_id, status="present").count()
    attendance_rate = round((present_days / total_days * 100), 1) if total_days else 0

    return render_template(
        "report.html",
        student=user,
        report_data=report_data,
        terms=terms,
        attendance_rate=attendance_rate,
    )
