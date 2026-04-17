import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.context import set_request_context
from app.models import ApiKey, User
from app.core.security import verify_api_key
from app.core.config import settings

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from API key with Redis caching and optimized lookup"""
    
    # 0. Check for RapidAPI headers first (they take precedence)
    rapidapi_proxy_secret = request.headers.get("x-rapidapi-proxy-secret")
    rapidapi_user_id = request.headers.get("x-rapidapi-user")
    
    if rapidapi_proxy_secret and settings.RAPIDAPI_PROXY_SECRET:
        if rapidapi_proxy_secret == settings.RAPIDAPI_PROXY_SECRET:
            # Trusted RapidAPI request
            email = f"rapidapi_{rapidapi_user_id}@pageiq.api"
            user = db.query(User).filter(User.email == email).first()
            if not user:
                # Auto-create RapidAPI user if it doesn't exist
                user = User(
                    email=email,
                    plan=request.headers.get("x-rapidapi-subscription", "free").lower()
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info(f"Auto-created RapidAPI user: {email}")
            
            request.state.user_id = user.id
            request.state.is_rapidapi = True
            set_request_context(user_id=user.id)
            return user
        else:
            logger.warning(f"RapidAPI secret mismatch: {rapidapi_proxy_secret[:4]}...")
    elif rapidapi_proxy_secret:
        logger.warning("RapidAPI secret provided but RAPIDAPI_PROXY_SECRET not set in settings")

    if not credentials:
        return None

    api_key = credentials.credentials
    if not api_key:
        return None

    # 1. Try Redis cache first
    redis = get_redis()
    cache_key = f"auth:apikey:v1:{api_key[:8]}:{api_key[-8:]}"
    cached_user_data = redis.get(cache_key)

    if cached_user_data:
        try:
            user_info = json.loads(cached_user_data)
            user_id = user_info.get("user_id")
            # Verify full key against hash if stored in cache, or just trust cache
            # For maximum security, we should still verify, but we can store hash in cache
            if verify_api_key(api_key, user_info.get("key_hash")):
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    request.state.user_id = user.id
                    request.state.api_key_id = user_info.get("api_key_id")
                    set_request_context(user_id=user.id)
                    return user
        except (json.JSONDecodeError, AttributeError):
            pass

    # 2. Optimized Database Lookup
    # Search by prefix first (very fast indexed lookup)
    prefix = api_key[:8]
    db_api_keys = db.query(ApiKey).filter(
        ApiKey.key_prefix == prefix,
        ApiKey.revoked == False
    ).all()

    for db_api_key in db_api_keys:
        if verify_api_key(api_key, db_api_key.key_hash):
            # Check expiration
            if db_api_key.expires_at and db_api_key.expires_at < datetime.utcnow():
                continue

            # Update last used timestamp (async/background would be better for performance)
            db_api_key.last_used = datetime.utcnow()
            db.commit()

            # Cache the result for 5 minutes
            user_data = {
                "user_id": db_api_key.user_id,
                "api_key_id": db_api_key.id,
                "key_hash": db_api_key.key_hash
            }
            redis.set(cache_key, json.dumps(user_data), ex=300)

            request.state.user_id = db_api_key.user_id
            request.state.api_key_id = db_api_key.id
            set_request_context(user_id=db_api_key.user_id)

            return db_api_key.user

    # 3. Fallback for old keys without prefix (if any)
    # This can be removed once migration is complete
    db_api_keys_no_prefix = db.query(ApiKey).filter(
        ApiKey.key_prefix == "",
        ApiKey.revoked == False
    ).all()
    for db_api_key in db_api_keys_no_prefix:
        if verify_api_key(api_key, db_api_key.key_hash):
            # ... same logic as above ...
            db_api_key.last_used = datetime.utcnow()
            db.commit()
            return db_api_key.user

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