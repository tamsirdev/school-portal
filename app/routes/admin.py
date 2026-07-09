from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app import db
from app.models.class_ import Class
from app.models.user import User
from app.routes.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="../templates/admin")


@admin_bp.route("/users")
@login_required
@admin_required
def list_users():
    users = User.query.all()
    return render_template("users.html", users=users)


@admin_bp.route("/users/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "error")
            return render_template("user_form.html")
        user = User(
            email=email,
            full_name=request.form.get("full_name", "").strip(),
            role=request.form.get("role", "student"),
        )
        user.set_password(request.form.get("password", "changeme123"))
        db.session.add(user)
        db.session.commit()
        flash(f"User {user.full_name} created.", "success")
        return redirect(url_for("admin.list_users"))
    return render_template("user_form.html")


@admin_bp.route("/classes")
@login_required
@admin_required
def list_classes():
    classes = Class.query.all()
    return render_template("classes.html", classes=classes)


@admin_bp.route("/classes/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_class():
    teachers = User.query.filter_by(role="teacher").all()
    if request.method == "POST":
        class_ = Class(
            name=request.form.get("name", "").strip(),
            academic_year=request.form.get("academic_year", "").strip(),
            teacher_id=request.form.get("teacher_id", type=int),
        )
        db.session.add(class_)
        db.session.commit()
        flash(f"Class {class_.name} created.", "success")
        return redirect(url_for("admin.list_classes"))
    return render_template("class_form.html", teachers=teachers)
