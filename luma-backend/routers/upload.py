"""
Upload router - handles file uploads
"""

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
import uuid
from datetime import datetime
import logging

from db import get_db, UPLOAD_DIR
from models.company import Company
from models.document import Document, DocumentType, DocumentStatus
from routers.auth import get_current_company
from utils.audit import log_upload

router = APIRouter()
logger = logging.getLogger(__name__)

# Configuration
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", 15))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".csv", ".xlsx", ".xls", ".png", ".jpg", ".jpeg"}


def get_file_extension(filename: str) -> str:
    """Get lowercase file extension"""
    return os.path.splitext(filename)[1].lower()


def validate_file_type(filename: str) -> DocumentType:
    """Validate and return document type"""
    ext = get_file_extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {ext} not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Map extension to DocumentType
    type_map = {
        ".pdf": DocumentType.PDF,
        ".csv": DocumentType.CSV,
        ".xlsx": DocumentType.XLSX,
        ".xls": DocumentType.XLSX,
        ".png": DocumentType.PNG,
        ".jpg": DocumentType.JPG,
        ".jpeg": DocumentType.JPG,
    }
    return type_map.get(ext)


def human_readable_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


@router.post("/")
async def upload_document(
    file: UploadFile = File(...),
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Upload a document (PDF, CSV, XLSX, or image)
    
    - **file**: The document file to upload (max 15MB)
    
    Returns document_id and upload status
    """
    try:
        # Validate file size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {MAX_UPLOAD_MB}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file"
            )
        
        # Validate file type
        file_type = validate_file_type(file.filename)
        
        # Generate unique filename
        file_ext = get_file_extension(file.filename)
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Create company-specific directory
        company_dir = os.path.join(UPLOAD_DIR, str(company.id))
        os.makedirs(company_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(company_dir, unique_filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Create database record
        document = Document(
            company_id=company.id,
            filename=file.filename,
            file_path=file_path,
            file_type=file_type,
            file_size=human_readable_size(file_size),
            status=DocumentStatus.UPLOADED
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Log upload event
        log_upload(
            company_id=str(company.id),
            filename=file.filename,
            file_size=human_readable_size(file_size),
            db=db
        )
        
        logger.info(f"✅ Document uploaded: {file.filename} ({human_readable_size(file_size)}) - {document.id}")
        
        return {
            "document_id": str(document.id),
            "filename": file.filename,
            "file_size": human_readable_size(file_size),
            "file_type": file_type.value,
            "status": "uploaded",
            "message": "File uploaded successfully. Use /analyze endpoint to process."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/documents")
async def list_documents(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    List all documents for current company
    """
    documents = db.query(Document).filter(
        Document.company_id == company.id
    ).order_by(Document.upload_date.desc()).all()
    
    return {
        "total": len(documents),
        "documents": [doc.to_dict() for doc in documents]
    }


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Get document details
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.company_id == company.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document.to_dict()


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Delete a document and its associated records
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.company_id == company.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete physical file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # Delete from database (cascade deletes records)
    db.delete(document)
    db.commit()
    
    logger.info(f"🗑️ Document deleted: {document.filename}")
    
    return {"message": "Document deleted successfully"}
