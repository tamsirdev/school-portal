from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    parent_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    parent = db.relationship("User", remote_side=[id], backref="children")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == "admin"

    def is_teacher(self):
        return self.role == "teacher"

    def is_student(self):
        return self.role == "student"

    def is_parent(self):
        return self.role == "parent"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
