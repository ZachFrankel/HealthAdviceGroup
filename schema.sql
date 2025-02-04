DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    age INTEGER,
    weight REAL,
    height INTEGER
);

DROP TABLE IF EXISTS bookings;
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATETIME NOT NULL,
    address TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

DROP TABLE IF EXISTS health_metrics;
CREATE TABLE health_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATETIME NOT NULL,
    weight REAL NOT NULL,
    blood_pressure TEXT NOT NULL,
    heart_rate INTEGER NOT NULL,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);