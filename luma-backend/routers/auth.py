"""
Authentication router - Supabase Auth integration
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import os
import jwt
import logging

from db import get_db
from models.company import Company
from utils.audit import log_login

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Supabase JWT secret (from Supabase dashboard)
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "your-jwt-secret")


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    company_name: str
    sector: str = None
    country: str = "ES"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    company_id: str


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify Supabase JWT token
    In production, this validates against Supabase Auth
    For MVP, we use a simplified version
    """
    token = credentials.credentials
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_signature": False}  # For MVP only
        )
        return payload
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_company(
    token_payload: dict = Depends(verify_token),
    db: Session = Depends(get_db)
) -> Company:
    """
    Get current company from token
    """
    company_id = token_payload.get("company_id")
    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Company ID not found in token"
        )
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    """
    Register new company and user
    
    In production: integrates with Supabase Auth
    For MVP: simplified registration
    """
    # Check if company already exists
    existing = db.query(Company).filter(Company.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create company
    company = Company(
        name=request.company_name,
        sector=request.sector,
        country=request.country,
        email=request.email
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    
    # Generate token (in production, Supabase handles this)
    token_payload = {
        "user_id": str(company.id),  # In production, separate user table
        "company_id": str(company.id),
        "email": request.email
    }
    token = jwt.encode(token_payload, SUPABASE_JWT_SECRET, algorithm="HS256")
    
    logger.info(f"✅ New company registered: {company.name}")
    
    return TokenResponse(
        access_token=token,
        user_id=str(company.id),
        company_id=str(company.id)
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login existing user
    
    In production: validates against Supabase Auth
    For MVP: simplified login
    """
    # Find company by email
    company = db.query(Company).filter(Company.email == request.email).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # In production: verify password with Supabase
    # For MVP: accept any password (INSECURE - FOR TESTING ONLY)
    
    # Log login event
    log_login(company_id=str(company.id), email=request.email, db=db)
    
    # Generate token
    token_payload = {
        "user_id": str(company.id),
        "company_id": str(company.id),
        "email": request.email
    }
    token = jwt.encode(token_payload, SUPABASE_JWT_SECRET, algorithm="HS256")
    
    logger.info(f"✅ Company logged in: {company.name}")
    
    return TokenResponse(
        access_token=token,
        user_id=str(company.id),
        company_id=str(company.id)
    )


@router.get("/me")
async def get_current_user(company: Company = Depends(get_current_company)):
    """Get current authenticated company details"""
    return company.to_dict()


@router.post("/logout")
async def logout():
    """
    Logout user
    In production: invalidates Supabase session
    For MVP: client-side token removal
    """
    return {"message": "Logged out successfully"}
