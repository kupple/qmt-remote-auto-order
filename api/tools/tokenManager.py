import jwt
from datetime import datetime

ALGORITHM = "HS256"

def generate_token(payload_data: dict,salt:str) -> str:
    payload = {
        **payload_data
    }
    return jwt.encode(payload, salt, algorithm=ALGORITHM)

def verify_token(token: str,salt:str) -> dict:
    try:
        return jwt.decode(token, salt, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}    