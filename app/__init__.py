from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'

    # 🔐 Basic config (we can move to config.py later)
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lifepilot.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # -----------------------------
    # Register Blueprints (IMPORTANT)
    # -----------------------------
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.documents import documents_bp
    from app.routes.scholarship import scholarships_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(scholarships_bp)

    # -----------------------------
    # Temporary home route
    # -----------------------------
    @app.route("/")
    def home():
        return "Life Pilot AI Agent Running 🚀 (Now Modular)"

    return app