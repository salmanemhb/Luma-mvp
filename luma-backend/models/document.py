"""
Document model - represents uploaded files
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from db import Base


class DocumentType(enum.Enum):
    """Supported document types"""
    PDF = "pdf"
    CSV = "csv"
    XLSX = "xlsx"
    PNG = "png"
    JPG = "jpg"


class DocumentStatus(enum.Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Local path or Supabase URL
    file_type = Column(Enum(DocumentType), nullable=False)
    file_size = Column(String(50))  # Human-readable size
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed_date = Column(DateTime)
    error_message = Column(String(1000))
    
    # Relationships
    company = relationship("Company", back_populates="documents")
    records = relationship("Record", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document {self.filename} ({self.status.value})>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": str(self.id),
            "company_id": str(self.company_id),
            "filename": self.filename,
            "file_path": self.file_path,
            "file_type": self.file_type.value if self.file_type else None,
            "file_size": self.file_size,
            "status": self.status.value if self.status else None,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "processed_date": self.processed_date.isoformat() if self.processed_date else None,
            "error_message": self.error_message,
        }
