# app/__init__.py
import os
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
        db.create_all()

    JWTManager(app)

    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    CORS(
        app,
        resources={r"/api/*": {"origins": [frontend_origin]}},
        supports_credentials=True,
    )

    # Blueprints
    from app.routes import auth, users, articles, quizzes, translations, word_bank, dev
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(articles)
    app.register_blueprint(quizzes)
    app.register_blueprint(translations)
    app.register_blueprint(word_bank)
    app.register_blueprint(dev)

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/")
    def index():
        return jsonify({"message": "API is running!"}), 200

    return app