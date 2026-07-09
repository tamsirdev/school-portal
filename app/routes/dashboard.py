from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.models.attendance import Attendance
from app.models.class_ import Class
from app.models.score import Score
from app.models.user import User

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    user = current_user

    if user.is_admin():
        students = User.query.filter_by(role="student").count()
        teachers = User.query.filter_by(role="teacher").count()
        classes = Class.query.count()
        return render_template(
            "dashboard/admin.html", students=students, teachers=teachers, classes=classes
        )

    if user.is_teacher():
        classes = Class.query.filter_by(teacher_id=user.id).all()
        return render_template("dashboard/teacher.html", classes=classes)

    if user.is_student() or user.is_parent():
        student_id = user.id if user.is_student() else user.parent_id
        scores = Score.query.filter_by(student_id=student_id).all()
        attendance = Attendance.query.filter_by(student_id=student_id).count()
        present = Attendance.query.filter_by(student_id=student_id, status="present").count()
        attendance_rate = round((present / attendance * 100), 1) if attendance else 0
        return render_template(
            "dashboard/student.html",
            scores=scores,
            attendance_rate=attendance_rate,
        )

    return render_template("dashboard/index.html")
