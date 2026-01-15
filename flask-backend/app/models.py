from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# associations
user_word = db.Table(
    "user_word",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("word_id", db.Integer, db.ForeignKey("word.id"), primary_key=True),
    db.Column("number_of_times_seen", db.Integer, default=0, nullable=False),
)

user_text = db.Table(
    "user_text",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("text_id", db.Integer, db.ForeignKey("text.id"), primary_key=True),
)

text_tag_association = db.Table(
    "text_tag_association",
    db.Column("text_id", db.Integer, db.ForeignKey("text.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)

# classes
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    quizzes_done = db.Column(db.Integer, default=0, nullable=False)

    words = db.relationship("Word", secondary=user_word, backref="users")
    texts = db.relationship("Text", secondary=user_text, backref="users")
    logs = db.relationship("Log", backref="user", lazy=True)

    def __init__(self, name: str, password: str):
        self.name = name
        self.set_password(password)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.name}>"


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lemma = db.Column(db.String(64), nullable=False, index=True)
    lemma_rank = db.Column(db.Integer, default=0, nullable=False)
    word_rank = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<Word {self.lemma}>"


class Text(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String, nullable=True)
    content = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=True)
    authors = db.Column(db.String, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    unique_words = db.Column(db.Integer, nullable=True)
    average_sentence_length = db.Column(db.Float, nullable=True)
    average_word_length = db.Column(db.Float, nullable=True)
    total_words = db.Column(db.Integer, nullable=True)
    difficulty = db.Column(db.Float, nullable=True)

    tags = db.relationship("Tag", secondary=text_tag_association, backref="texts")

    def __repr__(self):
        return f"<Text {self.title}>"


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, index=True)

    def __repr__(self):
        return f"<Tag {self.name}>"


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    elapsed_time_seconds = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    text_id = db.Column(db.Integer, db.ForeignKey("text.id"), nullable=True)

    def __repr__(self):
        return f"<Log {self.id} for User {self.user_id}>"


class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    text = db.Column(db.String, nullable=False, index=True)
    source_lang = db.Column(db.String(8), nullable=False)
    target_lang = db.Column(db.String(8), nullable=False)
    translated_text = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "text", "source_lang", "target_lang", name="uix_translation_text_langs"
        ),
    )

    def __repr__(self):
        return f"<Translation {self.text} {self.source_lang}->{self.target_lang}>"
