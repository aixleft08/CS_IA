from flask import Blueprint, request, jsonify, session
from app.models import db, User, Word, Text, Tag, Log
from werkzeug.security import check_password_hash
from flask import current_app as app
from flask_jwt_extended import (
    create_access_token, get_jwt_identity,
    jwt_required, set_access_cookies, unset_jwt_cookies, get_jwt)
from datetime import timedelta, datetime, timezone

# ---authentication routes---
auth = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth.route('/test', methods=['GET'])
def test():
    return jsonify({'status': 'online', 'timestamp': datetime.now(timezone.utc).isoformat()})

@auth.route('/login', methods=['POST'])
def login():
    data = request.json or {}

    name = data.get('name')
    password = data.get('password')

    if not isinstance(name, str) or not name.strip():
        return jsonify({'error': 'missing fields'}), 400
    if not isinstance(password, str) or not password.strip():
        return jsonify({'error': 'missing fields'}), 400

    user = User.query.filter_by(name=name.strip()).first()
    if not user or not user.verify_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user.id)
    resp = jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'quizzes_done': user.quizzes_done,
            'goal_length_minutes': user.goal_length_minutes
        },
        'token': access_token
    })

    set_access_cookies(resp, access_token, max_age=14*24*3600)
    return resp, 200

@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    resp = jsonify({'message': 'Logged out'})
    unset_jwt_cookies(resp)
    return resp, 200

@auth.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    name = (data.get('name') or '').strip()
    password = data.get('password') or ''
    confirm = data.get('confirm_password') or ''

    if not isinstance(name, str) or not name.strip():
        return jsonify({'error': 'missing fields'}), 400
    if not isinstance(password, str) or not password.strip():
        return jsonify({'error': 'missing fields'}), 400
    if not isinstance(confirm, str) or not confirm.strip():
        return jsonify({'error': 'missing fields'}), 400
    if password != confirm:
        return jsonify({'error': 'passwords do not match'}), 400

    if User.query.filter_by(name=name).first():
        return jsonify({'error': 'username already exists'}), 409

    user = User(name=name, password=password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)

    resp = jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'quizzes_done': user.quizzes_done,
            'goal_length_minutes': user.goal_length_minutes
        },
        'token': access_token
    })

    set_access_cookies(resp, access_token, max_age=14*24*3600)

    return resp, 200

@auth.route('/user', methods=['GET'])
@jwt_required()
def get_auth_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'quizzes_done': user.quizzes_done,
            'goal_length_minutes': user.goal_length_minutes
        }
    })

# ---Users routes---
users = Blueprint('users', __name__, url_prefix='/api/users')

@users.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'quizzes_done': user.quizzes_done,
            'goal_length_minutes': user.goal_length_minutes
        }
    })

@users.route('/goals', methods=['POST'])
@jwt_required()
def update_goals():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    user.goal_length_minutes = data.get('goal_length_minutes', user.goal_length_minutes)
    db.session.commit()
    
    return jsonify({'goals': {'goal_length_minutes': user.goal_length_minutes}})

@users.route('/quizzes/completed', methods=['POST'])
@jwt_required()
def increment_quizzes():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user.quizzes_done += 1
    db.session.commit()
    
    return jsonify({'count': user.quizzes_done})

@users.route('/library', methods=['GET'])
@jwt_required()
def get_library():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    texts = [{
        'id': t.id,
        'title': t.title,
        'authors': t.authors,
        'url': t.url,
        'difficulty': t.difficulty
    } for t in user.texts]
    
    return jsonify({'library': texts})

# ---Articles routes---
articles = Blueprint('articles', __name__, url_prefix='/api/articles')

@articles.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_article(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    article = Text.query.get_or_404(id)
    return jsonify({
        'article': {
            'id': article.id,
            'title': article.title,
            'content': article.content,
            'url': article.url,
            'authors': article.authors,
            'date': article.date.isoformat() if article.date else None,
            'unique_words': article.unique_words,
            'average_sentence_length': article.average_sentence_length,
            'average_word_length': article.average_word_length,
            'total_words': article.total_words,
            'difficulty': article.difficulty,
            'tags': [tag.name for tag in article.tags]
        }
    })

@articles.route('/<int:id>/reading-time', methods=['POST'])
@jwt_required()
def log_reading_time(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    elapsed_time = data.get('elapsed_time_seconds')
    
    log = Log(elapsed_time_seconds=elapsed_time, user_id=user.id, text_id=id)
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'readingTime': elapsed_time})

@articles.route('/search', methods=['GET'])
@jwt_required()
def search_articles():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    title = request.args.get('title')
    tag = request.args.get('tag')
    query = Text.query
    
    if title:
        query = query.filter(Text.title.ilike(f'%{title}%'))
    if tag:
        query = query.join(Text.tags).filter(Tag.name.ilike(f'%{tag}%'))
    
    articles = query.all()
    
    return jsonify({
        'results': [{
            'id': a.id,
            'title': a.title,
            'authors': a.authors,
            'url': a.url,
            'difficulty': a.difficulty,
            'tags': [t.name for t in a.tags]
        } for a in articles]
    })

# ---Quizzes routes---
quizzes = Blueprint('quizzes', __name__, url_prefix='/api/quizzes')

@quizzes.route('/generate', methods=['POST'])
@jwt_required()
def generate_quiz():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    article_id = data.get('article_id')
    
    # Need to implement quiz generation logic here later
    # This is a stub - replace with actual quiz generation
    quiz = {
        'id': 1,
        'article_id': article_id,
        'questions': [
            {
                'id': 1,
                'question': 'Sample question 1',
                'options': ['A', 'B', 'C', 'D'],
                'correct_answer': 'A'
            },
            # Add more questions...
        ]
    }
    
    return jsonify({'quiz': quiz})

@quizzes.route('/result', methods=['GET'])
@jwt_required()
def get_quiz_result():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    quiz_id = request.args.get('quiz_id')
    
    # Check if quiz is complete (stub implementation)
    # Need to implement actual quiz completion tracking later
    is_complete = True  # Replace with actual logic
    
    if not is_complete:
        return jsonify({'error': 'Quiz incomplete'}), 400
    
    # Calculate score (stub)
    score = 80  # Need to replace with actual scoring logic later
    
    return jsonify({'results': score})

# ---Translations routes---
translations = Blueprint('translations', __name__, url_prefix='/api/translations')

@translations.route('', methods=['GET'])
@jwt_required()
def get_translations():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    text = request.args.get('text')
    if not text:
        return jsonify({'error': "Missing 'text' parameter"}), 400
    
    # Implement actual translation logic here
    # This is a stub using a simple mapping
    translation_map = {
        'hello': '你好',
        # Need to add more translations later or use a translation service
    }
    
    translation = translation_map.get(text.lower(), f"{text}_zh")
    
    return jsonify({'translation': translation})

# ---Word Bank routes---
word_bank = Blueprint('word_bank', __name__, url_prefix='/api')

@word_bank.route('/words', methods=['GET'])
@jwt_required()
def list_words():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    # user.words comes from the many-to-many
    words = [
        {
            'id': w.id,
            'lemma': w.lemma,
            'lemma_rank': w.lemma_rank,
            'word_rank': w.word_rank,
        }
        for w in user.words
    ]

    return jsonify({'words': words}), 200


@word_bank.route('/words', methods=['POST'])
@jwt_required()
def add_word():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    word_text = data.get('word')
    
    if not word_text:
        return jsonify({'error': 'Missing word parameter'}), 400
    
    # Check if word already exists for user
    existing_word = Word.query.filter_by(lemma=word_text.lower()).first()
    if existing_word and existing_word in user.words:
        return jsonify({'error': 'Duplicate word'}), 409
    
    # Create or get word
    word = Word.query.filter_by(lemma=word_text.lower()).first()
    if not word:
        word = Word(lemma=word_text.lower(), lemma_rank=0, word_rank=0)
        db.session.add(word)
        db.session.flush()
    
    # Add word to user's word bank
    if word not in user.words:
        user.words.append(word)
        db.session.commit()
        return jsonify({'word': {'id': word.id, 'lemma': word.lemma}}), 201
    
    return jsonify({'error': 'Action declined'}), 500

@word_bank.route('/words/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_word(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    word = Word.query.get(id)
    if not word:
        return jsonify({'error': 'Word not found'}), 404
    
    if word in user.words:
        user.words.remove(word)
        db.session.commit()
        return jsonify({'message': 'Word deleted'})
    
    return jsonify({'error': 'Word not found in word bank'}), 404

@word_bank.route('/words', methods=['DELETE'])
@jwt_required()
def clear_words():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if not user.words:
        return jsonify({'error': 'Empty word bank'}), 400
    
    user.words = []
    db.session.commit()
    
    return jsonify({'message': 'Word bank cleared'})
