"""
Authentication API endpoints with real SQLite persistence and JWT token generation.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.database import UserRepository
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate):
    """
    Registers a new auditor account in SQLite.
    """
    existing_user = UserRepository.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    hashed_pwd = hash_password(user_in.password)
    user = UserRepository.create(
        email=user_in.email,
        hashed_password=hashed_pwd,
        full_name=user_in.full_name or "Financial Auditor",
        role=user_in.role or "auditor",
    )

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        created_at=user.created_at,
    )


@router.post("/login", response_model=Token)
def login(credentials: UserLogin):
    """
    Authenticates auditor credentials and returns a signed JWT access token.
    """
    user = UserRepository.get_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role}
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the currently logged in auditor profile.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        created_at=current_user.created_at,
    )
