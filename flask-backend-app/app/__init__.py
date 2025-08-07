from flask import Flask
from app.config import Config
from app.models import db
from datetime import timedelta, datetime, timezone
from flask_jwt_extended import (JWTManager)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    app.config["JWT_SECRET_KEY"] = "your_jwt_secret"
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=14)
    jwt = JWTManager(app)

    return app