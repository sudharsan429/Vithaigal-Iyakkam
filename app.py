import os

from flask import Flask, render_template

from config import Config
from database import db
from database.seed_data import seed_database
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.public import public_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload/instance directories exist.
    # On Vercel the filesystem is read-only (except /tmp), so don't crash if it fails.
    for path in (
        app.config["UPLOAD_FOLDER"],
        os.path.join(app.root_path, "instance"),
    ):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError:
            pass

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)

    # Register global context processor for all templates & error handlers
    from routes.public import inject_global_data

    app.context_processor(inject_global_data)

    # Custom Jinja filters
    @app.template_filter("datetime_format")
    def datetime_format_filter(value, format="%b %d, %Y"):
        if value is None:
            return ""
        return value.strftime(format)

    @app.template_filter("truncate_words")
    def truncate_words_filter(text, count=25):
        if not text:
            return ""
        words = text.split()
        if len(words) <= count:
            return text
        return " ".join(words[:count]) + "..."

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("base.html", not_found=True), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("base.html", server_error=True), 500

    # Initialize DB & Seed Data
    with app.app_context():
        db.create_all()
        seed_database()

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    print(f"Starting Vithaigal Iyakkam digital news portal on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)