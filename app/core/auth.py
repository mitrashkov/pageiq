from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ApiKey, User
from app.core.security import verify_api_key

# Security scheme
security = HTTPBearer(auto_error=False)  # Don't auto-error so we can handle anonymous users

def get_api_key_hash(api_key: str, db: Session) -> Optional[str]:
    """Get API key hash from database for verification"""
    db_api_key = db.query(ApiKey).filter(
        ApiKey.revoked == False
    ).first()  # In real implementation, this should search by hash or key identifier

    if db_api_key and verify_api_key(api_key, db_api_key.key_hash):
        return db_api_key.key_hash
    return None

def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from API key, or None for anonymous access"""
    if not credentials:
        # Anonymous access - create a temporary user or handle as free tier
        return None

    api_key = credentials.credentials

    if not api_key:
        return None

    # Find API key in database by verifying against all active keys
    # In production, you'd want to optimize this with proper indexing
    db_api_keys = db.query(ApiKey).filter(ApiKey.revoked == False).all()

    for db_api_key in db_api_keys:
        if verify_api_key(api_key, db_api_key.key_hash):
            # Update last used timestamp
            db_api_key.last_used = datetime.utcnow()
            db.commit()

            # Add user info to request state for logging
            request.state.user_id = db_api_key.user_id
            request.state.api_key_id = db_api_key.id

            return db_api_key.user

    # Invalid API key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
        headers={"WWW-Authenticate": "Bearer"},
    )

def require_auth(user: Optional[User] = Depends(get_current_user)) -> User:
    """Require authentication - raises 401 if not authenticated"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_optional_user(user: Optional[User] = Depends(get_current_user)) -> Optional[User]:
    """Get user if authenticated, None otherwise"""
    return user