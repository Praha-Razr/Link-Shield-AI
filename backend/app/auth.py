import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
import jwt
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User

# --- Password Hashing with Bcrypt ---
def hash_password(password: str) -> str:
    """Hash plaintext password with bcrypt (salt rounds 12)."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

# --- JWT Token Generation & Verification ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    expire = now_utc + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": now_utc})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except (jwt.PyJWTError, Exception):
        return None

# --- Token Extractor from Header or Cookie ---
def get_token_from_request(request: Request) -> Optional[str]:
    # 1. Check Authorization: Bearer <token>
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    
    # 2. Check access_token cookie
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token.strip()
    
    return None

# --- Authentication Dependencies ---
def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = get_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def require_officer(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "officer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: Officer credentials required for this intelligence workspace."
        )
    return current_user

def require_citizen_or_officer(current_user: User = Depends(get_current_user)) -> User:
    return current_user

# --- Login & Lockout Core Logic ---
def authenticate_user(db: Session, username: str, password: str) -> User:
    user = db.query(User).filter(User.username == username.strip().lower()).first()
    now_utc = datetime.now(timezone.utc)
    
    if not user:
        # Dummy verification to prevent timing side-channel attacks
        bcrypt.checkpw(b"dummy_password", b"$2b$12$e8Y5tGq6tQG6QJ7n1Rk8Ie0.0M2n/C1U1W6JkU0x6U.E4v5W0.P8K")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    
    # Check if account is locked
    if user.locked_until:
        # Handle timezone compatibility
        locked_time = user.locked_until
        if locked_time.tzinfo is None:
            locked_time = locked_time.replace(tzinfo=timezone.utc)
        
        if locked_time > now_utc:
            remaining_mins = max(1, int((locked_time - now_utc).total_seconds() / 60))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account temporarily locked due to 5 consecutive failed attempts. Please try again in {remaining_mins} minutes."
            )
        else:
            # Lock expired
            user.locked_until = None
            user.failed_attempts = 0
            db.commit()
    
    if not verify_password(password, user.password_hash):
        user.failed_attempts += 1
        if user.failed_attempts >= 5:
            user.locked_until = now_utc + timedelta(minutes=5)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    
    # Successful login: reset attempts and record last_login
    user.failed_attempts = 0
    user.locked_until = None
    user.last_login = now_utc
    db.commit()
    return user
