from app import db


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), nullable=False)

    scores = db.relationship("Score", backref="subject", lazy="dynamic")

    def __repr__(self):
        return f"<Subject {self.name}>"
