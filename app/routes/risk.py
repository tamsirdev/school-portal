from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.models.class_ import Class
from app.models.risk import RiskPrediction
from app.models.user import User
from app.routes.decorators import teacher_or_admin_required
from app.services.risk_predictor import predict_class_risk

risk_bp = Blueprint("risk", __name__, url_prefix="/risk", template_folder="../templates/risk")


@risk_bp.route("/class/<int:class_id>", methods=["GET", "POST"])
@login_required
@teacher_or_admin_required
def class_risk(class_id):
    class_ = Class.query.get_or_404(class_id)

    if request.method == "POST":
        term = int(request.form.get("term", 1))
        students = User.query.filter_by(role="student").all()
        results = predict_class_risk(students, term)
        for student_id, risk_score, risk_level, factors in results:
            existing = RiskPrediction.query.filter_by(
                student_id=student_id, term=term
            ).first()
            if existing:
                existing.risk_score = risk_score
                existing.risk_level = risk_level
                existing.top_factors = factors
            else:
                from app import db
                db.session.add(
                    RiskPrediction(
                        student_id=student_id,
                        term=term,
                        risk_score=risk_score,
                        risk_level=risk_level,
                        top_factors=factors,
                    )
                )
        from app import db
        db.session.commit()
        flash("Risk analysis complete.", "success")
        return redirect(url_for("risk.class_risk", class_id=class_id))

    term = int(request.args.get("term", 1))
    predictions = RiskPrediction.query.all()
    return render_template(
        "class_risk.html", class_=class_, predictions=predictions, term=term
    )
