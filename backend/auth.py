"""
Simple auth module for NEXUS.
Uses SQLite for storage, bcrypt-style hashing via hashlib+salt (no extra
dependency beyond passlib), and random tokens for sessions.
"""

import sqlite3
import hashlib
import secrets
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "nexus.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return pw_hash, salt


def create_user(email: str, password: str, name: str = "") -> dict:
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM users WHERE email = ?", (email,)
    ).fetchone()
    if existing:
        conn.close()
        return {"success": False, "error": "An account with this email already exists."}

    pw_hash, salt = hash_password(password)
    cursor = conn.execute(
        "INSERT INTO users (email, name, password_hash, salt) VALUES (?, ?, ?, ?)",
        (email, name, pw_hash, salt),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return {"success": True, "user_id": user_id}


def verify_user(email: str, password: str) -> dict:
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()

    if not user:
        conn.close()
        return {"success": False, "error": "Invalid email or password."}

    pw_hash, _ = hash_password(password, user["salt"])
    if pw_hash != user["password_hash"]:
        conn.close()
        return {"success": False, "error": "Invalid email or password."}

    token = secrets.token_hex(32)
    conn.execute(
        "INSERT INTO sessions (token, user_id) VALUES (?, ?)",
        (token, user["id"]),
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "token": token,
        "user": {"id": user["id"], "email": user["email"], "name": user["name"]},
    }


def get_user_from_token(token: str):
    conn = get_db()
    row = conn.execute(
        """
        SELECT users.id, users.email, users.name
        FROM sessions JOIN users ON sessions.user_id = users.id
        WHERE sessions.token = ?
        """,
        (token,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None