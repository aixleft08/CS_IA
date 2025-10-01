from flask import Flask, jsonify
from app.config import Config
from app.models import db
from datetime import timedelta, datetime, timezone
from flask_jwt_extended import (JWTManager)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes import auth, users, articles, quizzes, translations, word_bank
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(articles)
    app.register_blueprint(quizzes)
    app.register_blueprint(translations)
    app.register_blueprint(word_bank)

    app.config["JWT_SECRET_KEY"] = "your_jwt_secret"
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=14)
    jwt = JWTManager(app)
    
    @app.route("/", methods=['GET'])
    def index():
        return jsonify({"message": "API is running!"}), 200

    return app