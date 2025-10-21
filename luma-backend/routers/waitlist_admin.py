"""
Admin router for MVP dashboard.
Manages waitlist submissions from landing page and promotes them to company accounts.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime

from db import get_db
from models.waitlist import WaitlistSubmission
from models.company import Company
from routers.auth import get_current_company
import secrets
import string

router = APIRouter(prefix="/api/admin/waitlist", tags=["admin-waitlist"])


@router.get("/")
async def list_waitlist_submissions(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company)
):
    """
    List all waitlist submissions from landing page.
    Admin-only endpoint.
    """
    # TODO: Add admin role check
    
    query = db.query(WaitlistSubmission)
    
    if role:
        query = query.filter(WaitlistSubmission.role == role)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (WaitlistSubmission.name.ilike(search_term)) |
            (WaitlistSubmission.company.ilike(search_term)) |
            (WaitlistSubmission.email.ilike(search_term))
        )
    
    total = query.count()
    items = query.order_by(desc(WaitlistSubmission.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return {
        "total": total,
        "items": items
    }


@router.get("/{id}")
async def get_waitlist_detail(
    id: int,
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company)
):
    """Get detailed information about a waitlist submission."""
    submission = db.query(WaitlistSubmission)\
        .filter(WaitlistSubmission.id == id)\
        .first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Check if already promoted to company
    existing_company = db.query(Company)\
        .filter(Company.email == submission.email)\
        .first()
    
    return {
        "submission": submission,
        "already_promoted": existing_company is not None,
        "company_id": existing_company.id if existing_company else None
    }


@router.post("/{id}/promote")
async def promote_to_company(
    id: int,
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company)
):
    """
    Promote a waitlist submission to a full company account.
    Creates a Company record with temporary password.
    """
    submission = db.query(WaitlistSubmission)\
        .filter(WaitlistSubmission.id == id)\
        .first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Check if already promoted
    existing = db.query(Company)\
        .filter(Company.email == submission.email)\
        .first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"User already has a company account (ID: {existing.id})"
        )
    
    # Generate temporary password
    temp_password = ''.join(
        secrets.choice(string.ascii_letters + string.digits) 
        for _ in range(12)
    )
    
    # Create company account
    new_company = Company(
        name=submission.company,
        email=submission.email,
        password_hash=temp_password,  # TODO: Hash this properly
        sector="Unknown",  # Can be updated later
        country="ES",  # Default to Spain
        data_points=0
    )
    
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    
    # TODO: Send invitation email with temporary password
    
    return {
        "message": "Successfully promoted to company account",
        "company_id": new_company.id,
        "company_name": new_company.name,
        "email": new_company.email,
        "temporary_password": temp_password,
        "note": "Send this password to the user via email"
    }


@router.delete("/{id}")
async def delete_waitlist_submission(
    id: int,
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company)
):
    """Delete a waitlist submission (reject)."""
    submission = db.query(WaitlistSubmission)\
        .filter(WaitlistSubmission.id == id)\
        .first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    db.delete(submission)
    db.commit()
    
    return {"message": f"Deleted waitlist submission {id}"}
