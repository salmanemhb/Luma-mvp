"""
Report model - generated CSRD reports
"""

from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from db import Base


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    year = Column(Integer, nullable=False)
    
    # Aggregated data
    total_co2e = Column(Numeric(12, 3))  # Total emissions in tonnes
    scope1_co2e = Column(Numeric(12, 3))
    scope2_co2e = Column(Numeric(12, 3))
    scope3_co2e = Column(Numeric(12, 3))
    
    # Detailed breakdown (JSON)
    breakdown = Column(JSONB)  # {"electricity": 12.3, "natural_gas": 5.1, ...}
    monthly_data = Column(JSONB)  # [{"month": "2024-01", "co2e": 10.5}, ...]
    
    # Data quality
    coverage = Column(Numeric(5, 2))  # Percentage (0-100)
    data_sources_count = Column(Integer)
    
    # File URLs
    pdf_url = Column(String(500))
    excel_url = Column(String(500))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    methodology = Column(String(1000))  # Brief description of calculation method
    
    # Relationships
    company = relationship("Company", back_populates="reports")
    
    def __repr__(self):
        return f"<Report {self.year} - {self.total_co2e}tCO2e>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": str(self.id),
            "company_id": str(self.company_id),
            "year": self.year,
            "total_co2e": float(self.total_co2e) if self.total_co2e else None,
            "scope1_co2e": float(self.scope1_co2e) if self.scope1_co2e else None,
            "scope2_co2e": float(self.scope2_co2e) if self.scope2_co2e else None,
            "scope3_co2e": float(self.scope3_co2e) if self.scope3_co2e else None,
            "breakdown": self.breakdown,
            "monthly_data": self.monthly_data,
            "coverage": float(self.coverage) if self.coverage else None,
            "data_sources_count": self.data_sources_count,
            "pdf_url": self.pdf_url,
            "excel_url": self.excel_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "methodology": self.methodology,
        }
