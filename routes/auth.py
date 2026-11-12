from functools import wraps
from urllib.parse import urlparse

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash

from database import db
from database.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/admin")

REMEMBER_COOKIE_NAME = "vithaigal_remember_admin"
REMEMBER_MAX_AGE = 30 * 86400  # 30 days

VAULT_COOKIE_NAME = "vithaigal_admin_vault"
VAULT_MAX_AGE = 365 * 86400  # 365 days


def _get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def _set_vault_cookie(response, user):
    """Persist signed admin credentials vault cookie across serverless cold starts."""
    try:
        s = _get_serializer()
        token = s.dumps({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "password_hash": user.password_hash,
        })
        response.set_cookie(
            VAULT_COOKIE_NAME,
            token,
            max_age=VAULT_MAX_AGE,
            httponly=True,
            samesite="Lax",
            secure=False,
            path="/",
        )
    except (TypeError, ValueError) as err:
        current_app.logger.debug("Failed to set vault cookie: %s", err)
    return response


def _get_vault_data():
    """Retrieve and decode signed vault cookie payload if available."""
    token = request.cookies.get(VAULT_COOKIE_NAME)
    if not token:
        return None
    try:
        s = _get_serializer()
        return s.loads(token, max_age=VAULT_MAX_AGE)
    except (BadSignature, SignatureExpired, KeyError, TypeError, ValueError) as err:
        current_app.logger.debug("Vault cookie decode skipped: %s", err)
        return None


def _restore_user_from_remember_cookie():
    """Attempt to restore admin session from signed remember cookie."""
    token = request.cookies.get(REMEMBER_COOKIE_NAME)
    if not token:
        return None
    try:
        s = _get_serializer()
        data = s.loads(token, max_age=REMEMBER_MAX_AGE)
        user_id = data.get("user_id")
        username = data.get("username")
        user = None
        if user_id:
            user = db.session.get(User, user_id)
        if not user and username:
            user = User.query.filter(User.username.ilike(username)).first()
        if not user and username and data.get("password_hash"):
            # Restore user on fresh serverless instance from signed cookie
            user = User()
            user.username = username
            user.email = data.get("email", f"{username.lower()}@vithaigaliyakkam.org")
            user.full_name = data.get("full_name", username)
            user.role = data.get("role", "admin")
            user.password_hash = data.get("password_hash")
            db.session.add(user)
            db.session.commit()
        elif (
            user
            and data.get("password_hash")
            and user.password_hash != data.get("password_hash")
        ):
            # Sync updated password hash from cookie if local DB is outdated
            user.password_hash = data.get("password_hash")
            db.session.commit()

        if user:
            session.permanent = True
            session["user_id"] = user.id
            session["username"] = user.username
            session["full_name"] = user.full_name
            session["role"] = user.role
            return user
    except (BadSignature, SignatureExpired, KeyError, TypeError, ValueError) as err:
        current_app.logger.debug("Remember cookie validation skipped: %s", err)
    return None


def _set_remember_cookie(response, user):
    """Set 30-day signed persistent remember cookie on response."""
    try:
        s = _get_serializer()
        token = s.dumps({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "password_hash": user.password_hash,
        })
        response.set_cookie(
            REMEMBER_COOKIE_NAME,
            token,
            max_age=REMEMBER_MAX_AGE,
            httponly=True,
            samesite="Lax",
            secure=False,
            path="/",
        )
    except (TypeError, ValueError) as err:
        current_app.logger.debug("Failed to set remember cookie: %s", err)
    return response


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            user = _restore_user_from_remember_cookie()
            if not user:
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
    if session.get("user_id") or _restore_user_from_remember_cookie():
        return redirect(url_for("admin.dashboard"))

    has_users = User.query.first() is not None

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

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
            # Check if user already exists (by username or email)
            existing_user = User.query.filter(
                (User.username.ilike(username)) | (User.email.ilike(email))
            ).first()

            if existing_user:
                existing_user.username = username
                existing_user.email = email
                if full_name:
                    existing_user.full_name = full_name
                existing_user.role = "admin"
                existing_user.set_password(password)
                db.session.commit()
                target_user = existing_user
                flash(
                    f"Administrator credentials saved for {target_user.full_name}! / நிர்வாக கணக்கு விபரம் வெற்றிகரமாக சேமிக்கப்பட்டது!",
                    "success",
                )
            else:
                target_user = User()
                target_user.username = username
                target_user.email = email
                target_user.full_name = full_name or username
                target_user.role = "admin"
                target_user.set_password(password)
                db.session.add(target_user)
                db.session.commit()
                flash(
                    f"Registration successful! Welcome to the Editorial Portal, {target_user.full_name}. / நிர்வாக கணக்கு வெற்றிகரமாக உருவாக்கப்பட்டது!",
                    "success",
                )

            # Set session
            session.permanent = True
            session["user_id"] = target_user.id
            session["username"] = target_user.username
            session["full_name"] = target_user.full_name
            session["role"] = target_user.role

            resp = redirect(url_for("admin.dashboard"))
            resp = _set_remember_cookie(resp, target_user)
            resp = _set_vault_cookie(resp, target_user)
            return resp

    return render_template("admin/register.html", has_users=has_users)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # If admin is already authenticated or has valid persistent cookie, direct them straight to dashboard
    if session.get("user_id") or _restore_user_from_remember_cookie():
        return redirect(url_for("admin.dashboard"))

    has_users = User.query.first() is not None

    if request.method == "POST":
        identifier = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Allow login by either username or email
        user = User.query.filter(
            (User.username.ilike(identifier)) | (User.email.ilike(identifier))
        ).first()

        # Check vault cookie if user is missing or outdated on fresh serverless instance
        vault_data = _get_vault_data()
        if vault_data:
            v_user = vault_data.get("username", "")
            v_email = vault_data.get("email", "")
            v_hash = vault_data.get("password_hash", "")
            if identifier.lower() in (
                v_user.lower(),
                v_email.lower(),
            ) and check_password_hash(v_hash, password):
                if not user:
                    user = User()
                    user.username = v_user
                    user.email = v_email
                    user.full_name = vault_data.get("full_name", v_user)
                    user.role = vault_data.get("role", "admin")
                    user.password_hash = v_hash
                    db.session.add(user)
                    db.session.commit()
                elif user.password_hash != v_hash:
                    user.password_hash = v_hash
                    db.session.commit()

        if user and user.check_password(password):
            session.permanent = True
            session["user_id"] = user.id
            session["username"] = user.username
            session["full_name"] = user.full_name
            session["role"] = user.role
            flash(f"Welcome back, {user.full_name}! / நல்வரவு!", "success")

            next_page = request.args.get("next")
            redirect_url = url_for("admin.dashboard")
            if next_page and "/admin/login" not in next_page:
                if "://" in next_page:
                    next_page = urlparse(next_page).path
                if next_page.startswith("/admin"):
                    redirect_url = next_page

            resp = redirect(redirect_url)
            resp = _set_remember_cookie(resp, user)
            resp = _set_vault_cookie(resp, user)
            return resp
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
    resp = redirect(url_for("auth.login"))
    resp.delete_cookie(REMEMBER_COOKIE_NAME, path="/")
    return resp
