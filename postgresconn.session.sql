-- Table: user
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64),
    email VARCHAR(120),
    password_hash VARCHAR(128) NOT NULL,
    read_articles INTEGER
);

-- Table: word
CREATE TABLE word (
    id SERIAL PRIMARY KEY,
    lemma VARCHAR(64),
    lemma_rank INTEGER,
    word_rank INTEGER
);

-- Table: text
CREATE TABLE text (
    id SERIAL PRIMARY KEY,
    url VARCHAR,
    authors VARCHAR,
    date TIMESTAMP,
    unique_words INTEGER NOT NULL,
    average_sentence_length DOUBLE PRECISION NOT NULL,
    average_word_length DOUBLE PRECISION NOT NULL,
    total_words INTEGER NOT NULL,
    lemmatized_content VARCHAR NOT NULL,
    content VARCHAR NOT NULL,
    title VARCHAR,
    difficulty DOUBLE PRECISION
);

-- Table: tag
CREATE TABLE tag (
    id SERIAL PRIMARY KEY,
    name VARCHAR
);

-- Association Table: text_tag_association
CREATE TABLE text_tag_association (
    text_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (text_id, tag_id),
    FOREIGN KEY (text_id) REFERENCES text(id),
    FOREIGN KEY (tag_id) REFERENCES tag(id)
);

-- Table: user_text
CREATE TABLE user_text (
    user_id INTEGER NOT NULL,
    text_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, text_id),
    FOREIGN KEY (user_id) REFERENCES "user"(id),
    FOREIGN KEY (text_id) REFERENCES text(id)
);

-- Table: log
CREATE TABLE log (
    id SERIAL PRIMARY KEY,
    elapsed_time_seconds INTEGER,
    date TIMESTAMP,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES "user"(id)
);

-- Table: user_word
CREATE TABLE user_word (
    user_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    number_of_times_seen INTEGER,
    PRIMARY KEY (user_id, word_id),
    FOREIGN KEY (user_id) REFERENCES "user"(id),
    FOREIGN KEY (word_id) REFERENCES word(id)
);

-- Alembic versioning table
CREATE TABLE alembic_version (
    version_num VARCHAR(32) PRIMARY KEY
);