"""
Record model - represents extracted emission data points
"""

from sqlalchemy import Column, String, Numeric, Integer, Date, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from db import Base


class Record(Base):
    __tablename__ = "records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    
    # Extracted data
    supplier = Column(String(255))  # e.g., "Endesa", "Repsol"
    category = Column(String(100))  # e.g., "electricity", "natural_gas", "diesel"
    usage = Column(Numeric(12, 3))  # Numeric value (e.g., 1500.50)
    unit = Column(String(20))  # e.g., "kWh", "m3", "L"
    cost = Column(Numeric(10, 2))  # Cost in EUR
    
    # Emission calculation
    scope = Column(Integer)  # 1, 2, or 3
    co2e = Column(Numeric(12, 3))  # CO2 equivalent in tonnes
    factor_source = Column(String(100))  # e.g., "EEA 2023", "IPCC 2023"
    emission_factor = Column(Numeric(10, 6))  # The factor used
    
    # Metadata
    date = Column(Date)  # Transaction/invoice date
    invoice_number = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="records")
    
    def __repr__(self):
        return f"<Record {self.category} {self.usage}{self.unit} = {self.co2e}tCO2e>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": str(self.id),
            "document_id": str(self.document_id),
            "supplier": self.supplier,
            "category": self.category,
            "usage": float(self.usage) if self.usage else None,
            "unit": self.unit,
            "cost": float(self.cost) if self.cost else None,
            "scope": self.scope,
            "co2e": float(self.co2e) if self.co2e else None,
            "factor_source": self.factor_source,
            "emission_factor": float(self.emission_factor) if self.emission_factor else None,
            "date": self.date.isoformat() if self.date else None,
            "invoice_number": self.invoice_number,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
