from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    # Store hashed key and a prefix for fast lookup
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_used: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User", backref="api_keys")

