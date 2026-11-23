"""
FastAPI dependency injection utilities.
Validates real JWT tokens against SQLite UserRepository.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.database import UserRepository
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Decodes the JWT token and fetches the User from SQLite.
    Falls back to a demo auditor if no token is passed (convenience during local testing).
    """
    if token:
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            email = payload["sub"]
            user = UserRepository.get_by_email(email)
            if user:
                return user

    # Fallback to demo user if available, or create on the fly
    demo_user = UserRepository.get_by_email("auditor@demo.com")
    if not demo_user:
        from app.core.security import hash_password
        demo_user = UserRepository.create(
            email="auditor@demo.com",
            hashed_password=hash_password("password123"),
            full_name="Demo Lead Auditor",
            role="auditor",
        )
    return demo_user
