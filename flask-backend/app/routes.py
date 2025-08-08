from flask import Blueprint, request, jsonify, session
from app.models import db, User
from werkzeug.security import check_password_hash
from flask import current_app as app
from flask_jwt_extended import (
    create_access_token, get_jwt_identity,
    jwt_required, set_access_cookies, unset_jwt_cookies, get_jwt)
from datetime import timedelta, datetime, timezone

#authentication routes
auth = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth.route('/test', methods=['GET'])
def test():
    return jsonify({'status': 'ok'})

@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(name=data['name']).first()
    if user and user.verify_password(data['password']):
        access_token = create_access_token(identity=user.id)
        resp = jsonify({'message': 'Logged in'})
        set_access_cookies(resp, access_token, max_age=14*24*3600)
        return resp
    return jsonify({'message': 'Invalid credentials'}), 401

@auth.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({'message': 'Logged out'})
    unset_jwt_cookies(resp)
    return resp

@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'Name already registered'}), 400
    user = User(name=data['name'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered'})

#Implicit Cookie Refresh
@auth.after_app_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(days=7))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token, max_age=14*24*3600)
        return response
    except Exception:
        return response

######################################################################
#Users routes
users = Blueprint('users', __name__, url_prefix='/api/users')

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

@users.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Unauthorized'}), 401
    return jsonify({
        'id': user.id,
        'name': user.name,
        'quizzes_done': user.quizzes_done,
        'goal_length_minutes': user.goal_length_minutes
    })

@users.route('/goals', methods=['POST'])
def update_goals():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.json
    user.goal_length_minutes = data.get('goal_length_minutes', user.goal_length_minutes)
    db.session.commit()
    return jsonify({'message': 'Goals updated'})

@users.route('/quizzes/completed', methods=['POST'])
def increment_quizzes():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 401
    user.quizzes_done += 1
    db.session.commit()
    return jsonify({'message': 'Quiz count incremented'})

@users.route('/library', methods=['GET'])
def get_library():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 401
    # Assuming user.texts is a relationship to Text objects
    texts = [{
        'id': t.id,
        'title': t.title,
        'authors': t.authors,
        'url': t.url,
        'difficulty': t.difficulty
    } for t in user.texts]
    return jsonify({'library': texts})

######################################################################
#Articles routes
from app.models import Text, Tag, Log

articles = Blueprint('articles', __name__, url_prefix='/api/articles')

@articles.route('/<int:id>', methods=['GET'])
def get_article(id):
    article = Text.query.get_or_404(id)
    return jsonify({
        'id': article.id,
        'title': article.title,
        'content': article.content,
        'url': article.url,
        'authors': article.authors,
        'date': article.date,
        'unique_words': article.unique_words,
        'average_sentence_length': article.average_sentence_length,
        'average_word_length': article.average_word_length,
        'total_words': article.total_words,
        'difficulty': article.difficulty,
        'tags': [tag.name for tag in article.tags]
    })

@articles.route('/<int:id>/reading-time', methods=['POST'])
def log_reading_time(id):
    user = get_current_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.json
    elapsed_time = data.get('elapsed_time_seconds')
    log = Log(elapsed_time_seconds=elapsed_time, user_id=user.id)
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Reading time logged'})

@articles.route('/search', methods=['GET'])
def search_articles():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 401
    # Example: search by title or tag
    title = request.args.get('title')
    tag = request.args.get('tag')
    query = Text.query
    if title:
        query = query.filter(Text.title.ilike(f'%{title}%'))
    if tag:
        query = query.join(Text.tags).filter(Tag.name == tag)
    articles = query.all()
    return jsonify([{
        'id': a.id,
        'title': a.title,
        'authors': a.authors,
        'url': a.url,
        'difficulty': a.difficulty,
        'tags': [t.name for t in a.tags]
    } for a in articles])

from app.models import Word

######################################################################
# Quizzes routes
quizzes = Blueprint('quizzes', __name__, url_prefix='/api/quizzes')

@quizzes.route('/generate', methods=['POST'])
def generate_quiz():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 401
    # Example: Generate a quiz for an article (stub)
    # You can implement your own quiz logic here
    return jsonify({'quiz': 'Quiz generated with five questions'})

######################################################################
# Translations routes
translations = Blueprint('translations', __name__, url_prefix='/api/translations')

@translations.route('', methods=['GET'])
def get_translations():
    words = request.args.getlist('words')
    # Example: Dummy translation logic
    translations = {word: f"{word}_zh" for word in words}
    return jsonify({'translations': translations})

######################################################################
# Word Bank routes
word_bank = Blueprint('word_bank', __name__, url_prefix='/api')

@word_bank.route('/word', methods=['POST'])
def add_word():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.json
    word_id = data.get('word_id')
    word = Word.query.get(word_id)
    if word and word not in user.words:
        user.words.append(word)
        db.session.commit()
    return jsonify({'message': 'Word added'})

@word_bank.route('/word/<int:id>', methods=['DELETE'])
def delete_word(id):
    user = get_current_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 401
    word = Word.query.get(id)
    if word and word in user.words:
        user.words.remove(word)
        db.session.commit()
    return jsonify({'message': 'Word removed'})

@word_bank.route('/words', methods=['DELETE'])
def clear_words():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'Unauthorized'}), 401
    user.words = []
    db.session.commit()
    return jsonify({'message': 'All words cleared'})