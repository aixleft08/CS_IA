from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association tables
user_word = db.Table(
    'user_word',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('word_id', db.Integer, db.ForeignKey('word.id'), primary_key=True),
    db.Column('number_of_times_seen', db.Integer, default=0)
)

user_text = db.Table(
    'user_text',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('text_id', db.Integer, db.ForeignKey('text.id'), primary_key=True)
)

text_tag_association = db.Table(
    'text_tag_association',
    db.Column('text_id', db.Integer, db.ForeignKey('text.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    quizzes_done = db.Column(db.Integer, default=0)
    goal_length_minutes = db.Column(db.Integer, default=0)

    # Relationships
    words = db.relationship('Word', secondary=user_word, backref='users')
    texts = db.relationship('Text', secondary=user_text, backref='users')
    logs = db.relationship('Log', backref='user', lazy=True)

    def __init__(self, name, password):
        self.name = name
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name}>'

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lemma = db.Column(db.String(64), nullable=False)
    lemma_rank = db.Column(db.Integer)
    word_rank = db.Column(db.Integer)

    def __repr__(self):
        return f'<Word {self.lemma}>'

class Text(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String, nullable=False)
    url = db.Column(db.String)
    authors = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    unique_words = db.Column(db.Integer)
    average_sentence_length = db.Column(db.Float)
    average_word_length = db.Column(db.Float)
    lemmatized_content = db.Column(db.String)
    total_words = db.Column(db.Integer)
    synonymized_content = db.Column(db.String)
    lemmatized_synonymized_content = db.Column(db.String)
    difficulty = db.Column(db.Float)
    tags = db.relationship('Tag', secondary=text_tag_association, backref='texts')

    def __init__(self, title, content, url=None, authors=None, date=None, difficulty=None):
        self.title = title
        self.content = content
        self.url = url
        self.authors = authors
        self.date = date or datetime.utcnow()
        if difficulty is not None:
            self.difficulty = difficulty

    #Method stubs (implement logic as needed)
    def calculate_total_pages(self):
        pass

    def calculate_average_sentence_length(self):
        pass

    def calculate_average_word_length(self):
        pass

    def lemmatize_all_content(self):
        pass

    def calculate_unique_words(self):
        pass

    def calculate_difficulty(self):
        pass

    def synonymize_content(self):
        pass

    def __repr__(self):
        return f'<Text {self.title}>'

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return f'<Tag {self.name}>'

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    elapsed_time_seconds = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text_id = db.Column(db.Integer, db.ForeignKey('text.id'))  # <---

    def __repr__(self):
        return f'<Log {self.id} for User {self.user_id}>'