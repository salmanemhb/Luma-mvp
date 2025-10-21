"""
Analyze router - document parsing and emission calculations
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import logging

from db import get_db
from models.company import Company
from models.document import Document, DocumentStatus, DocumentType
from models.record import Record
from routers.auth import get_current_company
from utils.ocr import extract_text_from_pdf
from utils.parser import parse_csv, parse_xlsx, parse_text
from utils.calculator import calculate_emissions
from utils.audit import log_analyze

router = APIRouter()
logger = logging.getLogger(__name__)


class AnalyzeResponse(BaseModel):
    document_id: str
    status: str
    records_extracted: int
    total_co2e: float
    scope1: float
    scope2: float
    scope3: float
    message: str


async def process_document_task(document_id: str, db_session):
    """
    Background task to process document
    """
    try:
        document = db_session.query(Document).filter(Document.id == document_id).first()
        if not document:
            return
        
        # Update status
        document.status = DocumentStatus.PROCESSING
        db_session.commit()
        
        # Extract data based on file type
        extracted_data = []
        
        if document.file_type == DocumentType.PDF:
            # OCR extraction
            text = extract_text_from_pdf(document.file_path)
            extracted_data = parse_text(text)
        
        elif document.file_type in [DocumentType.CSV]:
            extracted_data = parse_csv(document.file_path)
        
        elif document.file_type == DocumentType.XLSX:
            extracted_data = parse_xlsx(document.file_path)
        
        elif document.file_type in [DocumentType.PNG, DocumentType.JPG]:
            # OCR from image
            from utils.ocr import extract_text_from_image
            text = extract_text_from_image(document.file_path)
            extracted_data = parse_text(text)
        
        if not extracted_data:
            document.status = DocumentStatus.FAILED
            document.error_message = "No data could be extracted from document"
            db_session.commit()
            return
        
        # Calculate emissions for each record
        records = []
        for data in extracted_data:
            emission_result = calculate_emissions(data, db_session)
            if emission_result:
                record = Record(
                    document_id=document.id,
                    supplier=data.get('supplier'),
                    category=emission_result['category'],
                    usage=data.get('usage'),
                    unit=data.get('unit'),
                    cost=data.get('cost'),
                    scope=emission_result['scope'],
                    co2e=emission_result['co2e'],
                    factor_source=emission_result['factor_source'],
                    emission_factor=emission_result['emission_factor'],
                    date=data.get('date'),
                    invoice_number=data.get('invoice_number'),
                    notes=data.get('notes')
                )
                records.append(record)
        
        # Save records
        db_session.bulk_save_objects(records)
        document.status = DocumentStatus.COMPLETED
        document.processed_date = datetime.utcnow()
        db_session.commit()
        
        logger.info(f"✅ Document processed: {document.id} - {len(records)} records extracted")
        
    except Exception as e:
        logger.error(f"❌ Document processing failed: {str(e)}")
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        db_session.commit()


@router.post("/{document_id}", response_model=AnalyzeResponse)
async def analyze_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Analyze an uploaded document
    
    Extracts data, categorizes emissions, and calculates CO2e
    
    - **document_id**: ID of previously uploaded document
    """
    # Check document exists and belongs to company
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.company_id == company.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.status == DocumentStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document is already being processed"
        )
    
    # Process in background for large files
    # For MVP, we can process synchronously for simplicity
    try:
        # Extract data based on file type
        extracted_data = []
        
        if document.file_type == DocumentType.PDF:
            text = extract_text_from_pdf(document.file_path)
            extracted_data = parse_text(text)
        
        elif document.file_type == DocumentType.CSV:
            extracted_data = parse_csv(document.file_path)
        
        elif document.file_type == DocumentType.XLSX:
            extracted_data = parse_xlsx(document.file_path)
        
        elif document.file_type in [DocumentType.PNG, DocumentType.JPG]:
            from utils.ocr import extract_text_from_image
            text = extract_text_from_image(document.file_path)
            extracted_data = parse_text(text)
        
        if not extracted_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data could be extracted from document"
            )
        
        # Calculate emissions
        records = []
        total_co2e = 0
        scope_totals = {1: 0, 2: 0, 3: 0}
        
        for data in extracted_data:
            emission_result = calculate_emissions(data, db)
            if emission_result:
                record = Record(
                    document_id=document.id,
                    supplier=data.get('supplier'),
                    category=emission_result['category'],
                    usage=data.get('usage'),
                    unit=data.get('unit'),
                    cost=data.get('cost'),
                    scope=emission_result['scope'],
                    co2e=emission_result['co2e'],
                    factor_source=emission_result['factor_source'],
                    emission_factor=emission_result['emission_factor'],
                    date=data.get('date'),
                    invoice_number=data.get('invoice_number'),
                    notes=data.get('notes')
                )
                records.append(record)
                total_co2e += float(emission_result['co2e'])
                scope_totals[emission_result['scope']] += float(emission_result['co2e'])
        
        # Save records
        db.bulk_save_objects(records)
        document.status = DocumentStatus.COMPLETED
        document.processed_date = datetime.utcnow()
        db.commit()
        
        # Log analyze event
        log_analyze(
            company_id=str(company.id),
            document_id=str(document.id),
            records_count=len(records),
            total_co2e=total_co2e,
            db=db
        )
        
        logger.info(f"✅ Document analyzed: {document_id} - {len(records)} records")
        
        return AnalyzeResponse(
            document_id=str(document.id),
            status="completed",
            records_extracted=len(records),
            total_co2e=round(total_co2e, 3),
            scope1=round(scope_totals[1], 3),
            scope2=round(scope_totals[2], 3),
            scope3=round(scope_totals[3], 3),
            message=f"Successfully extracted {len(records)} emission records"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Analysis failed: {str(e)}")
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/status/{document_id}")
async def get_analysis_status(
    document_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Check analysis status of a document
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
    
    # Get records count
    records_count = db.query(Record).filter(Record.document_id == document_id).count()
    
    return {
        "document_id": str(document.id),
        "status": document.status.value,
        "processed_date": document.processed_date.isoformat() if document.processed_date else None,
        "records_count": records_count,
        "error_message": document.error_message
    }
