"""
Usage Log model - tracks company activity
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from db import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), nullable=False)  # upload, analyze, report_generated, login
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    details = Column(JSONB, default={})  # Flexible JSON for event-specific data
    
    # Relationships
    company = relationship("Company", backref="usage_logs")
    
    def __repr__(self):
        return f"<UsageLog {self.event_type} @ {self.timestamp}>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": str(self.id),
            "company_id": str(self.company_id),
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "details": self.details,
        }
