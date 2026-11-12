import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IS_VERCEL = bool(os.environ.get("VERCEL"))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
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