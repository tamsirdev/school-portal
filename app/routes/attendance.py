from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app import db
from app.models.attendance import Attendance
from app.models.class_ import Class
from app.models.user import User
from app.routes.decorators import teacher_or_admin_required

attendance_bp = Blueprint(
    "attendance", __name__, url_prefix="/attendance", template_folder="../templates/attendance"
)


@attendance_bp.route("/<int:class_id>", methods=["GET", "POST"])
@login_required
@teacher_or_admin_required
def class_attendance(class_id):
    class_ = Class.query.get_or_404(class_id)
    students = User.query.filter_by(role="student").all()

    if request.method == "POST":
        attn_date = request.form.get("date", str(date.today()))
        for student in students:
            status = request.form.get(f"status_{student.id}", "absent")
            existing = Attendance.query.filter_by(
                student_id=student.id, class_id=class_id, date=attn_date
            ).first()
            if existing:
                existing.status = status
            else:
                db.session.add(
                    Attendance(
                        student_id=student.id, class_id=class_id, date=attn_date, status=status
                    )
                )
        db.session.commit()
        flash("Attendance saved.", "success")
        return redirect(url_for("attendance.class_attendance", class_id=class_id))

    attn_date = request.args.get("date", str(date.today()))
    records = {
        r.student_id: r
        for r in Attendance.query.filter_by(class_id=class_id, date=attn_date).all()
    }
    return render_template(
        "attendance.html", class_=class_, students=students, records=records, date=attn_date
    )
