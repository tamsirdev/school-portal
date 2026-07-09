from datetime import datetime

from app import db


class RiskPrediction(db.Model):
    __tablename__ = "risk_predictions"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    term = db.Column(db.Integer, nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False, default="low")
    top_factors = db.Column(db.JSON, nullable=True)
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    student = db.relationship("User", backref="risk_predictions", foreign_keys=[student_id])

    __table_args__ = (
        db.UniqueConstraint("student_id", "term", name="uq_risk"),
    )

    def __repr__(self):
        return f"<Risk {self.student_id} T{self.term}: {self.risk_level} ({self.risk_score:.2f})>"
