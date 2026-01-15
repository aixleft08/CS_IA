import random
import requests
from flask import Blueprint, request, jsonify, session
from app.models import db, User, Word, Text, Tag, Log, Translation, user_word, user_text
from flask import current_app as app
from flask_jwt_extended import (
    create_access_token, get_jwt_identity,
    jwt_required, set_access_cookies, unset_jwt_cookies, get_jwt)
from datetime import timedelta, datetime, timezone
from sqlalchemy import func

# Helper functions
def get_minutes_read(user_id):
    total_seconds = (
        db.session.query(func.coalesce(func.sum(Log.elapsed_time_seconds), 0))
        .filter(Log.user_id == user_id)
        .scalar()
    ) or 0

    return int(total_seconds // 60)

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
            'minutes_read': 0
        },
        'token': access_token
    })

    set_access_cookies(resp, access_token, max_age=14*24*3600)

    return resp, 200

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
            'minutes_read': get_minutes_read(user.id)
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
            'minutes_read': get_minutes_read(user.id)
        }
    })

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

    data = request.json or {}
    try:
        elapsed_time = int(data.get('elapsed_time_seconds', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'elapsed_time_seconds must be an integer'}), 400

    if elapsed_time <= 0:
        return jsonify({'error': 'elapsed_time_seconds must be > 0'}), 400
    if elapsed_time > 6 * 60 * 60:
        return jsonify({'error': 'elapsed_time_seconds too large'}), 400

    if not Text.query.get(id):
        return jsonify({'error': 'Article not found'}), 404

    log = Log(elapsed_time_seconds=elapsed_time, user_id=user.id, text_id=id)
    db.session.add(log)
    db.session.commit()

    return jsonify({'readingTime': elapsed_time}), 200

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

@articles.route('/search', methods=['GET'])
@jwt_required()
def search_articles():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    title = (request.args.get('title') or '').strip()
    tag = (request.args.get('tag') or '').strip()
    limit = min(int(request.args.get('limit', 20)), 50)

    query = Text.query.join(user_text, user_text.c.text_id == Text.id)\
                      .filter(user_text.c.user_id == user.id)

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

def _norm_tag(name: str) -> str:
    return (name or "").strip().lower()

def get_or_create_tag(name: str) -> Tag | None:
    name = _norm_tag(name)
    if not name:
        return None

    t = Tag.query.filter_by(name=name).first()
    if t:
        return t

    t = Tag(name=name)
    db.session.add(t)
    db.session.flush()  # gets t.id without committing
    return t

@dev.route('/seed-articles', methods=['POST'])
@jwt_required()
def seed_articles():
    raw_user_id = get_jwt_identity()
    try:
        user_id = int(raw_user_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user id in token"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.texts and len(user.texts) > 0:
        return jsonify({"error": "Already seeded for this user"}), 409

    samples = [
        {
            "text": Text(
                title="Reading practice: Daily routines",
                content=(
                    "Having a daily routine is super important. A routine is a set of habits you repeat every day. "
                    "It helps you save time, reduce stress, and focus on what matters next.\n\n"
                    "On a school day, you might wake up at 6am. You wash your face, brush your teeth, "
                    "and get dressed. Some people tend to make their bed right away, and some don't. It takes only one minute, "
                    "but it makes the room feel tidy.\n\n"
                    "Breakfast is an important part of the morning. A simple meal can give you energy you need for the day. "
                    "If you are busy, you can prepare something the night before. "
                    "For example, you can make a sandwich and put it in the fridge.\n\n"
                    "After breakfast, you go to school or start work. During the day, it is helpful to take short breaks. "
                    "A five-minute break can refresh your mind. You can stand up, drink water, and stretch.\n\n"
                    "In the evening, many people review what they learned and prepare for the next day. "
                    "Some people write a short to-do list. Others read a book, practice a hobby, or take a walk. "
                    "A calm routine before bed can improve your sleep.\n\n"
                    "Routines don't need to be perfect. The goal is to build a rhythm that supports your health, "
                    "your learning, and your goals. Even small habits can make a big difference over time, just like reading in Enlingo."
                ),
                url="https://example.com/routines",
                authors="System",
                difficulty=0.3,
            ),
            "tags": ["daily-life", "routine", "habits"]
        },
        {
            "text": Text(
                title="Travel story: A day in Tokyo",
                content=(
                    "Tokyo is a beautiful city of contrasts. It can feel modern and traditional at the same time. "
                    "Tall buildings and bright screens stand next to quiet temples and small gardens.\n\n"
                    "I started the day in Shibuya. The station was crowded, but the signs were clear. "
                    "When I walked outside, I saw Shibuya Crossing. Cars stopped, and people crossed from every direction. "
                    "It looked chaotic, but it was strangely organised.\n\n"
                    "After that, I took a train to Asakusa to visit Senso-ji. The streets near the temple were filled with shops. "
                    "Some sold souvenirs, and others sold snacks. The main gate looks so traditional yet so cool.\n\n"
                    "At lunchtime, I searched for a small ramen shop. In Tokyo, even simple restaurants can be excellent. "
                    "I bought a ticket from a machine, gave it to the chef, and sat at the counter. "
                    "The ramen arrived quickly: rich broth, noodles, and a slice of pork. It was hot and satisfying.\n\n"
                    "In the afternoon, I explored a quiet neighbourhood with narrow streets. I noticed small details: "
                    "bicycles parked neatly, tiny plants outside homes, and vending machines on almost every corner. "
                    "Even when the city is busy, there are calm places if you keep walking.\n\n"
                    "At night, the lights became brighter. I visited a convenience store to buy a drink and a snack. "
                    "Then I returned to the station, tired but happy. Tokyo felt huge, but the transport made it easy. "
                    "I promised myself I would come back and explore more slowly next time."
                ),
                url="https://example.com/tokyo",
                authors="System",
                difficulty=0.5,
            ),
            "tags": ["travel", "japan", "story"]
        },
        {
            "text": Text(
                title="English for school projects",
                content=(
                    "A school project is easier when you plan your writing. Good writing is not only about grammar. "
                    "It is also about structure, clarity, and strong examples.\n\n"
                    "First, understand the task. Read the instructions carefully and highlight key words. "
                    "Ask yourself: What is the topic? What questions must I answer? How long should the project be? "
                    "If you are unsure, ask your teacher early.\n\n"
                    "Next, collect information. Use reliable sources such as textbooks, school databases, and trusted websites. "
                    "Take notes in your own words. If you copy sentences directly, you may forget to cite them later.\n\n"
                    "Then, build a simple outline. A clear structure often looks like this:\n"
                    "1) Introduction: explain the topic and your main idea.\n"
                    "2) Body paragraphs: each paragraph covers one point, with evidence and explanation.\n"
                    "3) Conclusion: summarise your points and restate the main message.\n\n"
                    "When you write, keep your sentences clear. Avoid very long sentences with too many ideas. "
                    "Use linking words to show connections: however, therefore, for example, in addition, and as a result.\n\n"
                    "Finally, revise your work. Check for spelling, punctuation, and repeated words. "
                    "Read your project aloud to see if it sounds natural. If possible, ask a classmate to read it. "
                    "A fresh pair of eyes can find mistakes you missed.\n\n"
                    "With a good plan and careful revision, you can make your project more confident, more organised, and easier to read."
                ),
                url="https://example.com/school",
                authors="System",
                difficulty=0.4,
            ),
            "tags": ["school", "writing", "study-skills"]
        },
    ]

    texts = [item["text"] for item in samples]
    db.session.add_all(texts)
    db.session.flush()

    for item in samples:
        text_obj: Text = item["text"]
        tag_names = item["tags"]

        tag_objs = []
        for tn in tag_names:
            t = get_or_create_tag(tn)
            if t:
                tag_objs.append(t)

        text_obj.tags = tag_objs

    for text_obj in texts:
        if text_obj not in user.texts:
            user.texts.append(text_obj)

    db.session.commit()

    return jsonify({
        "inserted": len(texts),
        "user_id": user.id,
        "tagged": True,
        "linked_to_user": True,
    }), 201
