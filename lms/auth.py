import jwt
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.auth.models import User
from ninja.security import HttpBearer


def create_access_token(user):
    payload = {
        "user_id": user.id,
        "username": user.username,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(user):
    payload = {
        "user_id": user.id,
        "username": user.username,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            if payload.get("type") != "access":
                return None

            user = User.objects.select_related("profile").get(id=payload["user_id"])
            return user

        except Exception:
            return None