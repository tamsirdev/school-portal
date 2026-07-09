from app.models.user import User
from app.services.celery_app import celery_app
from app.services.risk_predictor import predict_class_risk


@celery_app.task
def run_risk_analysis(term=1):
    students = User.query.filter_by(role="student").all()
    results = predict_class_risk(students, term)

    from app import db
    from app.models.risk import RiskPrediction

    for student_id, risk_score, risk_level, factors in results:
        existing = RiskPrediction.query.filter_by(
            student_id=student_id, term=term
        ).first()
        if existing:
            existing.risk_score = risk_score
            existing.risk_level = risk_level
            existing.top_factors = factors
        else:
            db.session.add(
                RiskPrediction(
                    student_id=student_id,
                    term=term,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    top_factors=factors,
                )
            )
    db.session.commit()
    return f"Risk analysis complete for {len(results)} students"
