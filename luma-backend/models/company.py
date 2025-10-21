"""
Company model - represents client companies using Luma
"""

from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from db import Base


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    sector = Column(String(100))  # Manufacturing, Construction, etc.
    country = Column(String(2), default="ES")  # ISO country code
    size = Column(Integer)  # Number of employees
    cif = Column(String(20))  # Spanish tax ID (optional)
    cnae_code = Column(String(10))  # Spanish sector classification (future use)
    email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="company", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company {self.name} ({self.country})>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": str(self.id),
            "name": self.name,
            "sector": self.sector,
            "country": self.country,
            "size": self.size,
            "cif": self.cif,
            "cnae_code": self.cnae_code,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
