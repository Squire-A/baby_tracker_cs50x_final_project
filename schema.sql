CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username VARCHAR(30) NOT NULL UNIQUE,
    hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS babies (
    baby_id INTEGER PRIMARY KEY,
    baby_name TEXT NOT NULL,
    birthdate DATE NOT NULL,
    gender TEXT CHECK (gender IN ('Male', 'Female', 'Unspecified')),
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS sleeps (
    sleep_id INTEGER PRIMARY KEY,
    baby_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    duration_minutes INTEGER,
    FOREIGN KEY (baby_id) REFERENCES babies(baby_id)
);

CREATE TABLE IF NOT EXISTS nappy_changes (
    change_id INTEGER PRIMARY KEY,
    baby_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    wet BOOLEAN NOT NULL,
    dirty BOOLEAN NOT NULL,
    nappy_size CHECK (nappy_size IN ('S', 'M', 'L')) DEFAULT NULL,
    FOREIGN KEY (baby_id) REFERENCES babies(baby_id)
);

CREATE TABLE IF NOT EXISTS feeds (
    feed_id INTEGER PRIMARY KEY,
    baby_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    type TEXT CHECK (type IN ('Breast', 'Bottle')),
    quantity_ml INTEGER,
    duration_minutes INTEGER,
    FOREIGN KEY (baby_id) REFERENCES babies(baby_id)
);

CREATE TABLE IF NOT EXISTS milestones (
    milestone_id INTEGER PRIMARY KEY,
    baby_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (baby_id) REFERENCES babies(baby_id)
);
