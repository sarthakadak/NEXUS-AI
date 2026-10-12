"""
MongoDB connection for NEXUS.
Set MONGODB_URI in your .env file (see .env.example).
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

DB_NAME = os.getenv("MONGODB_DB", "nexus")
_client = None


def get_db():
    global _client
    if _client is None:
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise ValueError("MONGODB_URI is not set. Add it to your .env file.")
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _client[DB_NAME]