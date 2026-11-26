import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

def test_password_hashing():
    raw_pwd = "AuditorSecret2024!"
    hashed = hash_password(raw_pwd)
    assert hashed != raw_pwd
    assert "$" in hashed
    assert verify_password(raw_pwd, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_jwt_generation_and_decoding():
    data = {"sub": "auditor@college.edu", "role": "senior_auditor"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token.split(".")) == 3

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "auditor@college.edu"
    assert payload["role"] == "senior_auditor"
    assert "exp" in payload

def test_invalid_jwt():
    assert decode_access_token("invalid.token.signature") is None
