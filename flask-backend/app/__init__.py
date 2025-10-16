# app/__init__.py
from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.config import Config
from app.models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    with app.app_context():
        from app.models import User, Word, Text, Tag, Log
        db.create_all()

    app.config.setdefault("JWT_SECRET_KEY", "dev_change_me")
    app.config.setdefault("JWT_TOKEN_LOCATION", ["headers", "cookies"])
    app.config.setdefault("JWT_ACCESS_TOKEN_EXPIRES", timedelta(days=14))
    app.config.setdefault("JWT_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("JWT_COOKIE_SECURE", False)
    app.config.setdefault("JWT_COOKIE_CSRF_PROTECT", False)

    jwt = JWTManager(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    from app.routes import auth, users, articles, quizzes, translations, word_bank
    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(users, url_prefix="/api/users")
    app.register_blueprint(articles, url_prefix="/api/articles")
    app.register_blueprint(quizzes, url_prefix="/api/quizzes")
    app.register_blueprint(translations, url_prefix="/api/translations")
    app.register_blueprint(word_bank, url_prefix="/api/word-bank")

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/")
    def index():
        return jsonify({"message": "API is running!"}), 200

    return app
    app.config["JWT_SECRET_KEY"] = "your_jwt_secret"
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=14)
    jwt = JWTManager(app)
    
    @app.route("/", methods=['GET'])
    def index():
        return jsonify({"message": "API is running!"}), 200

    return app