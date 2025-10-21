"""
Waitlist submission model for landing page.
Added to MVP backend for unified database.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from db import Base


class WaitlistSubmission(Base):
    """
    Waitlist submissions from landing page (getluma.es).
    These users can be promoted to full Company accounts.
    """
    __tablename__ = "waitlist_submissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    company = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    role = Column(String(50), nullable=False)  # sme, consultant, corporate, other
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<WaitlistSubmission {self.email} - {self.company}>"
