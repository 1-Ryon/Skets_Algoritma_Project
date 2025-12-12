from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

from database import db_manager

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "academic-system-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 jam

security = HTTPBearer()


class AuthHandler:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM

    def encode_token(self, username: str, role: str) -> str:
        """Encode JWT token"""
        payload = {
            "sub": username,
            "role": role,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        """Decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def get_current_user(self, token: str) -> dict:
        """Get user data from token"""
        payload = self.decode_token(token)
        username = payload.get("sub")

        user = db_manager.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user


auth_handler = AuthHandler()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Dependency untuk mendapatkan current user"""
    token = credentials.credentials
    return auth_handler.get_current_user(token)
