"""
Simple auth module for NEXUS.
Stores users and login sessions in MongoDB.
"""

import hashlib
import secrets
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

from database import get_db


def init_db():
    """Create indexes (safe to run every time the server starts)."""
    db = get_db()
    db.users.create_index("email", unique=True)
    db.sessions.create_index("token", unique=True)


def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return pw_hash, salt


def _now():
    return datetime.now(timezone.utc).isoformat()


def _new_session(user_id: str) -> str:
    token = secrets.token_hex(32)
    get_db().sessions.insert_one(
        {"token": token, "user_id": user_id, "created_at": _now()}
    )
    return token


def create_user(email: str, password: str, name: str = "") -> dict:
    pw_hash, salt = hash_password(password)
    try:
        result = get_db().users.insert_one({
            "email": email,
            "name": name,
            "password_hash": pw_hash,
            "salt": salt,
            "created_at": _now(),
        })
    except DuplicateKeyError:
        return {"success": False, "error": "An account with this email already exists."}
    return {"success": True, "user_id": str(result.inserted_id)}


def verify_user(email: str, password: str) -> dict:
    user = get_db().users.find_one({"email": email})
    if not user:
        return {"success": False, "error": "Invalid email or password."}

    pw_hash, _ = hash_password(password, user["salt"])
    if pw_hash != user["password_hash"]:
        return {"success": False, "error": "Invalid email or password."}

    user_id = str(user["_id"])
    token = _new_session(user_id)
    return {
        "success": True,
        "token": token,
        "user": {"id": user_id, "email": user["email"], "name": user.get("name", "")},
    }


def get_or_create_google_user(email: str, name: str) -> dict:
    db = get_db()
    user = db.users.find_one({"email": email})

    if not user:
        # Google users get a random unusable password
        pw_hash, salt = hash_password(secrets.token_hex(32))
        result = db.users.insert_one({
            "email": email,
            "name": name,
            "password_hash": pw_hash,
            "salt": salt,
            "created_at": _now(),
        })
        user_id = str(result.inserted_id)
    else:
        user_id = str(user["_id"])

    token = _new_session(user_id)
    return {
        "success": True,
        "token": token,
        "user": {"id": user_id, "email": email, "name": name},
    }


def get_user_from_token(token: str):
    db = get_db()
    session = db.sessions.find_one({"token": token})
    if not session:
        return None
    try:
        user = db.users.find_one({"_id": ObjectId(session["user_id"])})
    except InvalidId:
        return None
    if not user:
        return None
    return {"id": str(user["_id"]), "email": user["email"], "name": user.get("name", "")}