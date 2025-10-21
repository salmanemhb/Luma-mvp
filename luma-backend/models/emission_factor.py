"""
Emission Factor model - reference data for CO2e calculations
"""

from sqlalchemy import Column, String, Numeric, Integer, UniqueConstraint
from db import Base


class EmissionFactor(Base):
    __tablename__ = "emission_factors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False)  # e.g., "electricity", "diesel"
    unit = Column(String(20), nullable=False)  # e.g., "kWh", "L", "tonne_km"
    factor = Column(Numeric(10, 6), nullable=False)  # CO2e per unit
    source = Column(String(100), nullable=False)  # e.g., "EEA", "IPCC", "DEFRA"
    year = Column(Integer, nullable=False)  # Year of data
    region = Column(String(10), default="EU")  # EU, ES, etc.
    notes = Column(String(500))
    
    __table_args__ = (
        UniqueConstraint('category', 'unit', 'source', 'year', name='uix_factor'),
    )
    
    def __repr__(self):
        return f"<EmissionFactor {self.category} {self.factor} kgCO2e/{self.unit}>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "category": self.category,
            "unit": self.unit,
            "factor": float(self.factor),
            "source": self.source,
            "year": self.year,
            "region": self.region,
            "notes": self.notes,
        }
