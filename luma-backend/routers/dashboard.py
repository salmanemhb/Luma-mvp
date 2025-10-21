"""
Dashboard router - emission data aggregation and visualization
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, date
from typing import Optional
import logging

from db import get_db
from models.company import Company
from models.record import Record
from models.document import Document
from routers.auth import get_current_company

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def get_dashboard_data(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None, description="Filter by year"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter")
):
    """
    Get aggregated emission data for dashboard
    
    Returns:
    - Total emissions by scope
    - Monthly breakdown
    - Top emission sources
    - Category breakdown
    """
    # Get all documents for company
    document_ids = db.query(Document.id).filter(
        Document.company_id == company.id
    ).subquery()
    
    # Base query
    query = db.query(Record).filter(Record.document_id.in_(document_ids))
    
    # Apply filters
    if year:
        query = query.filter(extract('year', Record.date) == year)
    if start_date:
        query = query.filter(Record.date >= start_date)
    if end_date:
        query = query.filter(Record.date <= end_date)
    
    # Total emissions by scope
    scope_totals = db.query(
        Record.scope,
        func.sum(Record.co2e).label('total')
    ).filter(
        Record.document_id.in_(document_ids)
    ).group_by(Record.scope).all()
    
    scope_breakdown = {
        "scope1": 0,
        "scope2": 0,
        "scope3": 0
    }
    total_co2e = 0
    
    for scope, total in scope_totals:
        if scope:
            scope_breakdown[f"scope{scope}"] = float(total or 0)
            total_co2e += float(total or 0)
    
    # Monthly breakdown
    monthly_data = db.query(
        func.date_trunc('month', Record.date).label('month'),
        func.sum(Record.co2e).label('total')
    ).filter(
        Record.document_id.in_(document_ids),
        Record.date.isnot(None)
    ).group_by(
        func.date_trunc('month', Record.date)
    ).order_by('month').all()
    
    monthly_breakdown = [
        {
            "month": month.strftime('%Y-%m') if month else None,
            "co2e": float(total or 0)
        }
        for month, total in monthly_data
    ]
    
    # Category breakdown (top sources)
    category_data = db.query(
        Record.category,
        func.sum(Record.co2e).label('total'),
        func.count(Record.id).label('count')
    ).filter(
        Record.document_id.in_(document_ids)
    ).group_by(
        Record.category
    ).order_by(
        func.sum(Record.co2e).desc()
    ).limit(10).all()
    
    category_breakdown = [
        {
            "category": cat,
            "co2e": float(total or 0),
            "count": count
        }
        for cat, total, count in category_data
    ]
    
    # Supplier breakdown
    supplier_data = db.query(
        Record.supplier,
        func.sum(Record.co2e).label('total')
    ).filter(
        Record.document_id.in_(document_ids),
        Record.supplier.isnot(None)
    ).group_by(
        Record.supplier
    ).order_by(
        func.sum(Record.co2e).desc()
    ).limit(5).all()
    
    top_suppliers = [
        {
            "supplier": supplier,
            "co2e": float(total or 0)
        }
        for supplier, total in supplier_data
    ]
    
    # Data quality metrics
    total_records = db.query(func.count(Record.id)).filter(
        Record.document_id.in_(document_ids)
    ).scalar()
    
    records_with_date = db.query(func.count(Record.id)).filter(
        Record.document_id.in_(document_ids),
        Record.date.isnot(None)
    ).scalar()
    
    data_coverage = (records_with_date / total_records * 100) if total_records > 0 else 0
    
    return {
        "summary": {
            "total_co2e": round(total_co2e, 3),
            "scope1_co2e": round(scope_breakdown["scope1"], 3),
            "scope2_co2e": round(scope_breakdown["scope2"], 3),
            "scope3_co2e": round(scope_breakdown["scope3"], 3),
            "total_records": total_records,
            "data_coverage": round(data_coverage, 2)
        },
        "monthly_data": monthly_breakdown,
        "category_breakdown": category_breakdown,
        "top_suppliers": top_suppliers,
        "scope_breakdown": scope_breakdown
    }


@router.get("/records")
async def get_emission_records(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Get paginated emission records
    """
    # Get all documents for company
    document_ids = db.query(Document.id).filter(
        Document.company_id == company.id
    ).subquery()
    
    # Get records
    records = db.query(Record).filter(
        Record.document_id.in_(document_ids)
    ).order_by(
        Record.date.desc().nullslast()
    ).limit(limit).offset(offset).all()
    
    total = db.query(func.count(Record.id)).filter(
        Record.document_id.in_(document_ids)
    ).scalar()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "records": [record.to_dict() for record in records]
    }


@router.get("/stats")
async def get_stats(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Get quick statistics
    """
    # Get all documents for company
    document_ids = db.query(Document.id).filter(
        Document.company_id == company.id
    ).subquery()
    
    total_documents = db.query(func.count(Document.id)).filter(
        Document.company_id == company.id
    ).scalar()
    
    total_records = db.query(func.count(Record.id)).filter(
        Record.document_id.in_(document_ids)
    ).scalar()
    
    total_emissions = db.query(func.sum(Record.co2e)).filter(
        Record.document_id.in_(document_ids)
    ).scalar() or 0
    
    # Get date range
    date_range = db.query(
        func.min(Record.date).label('earliest'),
        func.max(Record.date).label('latest')
    ).filter(
        Record.document_id.in_(document_ids)
    ).first()
    
    return {
        "total_documents": total_documents,
        "total_records": total_records,
        "total_emissions_tco2e": float(total_emissions),
        "date_range": {
            "earliest": date_range.earliest.isoformat() if date_range.earliest else None,
            "latest": date_range.latest.isoformat() if date_range.latest else None
        }
    }
