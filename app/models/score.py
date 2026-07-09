from app import db


class Score(db.Model):
    __tablename__ = "scores"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    term = db.Column(db.Integer, nullable=False, default=1)
    exam_type = db.Column(db.String(30), nullable=False, default="midterm")
    score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False, default=100.0)

    student = db.relationship("User", backref="score_records", foreign_keys=[student_id])

    def percentage(self):
        return round((self.score / self.max_score) * 100, 1) if self.max_score else 0.0

    def grade(self):
        pct = self.percentage()
        if pct >= 80:
            return "A"
        elif pct >= 70:
            return "B"
        elif pct >= 60:
            return "C"
        elif pct >= 50:
            return "D"
        return "F"

    def __repr__(self):
        return f"<Score {self.student_id} {self.subject_id}: {self.score}/{self.max_score}>"
