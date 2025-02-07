import sqlite3 from 'sqlite3';

const db = new sqlite3.Database('./src/lib/server/db.db');

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (name) REFERENCES users(name),
    FOREIGN KEY (email) REFERENCES users(email)
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS health_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    date TEXT NOT NULL,
    weight REAL,
    blood_pressure TEXT,
    steps INTEGER,
    notes TEXT,
    FOREIGN KEY (email) REFERENCES users(email)
  )`);
});

export { db };