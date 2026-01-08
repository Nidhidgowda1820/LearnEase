import os
import json
import hashlib
import secrets
from typing import Optional
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

# Simple file-based user storage (can be replaced with database later)
USERS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "users.json"
)

def _ensure_users_file():
    """Create users.json if it doesn't exist."""
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)

def _load_users():
    """Load users from JSON file."""
    _ensure_users_file()
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def _save_users(users):
    """Save users to JSON file."""
    _ensure_users_file()
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def _hash_password(password: str) -> str:
    """Simple password hashing (use bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()

def _verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return _hash_password(password) == hashed

def _generate_token() -> str:
    """Generate a simple token."""
    return secrets.token_urlsafe(32)

# Request models
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(req: RegisterRequest):
    """Register a new user."""
    users = _load_users()
    
    if req.email.lower() in users:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    user_id = secrets.token_urlsafe(16)
    users[req.email.lower()] = {
        "id": user_id,
        "name": req.name,
        "email": req.email.lower(),
        "password_hash": _hash_password(req.password),
    }
    _save_users(users)
    
    token = _generate_token()
    
    return JSONResponse(
        status_code=201,
        content={
            "message": "User registered successfully",
            "user": {
                "id": user_id,
                "name": req.name,
                "email": req.email.lower(),
            },
            "token": token,
        }
    )

@router.post("/login")
async def login(req: LoginRequest):
    """Login user."""
    users = _load_users()
    email_lower = req.email.lower()
    
    if email_lower not in users:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = users[email_lower]
    
    if not _verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = _generate_token()
    
    return JSONResponse(
        content={
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
            },
            "token": token,
        }
    )

