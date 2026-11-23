"""
User Model for SQLite persistence.
"""
from datetime import datetime
from typing import Optional


class User:
    """
    User entity representing an auditor.
    """
    def __init__(
        self,
        id: int,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        role: str = "auditor",
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.role = role
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "created_at": self.created_at,
        }
