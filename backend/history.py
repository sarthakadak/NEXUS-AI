"""
Saves every analysis a logged-in user runs, so they can see it again later.
Stored in the MongoDB "analyses" collection.
"""

from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

from database import get_db


def init_history_table():
    """Index so a user's history loads fast (newest first)."""
    get_db().analyses.create_index([("user_id", 1), ("_id", -1)])


def save_analysis(user_id: str, problem: str, result: dict) -> str:
    final = result.get("final_decision", {})
    inserted = get_db().analyses.insert_one({
        "user_id": user_id,
        "problem": problem,
        "decision": final.get("decision", ""),
        "confidence": final.get("confidence", ""),
        "result": result,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return str(inserted.inserted_id)


def list_analyses(user_id: str) -> list:
    """Short list for the history sidebar (newest first)."""
    docs = get_db().analyses.find(
        {"user_id": user_id},
        {"problem": 1, "decision": 1, "confidence": 1, "created_at": 1},
    ).sort("_id", -1)
    return [
        {
            "id": str(d["_id"]),
            "problem": d["problem"],
            "decision": d.get("decision", ""),
            "confidence": d.get("confidence", ""),
            "created_at": d.get("created_at", ""),
        }
        for d in docs
    ]


def get_analysis(user_id: str, analysis_id: str):
    """Full saved result. Only returns it if it belongs to this user."""
    try:
        oid = ObjectId(analysis_id)
    except InvalidId:
        return None
    d = get_db().analyses.find_one({"_id": oid, "user_id": user_id})
    if not d:
        return None
    d["id"] = str(d.pop("_id"))
    return d


def delete_analysis(user_id: str, analysis_id: str) -> bool:
    try:
        oid = ObjectId(analysis_id)
    except InvalidId:
        return False
    result = get_db().analyses.delete_one({"_id": oid, "user_id": user_id})
    return result.deleted_count > 0