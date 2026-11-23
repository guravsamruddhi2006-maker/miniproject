"""
Application configuration settings.
"""
import os

SECRET_KEY = os.getenv("SECRET_KEY", "financial-filing-auditor-secret-key-hitl-ai-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
DATABASE_FILE = "auditor.db"
