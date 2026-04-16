"""
API key management and rotation utilities
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import generate_api_key, hash_api_key
from app.models import ApiKey, User


class APIKeyManager:
    """API key generation, rotation, and management"""

    def __init__(self, key_length: int = 32):
        self.key_length = key_length

    def generate_key(self) -> str:
        """Generate a new API key"""
        return generate_api_key()

    def create_api_key(
        self,
        db: Session,
        user_id: int,
        name: Optional[str] = None,
        expires_in_days: Optional[int] = None
    ) -> ApiKey:
        """Create a new API key for a user"""
        api_key = self.generate_key()
        key_hash = hash_api_key(api_key)

        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        db_api_key = ApiKey(
            user_id=user_id,
            key_hash=key_hash,
            name=name,
            expires_at=expires_at
        )

        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)

        # Return the unhashed key (only time it's visible)
        db_api_key.plain_key = api_key
        return db_api_key

    def revoke_api_key(self, db: Session, key_id: int, user_id: int) -> bool:
        """Revoke an API key"""
        api_key = db.query(ApiKey).filter(
            ApiKey.id == key_id,
            ApiKey.user_id == user_id
        ).first()

        if api_key:
            api_key.revoked = True
            api_key.revoked_at = datetime.utcnow()
            db.commit()
            return True

        return False

    def rotate_api_key(
        self,
        db: Session,
        old_key_id: int,
        user_id: int,
        name: Optional[str] = None
    ) -> Optional[ApiKey]:
        """Rotate an API key (revoke old, create new)"""
        # Revoke old key
        if not self.revoke_api_key(db, old_key_id, user_id):
            return None

        # Create new key
        return self.create_api_key(db, user_id, name)

    def list_user_keys(self, db: Session, user_id: int) -> list:
        """List all API keys for a user"""
        keys = db.query(ApiKey).filter(ApiKey.user_id == user_id).all()
        return keys

    def validate_key_rotation(self, db: Session, user_id: int) -> dict:
        """
        Check if user should rotate their keys

        Returns dict with recommendations
        """
        keys = self.list_user_keys(db, user_id)

        recommendations = {
            "should_rotate": False,
            "reasons": [],
            "keys_to_rotate": []
        }

        for key in keys:
            reasons = []

            # Check if key is old (> 90 days)
            if key.created_at and (datetime.utcnow() - key.created_at).days > 90:
                reasons.append("Key is older than 90 days")
                recommendations["keys_to_rotate"].append(key.id)

            # Check if key has been used recently
            if key.last_used and (datetime.utcnow() - key.last_used).days > 30:
                reasons.append("Key hasn't been used in 30+ days")

            # Check if key is close to expiry
            if key.expires_at and (key.expires_at - datetime.utcnow()).days < 7:
                reasons.append("Key expires soon")

            if reasons:
                recommendations["should_rotate"] = True
                recommendations["reasons"].extend(reasons)

        return recommendations

    def cleanup_expired_keys(self, db: Session) -> int:
        """Clean up expired API keys"""
        expired_keys = db.query(ApiKey).filter(
            ApiKey.expires_at < datetime.utcnow(),
            ApiKey.revoked == False
        ).all()

        for key in expired_keys:
            key.revoked = True
            key.revoked_at = datetime.utcnow()

        db.commit()
        return len(expired_keys)


class APIKeyEndpoints:
    """API endpoints for API key management"""

    def __init__(self):
        self.key_manager = APIKeyManager()

    def create_key_endpoint(self, user: User, name: Optional[str], db: Session):
        """Create a new API key for the user"""
        api_key = self.key_manager.create_api_key(db, user.id, name)

        return {
            "success": True,
            "data": {
                "key_id": api_key.id,
                "api_key": api_key.plain_key,  # Only shown once
                "name": api_key.name,
                "created_at": api_key.created_at,
                "expires_at": api_key.expires_at
            },
            "message": "API key created successfully. Store this key securely - it won't be shown again."
        }

    def list_keys_endpoint(self, user: User, db: Session):
        """List user's API keys"""
        keys = self.key_manager.list_user_keys(db, user.id)

        return {
            "success": True,
            "data": {
                "keys": [
                    {
                        "id": key.id,
                        "name": key.name,
                        "created_at": key.created_at,
                        "last_used": key.last_used,
                        "expires_at": key.expires_at,
                        "revoked": key.revoked
                    } for key in keys
                ]
            }
        }

    def revoke_key_endpoint(self, user: User, key_id: int, db: Session):
        """Revoke an API key"""
        success = self.key_manager.revoke_api_key(db, key_id, user.id)

        if success:
            return {
                "success": True,
                "message": "API key revoked successfully"
            }
        else:
            return {
                "success": False,
                "error": {
                    "message": "API key not found or already revoked"
                }
            }

    def rotate_key_endpoint(self, user: User, key_id: int, name: Optional[str], db: Session):
        """Rotate an API key"""
        new_key = self.key_manager.rotate_api_key(db, key_id, user.id, name)

        if new_key:
            return {
                "success": True,
                "data": {
                    "old_key_id": key_id,
                    "new_key_id": new_key.id,
                    "new_api_key": new_key.plain_key,  # Only shown once
                    "name": new_key.name,
                    "created_at": new_key.created_at
                },
                "message": "API key rotated successfully. Use the new key - the old one is now revoked."
            }
        else:
            return {
                "success": False,
                "error": {
                    "message": "Failed to rotate API key"
                }
            }

    def rotation_check_endpoint(self, user: User, db: Session):
        """Check if user should rotate their keys"""
        recommendations = self.key_manager.validate_key_rotation(db, user.id)

        return {
            "success": True,
            "data": recommendations
        }


# Global instances
api_key_manager = APIKeyManager()
api_key_endpoints = APIKeyEndpoints()