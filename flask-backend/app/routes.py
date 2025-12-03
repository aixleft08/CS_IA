import random
import requests
from flask import Blueprint, request, jsonify, session
from app.models import db, User, Word, Text, Tag, Log, Translation, user_word
from flask import current_app as app
from flask_jwt_extended import (
    create_access_token, get_jwt_identity,
    jwt_required, set_access_cookies, unset_jwt_cookies, get_jwt)
from datetime import timedelta, datetime, timezone

# Helper functions
def get_or_create_translation(text, source='en', target='zh'):
    normalized = (text or '').strip()
    if not normalized:
        return None

    t = Translation.query.filter_by(
        text=normalized,
        source_lang=source,
        target_lang=target
    ).first()
    if t:
        return t

    base_url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": source,   # source language, e.g. 'en'
        "tl": target,   # target language, e.g. 'zh'
        "dt": ["t", "bd"],  # multiple dt params -> main text + dictionary
        "dj": "1",
        "q": normalized,
    }

    try:
        resp = requests.get(base_url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        sentences = data.get("sentences", [])
        translated = "".join(s.get("trans", "") for s in sentences).strip()
        if not translated:
            return None
    except Exception:
        return None

    t = Translation(
        text=normalized,
        source_lang=source,
        target_lang=target,
        translated_text=translated,
    )
    db.session.add(t)
    db.session.flush()

    return t

def _get_user_or_401():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return None, (jsonify({'error': 'Unauthorized'}), 401)
    return user, None

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

    access_token = create_access_token(identity=str(user.id))
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

    access_token = create_access_token(identity=str(user.id))

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

@users.route('/last-reading', methods=['GET'])
@jwt_required()
def last_reading():
    user_id = get_jwt_identity()

    last_log = (Log.query
                  .filter_by(user_id=user_id)
                  .filter(Log.text_id.isnot(None))
                  .order_by(Log.date.desc())
                  .first())

    if not last_log:
        return jsonify({'last': None}), 200

    text = Text.query.get(last_log.text_id)
    if not text:
        return jsonify({'last': None}), 200

    return jsonify({'last': {'id': text.id, 'title': text.title}}), 200

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
    limit = min(int(request.args.get('limit', 20)), 50)

    query = Text.query

    if title:
        query = query.filter(Text.title.ilike(f'%{title}%'))
    if tag:
        query = query.join(Text.tags).filter(Tag.name.ilike(f'%{tag}%'))

    articles = query.order_by(Text.date.desc()).limit(limit).all()

    def excerpt(text, length=140):
        if not text:
            return ''
        return text[:length] + ('…' if len(text) > length else '')

    return jsonify({
        'results': [{
            'id': a.id,
            'title': a.title,
            'authors': a.authors,
            'url': a.url,
            'difficulty': a.difficulty,
            'tags': [t.name for t in a.tags],
            'excerpt': excerpt(a.content),
            'date': a.date.isoformat() if a.date else None,
        } for a in articles]
    })

@articles.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_article(id):
    user_id = get_jwt_identity()

    article = Text.query.get(id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404

    from app.models import user_text
    db.session.execute(user_text.delete().where(user_text.c.text_id == id))

    Log.query.filter_by(text_id=id).delete(synchronize_session=False)

    db.session.delete(article)
    db.session.commit()

    return jsonify({'deleted': id}), 200


# ---Quizzes routes---
quizzes = Blueprint('quizzes', __name__, url_prefix='/api/quizzes')

@quizzes.route('/wordbank', methods=['GET'])
@jwt_required()
def generate_wordbank_quiz():
    user, error_resp = _get_user_or_401()
    if error_resp:
        return error_resp

    try:
        limit = int(request.args.get('limit', 10))
    except ValueError:
        limit = 10
    limit = max(1, min(limit, 50))

    candidates = []
    for w in user.words:
        t = Translation.query.filter_by(
            text=w.lemma,
            source_lang='en',
            target_lang='zh'
        ).first()
        if t and t.translated_text:
            candidates.append((w, t))

    if not candidates:
        return jsonify({'error': 'No words with translations in wordbank'}), 400

    if len(candidates) > limit:
        candidates = random.sample(candidates, limit)
    else:
        random.shuffle(candidates)

    questions = []
    for w, t in candidates:
        lemma = (w.lemma or '').strip()
        questions.append({
            'id': w.id,
            'zh': t.translated_text,
            'hint': lemma[0] if lemma else None,
        })

    return jsonify({
        'mode': 'wordbank_zh_to_en',
        'count': len(questions),
        'questions': questions,
    }), 200

@quizzes.route('/wordbank/submit', methods=['POST'])
@jwt_required()
def submit_wordbank_quiz():
    user, error_resp = _get_user_or_401()
    if error_resp:
        return error_resp

    data = request.json or {}
    answers = data.get('answers') or []

    if not isinstance(answers, list) or not answers:
        return jsonify({'error': 'Missing or empty answers list'}), 400

    total = 0
    correct = 0
    details = []

    touched_word_ids = set()

    for item in answers:
        try:
            wid = int(item.get('id'))
        except (TypeError, ValueError):
            continue

        given_raw = (item.get('answer') or '').strip()
        if not given_raw:
            word_obj = Word.query.get(wid)
            if not word_obj:
                continue
            expected = (word_obj.lemma or '').strip()
            total += 1
            details.append({
                'id': wid,
                'correct': False,
                'expected': expected,
                'given': given_raw,
            })
            touched_word_ids.add(wid)
            continue

        word_obj = Word.query.get(wid)
        if not word_obj:
            continue

        expected = (word_obj.lemma or '').strip()
        total += 1

        is_correct = expected.lower() == given_raw.lower()
        if is_correct:
            correct += 1

        details.append({
            'id': wid,
            'correct': is_correct,
            'expected': expected,
            'given': given_raw,
        })
        touched_word_ids.add(wid)

    if touched_word_ids:
        for wid in touched_word_ids:
            db.session.execute(
                user_word.update()
                .where(
                    user_word.c.user_id == user.id,
                    user_word.c.word_id == wid,
                )
                .values(
                    number_of_times_seen=user_word.c.number_of_times_seen + 1
                )
            )

    if total > 0:
        user.quizzes_done = (user.quizzes_done or 0) + 1

    db.session.commit()

    accuracy = (correct / total) if total > 0 else 0.0

    return jsonify({
        'total': total,
        'correct': correct,
        'accuracy': accuracy,
        'details': details,
    }), 200

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
    source = request.args.get('source', 'en')
    target = request.args.get('target', 'zh')

    if not text:
        return jsonify({'error': "Missing 'text' parameter"}), 400

    t = get_or_create_translation(text, source=source, target=target)
    if not t:
        return jsonify({'error': 'Could not translate'}), 502

    return jsonify({
        'translation': t.translated_text,
        'source_lang': t.source_lang,
        'target_lang': t.target_lang,
        'cached': True
    }), 200


# ---Word Bank routes---
word_bank = Blueprint('word_bank', __name__, url_prefix='/api')

@word_bank.route('/words', methods=['GET'])
@jwt_required()
def list_words():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    words_payload = []
    for w in user.words:
        t = Translation.query.filter_by(
            text=w.lemma,
            source_lang='en',
            target_lang='zh'
        ).first()
        zh_text = t.translated_text if t else None

        words_payload.append({
            'id': w.id,
            'lemma': w.lemma,
            'lemma_rank': w.lemma_rank,
            'word_rank': w.word_rank,
            'translation': zh_text,
        })

    return jsonify({'words': words_payload}), 200

@word_bank.route('/words', methods=['POST'])
@jwt_required()
def add_word():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json or {}
    word_text = data.get('word')

    if not word_text:
        return jsonify({'error': 'Missing word parameter'}), 400

    lemma = (word_text or '').strip().lower()
    if not lemma:
        return jsonify({'error': 'Missing word parameter'}), 400

    existing_word = Word.query.filter_by(lemma=lemma).first()
    if existing_word and existing_word in user.words:
        return jsonify({'error': 'Duplicate word'}), 409

    word = existing_word
    if not word:
        word = Word(lemma=lemma, lemma_rank=0, word_rank=0)
        db.session.add(word)
        db.session.flush()

    t = get_or_create_translation(lemma, source='en', target='zh')
    zh_text = t.translated_text if t else None

    if word not in user.words:
        user.words.append(word)
        db.session.commit()
        return jsonify({
            'word': {
                'id': word.id,
                'lemma': word.lemma,
                'translation': zh_text,
            }
        }), 201
    
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
        return jsonify({'message': 'Word deleted'}), 200
    
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
    
    return jsonify({'message': 'Word bank cleared'}), 200


# ---Dev routes---
dev = Blueprint('dev', __name__, url_prefix='/api/dev')

@dev.route('/seed-articles', methods=['POST'])
@jwt_required()
def seed_articles():
    user_id = get_jwt_identity()

    samples = [
        Text(
            title="Reading practice: Daily routines",
            content="This is a simple article about daily routines. You wake up, you eat, you study...",
            url="https://example.com/routines",
            authors="System",
            difficulty=0.3,
        ),
        Text(
            title="Travel story: A day in Tokyo",
            content="Tokyo is a busy city. In this article, we will explore Shibuya, Senso-ji, and ramen shops...",
            url="https://example.com/tokyo",
            authors="System",
            difficulty=0.5,
        ),
        Text(
            title="English for school projects",
            content="When writing a school project, it's important to structure your ideas...",
            url="https://example.com/school",
            authors="System",
            difficulty=0.4,
        ),
    ]

    db.session.add_all(samples)
    db.session.commit()
    return jsonify({"inserted": len(samples)}), 201
