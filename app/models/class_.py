from app import db


class Class(db.Model):
    __tablename__ = "classes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    teacher = db.relationship("User", backref="classes_taught", foreign_keys=[teacher_id])
    subjects = db.relationship("Subject", backref="class_", lazy="dynamic")
    attendances = db.relationship("Attendance", backref="class_", lazy="dynamic")

    def __repr__(self):
        return f"<Class {self.name} ({self.academic_year})>"
