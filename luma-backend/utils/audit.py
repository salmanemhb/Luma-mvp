"""
Audit logging utilities - track usage events
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from models.usage_log import UsageLog

logger = logging.getLogger(__name__)


def log_event(
    company_id: str,
    event_type: str,
    db: Session,
    details: Optional[Dict] = None
):
    """
    Log a usage event to the database
    
    Args:
        company_id: UUID of the company
        event_type: Type of event (upload, analyze, report_generated, login)
        db: Database session
        details: Optional dictionary with event-specific details
    """
    try:
        log_entry = UsageLog(
            company_id=company_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            details=details or {}
        )
        
        db.add(log_entry)
        db.commit()
        
        logger.debug(f"📊 Logged event: {event_type} for company {company_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to log event: {str(e)}")
        db.rollback()


def log_upload(company_id: str, filename: str, file_size: str, db: Session):
    """Log document upload event"""
    log_event(
        company_id=company_id,
        event_type="upload",
        db=db,
        details={
            "filename": filename,
            "file_size": file_size
        }
    )


def log_analyze(
    company_id: str,
    document_id: str,
    records_count: int,
    total_co2e: float,
    db: Session
):
    """Log document analysis event"""
    log_event(
        company_id=company_id,
        event_type="analyze",
        db=db,
        details={
            "document_id": document_id,
            "records_count": records_count,
            "total_co2e": total_co2e
        }
    )


def log_report_generated(
    company_id: str,
    report_id: str,
    year: int,
    total_co2e: float,
    pdf_url: str,
    db: Session
):
    """Log report generation event"""
    log_event(
        company_id=company_id,
        event_type="report_generated",
        db=db,
        details={
            "report_id": report_id,
            "year": year,
            "total_co2e": total_co2e,
            "pdf_url": pdf_url
        }
    )


def log_login(company_id: str, email: str, db: Session):
    """Log user login event"""
    log_event(
        company_id=company_id,
        event_type="login",
        db=db,
        details={
            "email": email
        }
    )
    
    # Update last_login timestamp in companies table
    try:
        from models.company import Company
        company = db.query(Company).filter(Company.id == company_id).first()
        if company:
            company.last_login = datetime.utcnow()
            db.commit()
    except Exception as e:
        logger.error(f"Failed to update last_login: {str(e)}")
