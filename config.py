import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IS_VERCEL = bool(os.environ.get("VERCEL"))

class Config:
    # Consistent secret key across serverless instances and cold starts
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "vithaigal-iyakkam-secure-persistent-secret-key-2026"
    )
    # Retain admin session for 30 days
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_NAME = "vithaigal_admin_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_PATH = "/"
    PREFERRED_URL_SCHEME = "https"

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:////tmp/vithaigal.db" if IS_VERCEL
        else f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'vithaigal.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = "/tmp/uploads" if IS_VERCEL else os.path.join(BASE_DIR, "static", "images", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = ("png", "jpg", "jpeg", "webp", "gif")
    ITEMS_PER_PAGE = 9
    ADMIN_ITEMS_PER_PAGE = 15