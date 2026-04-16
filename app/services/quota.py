from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.core.config import settings


class QuotaService:
    """Service for managing user quotas and usage tracking"""

    def __init__(self):
        self.default_limits = {
            "free": settings.FREE_TIER_REQUESTS_PER_MONTH,
            "basic": 5000,
            "pro": 50000,
            "business": 500000,
            "enterprise": float('inf')  # Unlimited
        }

    def check_quota(self, user: Optional[User], db: Session) -> Tuple[bool, int, int]:
        """
        Check if user has quota remaining.

        Args:
            user: User object or None for anonymous
            db: Database session

        Returns:
            Tuple of (allowed: bool, remaining: int, limit: int)
        """
        if user is None:
            # Anonymous users get free tier limits
            limit = self.default_limits["free"]
            # For anonymous users, we don't track usage persistently
            # In production, you'd track by IP or session
            remaining = limit
            return True, remaining, limit

        # Get user's plan and current usage
        plan = user.plan
        limit = self._get_plan_limit(plan)
        current_usage = user.quota_used

        remaining = max(0, limit - current_usage)
        allowed = remaining > 0 or plan == "enterprise"

        return allowed, remaining, limit

    def consume_quota(self, user: User, amount: int = 1, db: Session = None) -> bool:
        """
        Consume quota for a user.

        Args:
            user: User object
            amount: Amount to consume (default 1)
            db: Database session (if None, will get from dependency)

        Returns:
            True if successful, False if insufficient quota
        """
        if db is None:
            # This would be handled by dependency injection in real usage
            return False

        allowed, remaining, _ = self.check_quota(user, db)

        if not allowed and user.plan != "enterprise":
            return False

        # Update usage
        user.quota_used += amount
        user.updated_at = datetime.utcnow()
        db.commit()

        return True

    def reset_quota_if_needed(self, user: User, db: Session):
        """
        Reset quota usage if the billing period has reset.

        For simplicity, we'll reset monthly on the 1st.
        In production, this would be more sophisticated.
        """
        now = datetime.utcnow()
        last_reset = user.updated_at or user.created_at

        # Reset if it's a new month
        if now.month != last_reset.month or now.year != last_reset.year:
            user.quota_used = 0
            user.updated_at = now
            db.commit()

    def _get_plan_limit(self, plan: str) -> int:
        """Get quota limit for a plan"""
        return self.default_limits.get(plan, self.default_limits["free"])

    def get_quota_info(self, user: Optional[User], db: Session) -> dict:
        """
        Get detailed quota information for a user.

        Returns:
            Dict with quota information
        """
        allowed, remaining, limit = self.check_quota(user, db)

        if user:
            self.reset_quota_if_needed(user, db)

        return {
            "allowed": allowed,
            "remaining": remaining,
            "limit": limit,
            "used": user.quota_used if user else 0,
            "plan": user.plan if user else "free",
            "reset_date": self._get_next_reset_date()
        }

    def _get_next_reset_date(self) -> str:
        """Get next quota reset date (1st of next month)"""
        now = datetime.utcnow()
        if now.month == 12:
            next_month = 1
            next_year = now.year + 1
        else:
            next_month = now.month + 1
            next_year = now.year

        next_reset = datetime(next_year, next_month, 1)
        return next_reset.isoformat()


# Global quota service instance
quota_service = QuotaService()