import jwt
from datetime import datetime

SECRET_KEY = "qmtauto123321"
ALGORITHM = "HS256"

def generate_token(payload_data: dict) -> str:
    payload = {
        **payload_data
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}    