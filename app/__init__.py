from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from flasgger import Swagger
from config import config
import os

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Finance Data Processing API",
        "description": "Backend API for Finance Dashboard with Role-Based Access Control",
        "version": "1.0.0",
        "contact": { "name": "Abigna Katakam" }
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token. Format: **Bearer &lt;token&gt;**"
        }
    },
    "security": [{"Bearer": []}]
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [{"endpoint": "apispec", "route": "/apispec.json", "rule_filter": lambda rule: True, "model_filter": lambda tag: True}],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}


def create_app(env="default"):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config[env])

    # Enable CORS for all routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    Swagger(app, template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.records import records_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(records_bp, url_prefix="/api/records")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    # Serve frontend
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

    @app.route("/")
    def serve_frontend():
        return send_from_directory(frontend_dir, "index.html")

    return app