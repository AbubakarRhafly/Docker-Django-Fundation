import os
from datetime import datetime, timezone

from pymongo import MongoClient


MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "simple_lms_logs")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

activity_logs = db["activity_logs"]
learning_analytics = db["learning_analytics"]


def log_activity(user, action, details=None):
    activity_logs.insert_one({
        "user_id": user.id if user and getattr(user, "is_authenticated", False) else None,
        "username": user.username if user and getattr(user, "is_authenticated", False) else "anonymous",
        "action": action,
        "details": details or {},
        "created_at": datetime.now(timezone.utc),
    })


def log_learning_event(user, course_id, lesson_id=None, event_type="learning_event"):
    learning_analytics.insert_one({
        "user_id": user.id if user else None,
        "username": user.username if user else "anonymous",
        "course_id": course_id,
        "lesson_id": lesson_id,
        "event_type": event_type,
        "created_at": datetime.now(timezone.utc),
    })


def get_activity_summary():
    pipeline = [
        {
            "$group": {
                "_id": "$action",
                "total": {"$sum": 1}
            }
        },
        {
            "$sort": {
                "total": -1
            }
        }
    ]

    return list(activity_logs.aggregate(pipeline))


def get_learning_summary():
    pipeline = [
        {
            "$group": {
                "_id": {
                    "course_id": "$course_id",
                    "event_type": "$event_type"
                },
                "total": {"$sum": 1}
            }
        },
        {
            "$sort": {
                "total": -1
            }
        }
    ]

    return list(learning_analytics.aggregate(pipeline))