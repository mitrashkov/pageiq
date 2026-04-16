"""
GDPR compliance utilities for data export and deletion
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, WebsiteAnalysis, ApiKey
from app.services.quota import quota_service


class GDPRComplianceManager:
    """GDPR compliance manager for data export and deletion"""

    def export_user_data(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Export all user data for GDPR Article 20 (data portability)

        Returns comprehensive user data export
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Get all user analyses
        analyses = db.query(WebsiteAnalysis).filter(
            WebsiteAnalysis.user_id == user_id
        ).all()

        # Get all API keys (without hashes)
        api_keys = db.query(ApiKey).filter(
            ApiKey.user_id == user_id
        ).all()

        # Get quota usage history (simplified)
        quota_info = quota_service.get_quota_info(user, db)

        # Structure the export data
        export_data = {
            "export_metadata": {
                "user_id": user.id,
                "export_date": datetime.utcnow().isoformat(),
                "gdpr_article": "Article 20 - Right to data portability",
                "data_controller": "PageIQ API",
                "export_format": "JSON",
                "data_retention_policy": "User data retained for service provision, deleted upon account closure"
            },
            "user_profile": {
                "id": user.id,
                "email": user.email,
                "plan": user.plan,
                "status": user.status,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "quota_used": user.quota_used,
                "quota_limit": user.quota_limit
            },
            "api_keys": [
                {
                    "id": key.id,
                    "name": key.name,
                    "created_at": key.created_at.isoformat() if key.created_at else None,
                    "last_used": key.last_used.isoformat() if key.last_used else None,
                    "revoked": key.revoked,
                    "revoked_at": key.revoked_at.isoformat() if key.revoked_at else None,
                    "expires_at": key.expires_at.isoformat() if key.expires_at else None
                } for key in api_keys
            ],
            "website_analyses": [
                {
                    "id": analysis.id,
                    "url": analysis.url,
                    "title": analysis.title,
                    "description": analysis.description,
                    "logo": analysis.logo,
                    "favicon": analysis.favicon,
                    "emails": analysis.emails,
                    "phones": analysis.phones,
                    "socials": analysis.socials,
                    "tech_stack": analysis.tech_stack,
                    "industry_guess": analysis.industry_guess,
                    "language": analysis.language,
                    "country_guess": analysis.country_guess,
                    "keywords": analysis.keywords,
                    "schema_org": analysis.schema_org,
                    "og_tags": analysis.og_tags,
                    "screenshot_url": analysis.screenshot_url,
                    "page_speed_score": analysis.page_speed_score,
                    "ai_summary": analysis.ai_summary,
                    "timestamp": analysis.timestamp.isoformat() if analysis.timestamp else None,
                    "processing_time_ms": analysis.processing_time_ms,
                    "cached": analysis.cached
                } for analysis in analyses
            ],
            "usage_statistics": quota_info,
            "data_processing_agreement": {
                "legal_basis": "Contract (Terms of Service)",
                "purpose": "Website intelligence analysis service",
                "data_categories": [
                    "Account information (email, plan details)",
                    "API usage data",
                    "Website analysis results",
                    "Technical metadata"
                ],
                "retention_period": "Account active: unlimited, Account closed: 30 days",
                "data_recipients": "Service infrastructure providers",
                "international_transfers": "Data stored in EU/US compliant regions"
            }
        }

        return export_data

    def delete_user_data(self, db: Session, user_id: int, confirm_deletion: bool = False) -> Dict[str, Any]:
        """
        Delete all user data for GDPR Article 17 (right to erasure)

        This is a destructive operation that permanently removes user data.
        """
        if not confirm_deletion:
            return {
                "success": False,
                "error": {
                    "message": "Data deletion requires explicit confirmation",
                    "code": "CONFIRMATION_REQUIRED"
                }
            }

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "success": False,
                "error": {
                    "message": "User not found",
                    "code": "USER_NOT_FOUND"
                }
            }

        deletion_summary = {
            "user_id": user_id,
            "deletion_timestamp": datetime.utcnow().isoformat(),
            "gdpr_article": "Article 17 - Right to erasure",
            "data_removed": []
        }

        try:
            # Delete all website analyses
            analyses_deleted = db.query(WebsiteAnalysis).filter(
                WebsiteAnalysis.user_id == user_id
            ).delete()
            deletion_summary["data_removed"].append(f"{analyses_deleted} website analyses")

            # Delete all API keys
            keys_deleted = db.query(ApiKey).filter(
                ApiKey.user_id == user_id
            ).delete()
            deletion_summary["data_removed"].append(f"{keys_deleted} API keys")

            # Delete user account
            db.delete(user)
            deletion_summary["data_removed"].append("user account")

            # Commit the deletion
            db.commit()

            return {
                "success": True,
                "data": deletion_summary,
                "message": "All user data has been permanently deleted"
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "message": f"Data deletion failed: {str(e)}",
                    "code": "DELETION_FAILED"
                }
            }

    def anonymize_user_data(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Anonymize user data instead of deleting (GDPR Article 17 alternative)

        This keeps usage statistics but removes personal identifiable information.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "success": False,
                "error": {
                    "message": "User not found",
                    "code": "USER_NOT_FOUND"
                }
            }

        try:
            # Anonymize user email
            user.email = f"deleted-user-{user.id}@anonymized.pageiq.com"
            user.status = "anonymized"
            user.updated_at = datetime.utcnow()

            # Anonymize API keys
            api_keys = db.query(ApiKey).filter(ApiKey.user_id == user_id).all()
            for key in api_keys:
                key.revoked = True
                key.revoked_at = datetime.utcnow()

            # Anonymize website analyses (remove personal data but keep technical insights)
            analyses = db.query(WebsiteAnalysis).filter(
                WebsiteAnalysis.user_id == user_id
            ).all()

            for analysis in analyses:
                # Keep technical data but remove potentially sensitive info
                analysis.title = "[ANONYMIZED]" if analysis.title else None
                analysis.description = "[ANONYMIZED]" if analysis.description else None
                analysis.emails = []  # Remove email addresses
                analysis.phones = []  # Remove phone numbers
                # Keep technical data like tech_stack, keywords, etc.

            db.commit()

            return {
                "success": True,
                "message": "User data has been anonymized",
                "data": {
                    "user_id": user_id,
                    "anonymized_at": datetime.utcnow().isoformat(),
                    "analyses_kept": len(analyses),
                    "api_keys_revoked": len(api_keys)
                }
            }

        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "message": f"Data anonymization failed: {str(e)}",
                    "code": "ANONYMIZATION_FAILED"
                }
            }

    def get_data_retention_info(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Provide information about data retention for GDPR Article 13/14
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Count user's data
        analyses_count = db.query(WebsiteAnalysis).filter(
            WebsiteAnalysis.user_id == user_id
        ).count()

        keys_count = db.query(ApiKey).filter(
            ApiKey.user_id == user_id
        ).count()

        return {
            "data_inventory": {
                "user_profile": 1,
                "api_keys": keys_count,
                "website_analyses": analyses_count,
                "total_data_points": 1 + keys_count + analyses_count
            },
            "retention_policy": {
                "user_account": "Retained while account is active",
                "api_keys": "Retained while valid, deleted when expired/revoked",
                "website_analyses": "Retained while account is active",
                "anonymized_data": "Deleted after 30 days",
                "audit_logs": "Deleted after 90 days"
            },
            "user_rights": {
                "access": "Request data export anytime",
                "rectification": "Update account information",
                "erasure": "Request complete data deletion",
                "portability": "Export data in machine-readable format",
                "restriction": "Limit processing of personal data",
                "objection": "Object to data processing"
            },
            "contact_information": {
                "data_controller": "PageIQ API",
                "privacy_officer": "privacy@pageiq.com",
                "response_time": "Within 30 days"
            }
        }


class GDPRComplianceEndpoints:
    """API endpoints for GDPR compliance"""

    def __init__(self):
        self.gdpr_manager = GDPRComplianceManager()

    def export_data_endpoint(self, user: User, db: Session):
        """Export user data endpoint"""
        try:
            export_data = self.gdpr_manager.export_user_data(db, user.id)

            return {
                "success": True,
                "data": export_data,
                "message": "Data export completed. Download the data using the export link."
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "message": f"Data export failed: {str(e)}",
                    "code": "EXPORT_FAILED"
                }
            }

    def delete_data_endpoint(self, user: User, confirmation: str, db: Session):
        """Delete user data endpoint"""
        if confirmation != "DELETE_ALL_MY_DATA":
            return {
                "success": False,
                "error": {
                    "message": "Invalid confirmation phrase",
                    "code": "INVALID_CONFIRMATION"
                }
            }

        result = self.gdpr_manager.delete_user_data(db, user.id, confirm_deletion=True)

        if result["success"]:
            # In a real implementation, you'd want to:
            # 1. Send confirmation email
            # 2. Log the deletion for audit purposes
            # 3. Invalidate any active sessions
            pass

        return result

    def anonymize_data_endpoint(self, user: User, db: Session):
        """Anonymize user data endpoint"""
        result = self.gdpr_manager.anonymize_user_data(db, user.id)
        return result

    def data_retention_info_endpoint(self, user: User, db: Session):
        """Data retention information endpoint"""
        try:
            info = self.gdpr_manager.get_data_retention_info(db, user.id)
            return {
                "success": True,
                "data": info
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "message": f"Failed to retrieve retention info: {str(e)}",
                    "code": "RETENTION_INFO_FAILED"
                }
            }


# Global instances
gdpr_manager = GDPRComplianceManager()
gdpr_endpoints = GDPRComplianceEndpoints()