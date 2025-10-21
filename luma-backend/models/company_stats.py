"""
Company Stats model - cached monthly statistics
"""

from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from db import Base


class CompanyStats(Base):
    __tablename__ = "company_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    month = Column(Date, nullable=False)  # First day of month (YYYY-MM-01)
    
    # Aggregated metrics
    uploads_count = Column(Integer, default=0)
    records_count = Column(Integer, default=0)
    total_emissions = Column(Numeric(12, 3), default=0)  # tCO2e
    reports_generated = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    
    __table_args__ = (
        UniqueConstraint('company_id', 'month', name='uix_company_month'),
    )
    
    # Relationships
    company = relationship("Company", backref="stats")
    
    def __repr__(self):
        return f"<CompanyStats {self.month} - {self.total_emissions}tCO2e>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": str(self.id),
            "company_id": str(self.company_id),
            "month": self.month.isoformat() if self.month else None,
            "uploads_count": self.uploads_count,
            "records_count": self.records_count,
            "total_emissions": float(self.total_emissions) if self.total_emissions else 0,
            "reports_generated": self.reports_generated,
            "active_users": self.active_users,
        }
