from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app import db
from app.models.class_ import Class
from app.models.score import Score
from app.models.subject import Subject
from app.models.user import User
from app.routes.decorators import teacher_or_admin_required

scores_bp = Blueprint(
    "scores", __name__, url_prefix="/scores",
    template_folder="../templates/scores",
)


@scores_bp.route("/<int:class_id>/<int:subject_id>", methods=["GET", "POST"])
@login_required
@teacher_or_admin_required
def manage_scores(class_id, subject_id):
    class_ = Class.query.get_or_404(class_id)
    subject = Subject.query.get_or_404(subject_id)
    students = User.query.filter_by(role="student").all()

    if request.method == "POST":
        term = int(request.form.get("term", 1))
        exam_type = request.form.get("exam_type", "midterm")
        for student in students:
            score_val = request.form.get(f"score_{student.id}")
            if score_val is None or score_val.strip() == "":
                continue
            existing = Score.query.filter_by(
                student_id=student.id, subject_id=subject_id, term=term, exam_type=exam_type
            ).first()
            if existing:
                existing.score = float(score_val)
            else:
                db.session.add(
                    Score(
                        student_id=student.id,
                        subject_id=subject_id,
                        term=term,
                        exam_type=exam_type,
                        score=float(score_val),
                        max_score=100.0,
                    )
                )
        db.session.commit()
        flash("Scores saved.", "success")
        return redirect(url_for("scores.manage_scores", class_id=class_id, subject_id=subject_id))

    term = int(request.args.get("term", 1))
    exam_type = request.args.get("exam_type", "midterm")
    records = {
        r.student_id: r
        for r in Score.query.filter_by(
            subject_id=subject_id, term=term, exam_type=exam_type
        ).all()
    }
    return render_template(
        "scores.html",
        class_=class_,
        subject=subject,
        students=students,
        records=records,
        term=term,
        exam_type=exam_type,
    )
