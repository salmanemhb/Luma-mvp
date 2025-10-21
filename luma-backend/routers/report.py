"""
Report router - CSRD report generation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime
from typing import Optional
import os
import logging

from db import get_db
from models.company import Company
from models.record import Record
from models.document import Document
from models.report import Report
from routers.auth import get_current_company
from utils.report_generator import generate_pdf_report, generate_excel_report
from utils.audit import log_report_generated

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{company_id}")
async def generate_report(
    company_id: str,
    year: Optional[int] = Query(None, description="Report year (default: current year)"),
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Generate CSRD-Lite report for a given year
    
    Creates both PDF and Excel versions
    """
    # Verify company access
    if str(company.id) != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Default to current year
    if not year:
        year = datetime.now().year
    
    # Get all documents for company
    document_ids = db.query(Document.id).filter(
        Document.company_id == company.id
    ).subquery()
    
    # Get records for the year
    records = db.query(Record).filter(
        Record.document_id.in_(document_ids),
        extract('year', Record.date) == year
    ).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No emission data found for year {year}"
        )
    
    # Calculate aggregates
    scope_totals = db.query(
        Record.scope,
        func.sum(Record.co2e).label('total')
    ).filter(
        Record.document_id.in_(document_ids),
        extract('year', Record.date) == year
    ).group_by(Record.scope).all()
    
    scope1 = scope2 = scope3 = 0
    for scope, total in scope_totals:
        if scope == 1:
            scope1 = float(total or 0)
        elif scope == 2:
            scope2 = float(total or 0)
        elif scope == 3:
            scope3 = float(total or 0)
    
    total_co2e = scope1 + scope2 + scope3
    
    # Category breakdown
    category_data = db.query(
        Record.category,
        func.sum(Record.co2e).label('total')
    ).filter(
        Record.document_id.in_(document_ids),
        extract('year', Record.date) == year
    ).group_by(Record.category).all()
    
    breakdown = {cat: float(total or 0) for cat, total in category_data}
    
    # Monthly data
    monthly_data = db.query(
        func.date_trunc('month', Record.date).label('month'),
        func.sum(Record.co2e).label('total')
    ).filter(
        Record.document_id.in_(document_ids),
        extract('year', Record.date) == year
    ).group_by(func.date_trunc('month', Record.date)).order_by('month').all()
    
    monthly_list = [
        {"month": month.strftime('%Y-%m') if month else None, "co2e": float(total or 0)}
        for month, total in monthly_data
    ]
    
    # Data quality
    total_records = len(records)
    records_with_date = sum(1 for r in records if r.date)
    coverage = (records_with_date / total_records * 100) if total_records > 0 else 0
    
    # Generate reports
    try:
        report_data = {
            "company": company,
            "year": year,
            "total_co2e": total_co2e,
            "scope1": scope1,
            "scope2": scope2,
            "scope3": scope3,
            "breakdown": breakdown,
            "monthly_data": monthly_list,
            "coverage": coverage,
            "records": records
        }
        
        pdf_path = generate_pdf_report(report_data)
        excel_path = generate_excel_report(report_data)
        
        # Save report record
        report = Report(
            company_id=company.id,
            year=year,
            total_co2e=total_co2e,
            scope1_co2e=scope1,
            scope2_co2e=scope2,
            scope3_co2e=scope3,
            breakdown=breakdown,
            monthly_data=monthly_list,
            coverage=coverage,
            data_sources_count=total_records,
            pdf_url=pdf_path,
            excel_url=excel_path,
            methodology="Emissions calculated using IPCC/EEA/DEFRA emission factors. Scope 1: direct emissions. Scope 2: indirect emissions from purchased energy. Scope 3: other indirect emissions."
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        # Log report generation event
        log_report_generated(
            company_id=str(company.id),
            report_id=str(report.id),
            year=year,
            total_co2e=total_co2e,
            pdf_url=pdf_path,
            db=db
        )
        
        logger.info(f"✅ Report generated for {company.name} - {year}")
        
        return {
            "report_id": str(report.id),
            "year": year,
            "total_co2e": round(total_co2e, 3),
            "scope1_co2e": round(scope1, 3),
            "scope2_co2e": round(scope2, 3),
            "scope3_co2e": round(scope3, 3),
            "coverage": round(coverage, 2),
            "pdf_url": pdf_path,
            "excel_url": excel_path,
            "message": "Report generated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Report generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}"
        )


@router.get("/list")
async def list_reports(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    List all reports for company
    """
    reports = db.query(Report).filter(
        Report.company_id == company.id
    ).order_by(Report.year.desc(), Report.created_at.desc()).all()
    
    return {
        "total": len(reports),
        "reports": [report.to_dict() for report in reports]
    }


@router.get("/{report_id}")
async def get_report(
    report_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Get report details
    """
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.company_id == company.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report.to_dict()


@router.get("/{report_id}/download/pdf")
async def download_pdf(
    report_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Download PDF report
    """
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.company_id == company.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if not report.pdf_url or not os.path.exists(report.pdf_url):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found"
        )
    
    return FileResponse(
        report.pdf_url,
        media_type="application/pdf",
        filename=f"luma_csrd_report_{company.name}_{report.year}.pdf"
    )


@router.get("/{report_id}/download/excel")
async def download_excel(
    report_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Download Excel report
    """
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.company_id == company.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if not report.excel_url or not os.path.exists(report.excel_url):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Excel file not found"
        )
    
    return FileResponse(
        report.excel_url,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"luma_csrd_report_{company.name}_{report.year}.xlsx"
    )
