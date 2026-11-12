from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from database import db
from database.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/admin")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash(
                "Please log in to access the administration dashboard. / நிர்வாக பக்கத்திற்கு உள்நுழையவும்.",
                "warning",
            )
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Admin registration endpoint so administrators can register their own account."""
    if session.get("user_id"):
        return redirect(url_for("admin.dashboard"))

    has_users = User.query.first() is not None

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Basic validations
        if not username or not email or not password or not confirm_password:
            flash(
                "Please fill in all required fields. / அனைத்து தேவையான தகவல்களையும் நிரப்பவும்.",
                "danger",
            )
        elif len(username) < 3:
            flash(
                "Username must be at least 3 characters long. / பயனர் பெயர் குறைந்தது 3 எழுத்துக்கள் இருக்க வேண்டும்.",
                "danger",
            )
        elif " " in username:
            flash(
                "Username cannot contain spaces. / பயனர் பெயரில் இடைவெளி இருக்கக்கூடாது.",
                "danger",
            )
        elif "@" not in email or "." not in email:
            flash(
                "Please enter a valid email address. / சரியான மின்னஞ்சல் முகவரியை உள்ளிடவும்.",
                "danger",
            )
        elif len(password) < 6:
            flash(
                "Password must be at least 6 characters long. / கடவுச்சொல் குறைந்தது 6 எழுத்துக்கள் இருக்க வேண்டும்.",
                "danger",
            )
        elif password != confirm_password:
            flash(
                "Passwords do not match. Please re-enter. / கடவுச்சொற்கள் பொருந்தவில்லை.",
                "danger",
            )
        else:
            # Check unique username
            existing_user = User.query.filter(User.username.ilike(username)).first()
            if existing_user:
                flash(
                    f'Username "{username}" is already taken. Please choose another. / இந்த பயனர் பெயர் ஏற்கனவே உள்ளது.',
                    "warning",
                )
                return render_template(
                    "admin/register.html", has_users=has_users, form_data=request.form
                )

            # Check unique email
            existing_email = User.query.filter(User.email.ilike(email)).first()
            if existing_email:
                flash(
                    f'Email "{email}" is already registered. Please log in or use another email. / இந்த மின்னஞ்சல் ஏற்கனவே உள்ளது.',
                    "warning",
                )
                return render_template(
                    "admin/register.html", has_users=has_users, form_data=request.form
                )

            # Create user
            new_user = User(
                username=username,
                email=email,
                full_name=full_name or username,
                role="admin",
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            # Set session
            session.permanent = True
            session["user_id"] = new_user.id
            session["username"] = new_user.username
            session["full_name"] = new_user.full_name
            session["role"] = new_user.role

            flash(
                f"Registration successful! Welcome to the Editorial Portal, {new_user.full_name}. / நிர்வாக கணக்கு வெற்றிகரமாக உருவாக்கப்பட்டது!",
                "success",
            )
            return redirect(url_for("admin.dashboard"))

    return render_template("admin/register.html", has_users=has_users)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # If admin is already authenticated, direct them straight to dashboard
    if session.get("user_id"):
        return redirect(url_for("admin.dashboard"))

    has_users = User.query.first() is not None

    if request.method == "POST":
        identifier = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Allow login by either username or email
        user = User.query.filter(
            (User.username.ilike(identifier)) | (User.email.ilike(identifier))
        ).first()

        if user and user.check_password(password):
            session.permanent = True
            session["user_id"] = user.id
            session["username"] = user.username
            session["full_name"] = user.full_name
            session["role"] = user.role
            flash(f"Welcome back, {user.full_name}! / நல்வரவு!", "success")

            next_page = request.args.get("next")
            if next_page and "/admin/login" not in next_page:
                if "://" in next_page:
                    from urllib.parse import urlparse
                    next_page = urlparse(next_page).path
                if next_page.startswith("/admin"):
                    return redirect(next_page)
            return redirect(url_for("admin.dashboard"))
        else:
            flash(
                "Invalid username/email or password. Please try again. / தவறான பயனர் பெயர் அல்லது கடவுச்சொல்.",
                "danger",
            )

    return render_template("admin/login.html", has_users=has_users)


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been securely logged out. / வெற்றிகரமாக வெளியேறிவிட்டீர்கள்.", "info")
    return redirect(url_for("auth.login"))
