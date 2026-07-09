from datetime import date

from app import db


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(
        db.String(20), nullable=False, default="present"
    )

    student = db.relationship("User", backref="attendance_records", foreign_keys=[student_id])

    __table_args__ = (
        db.UniqueConstraint("student_id", "class_id", "date", name="uq_attendance"),
    )

    def __repr__(self):
        return f"<Attendance {self.student_id} on {self.date}: {self.status}>"
