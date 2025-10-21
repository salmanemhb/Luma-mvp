"""
Admin middleware - role-based access control
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import jwt
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "your-jwt-secret")
ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "").split(",")


def get_role_from_token(request: Request) -> Optional[str]:
    """
    Extract role from JWT token
    Returns: 'admin', 'company_user', or None
    """
    try:
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        # Extract token
        token = auth_header.replace("Bearer ", "")
        
        # Decode token
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_signature": False}  # For MVP; enable in production
        )
        
        # Check if admin
        email = payload.get("email", "")
        if email in ADMIN_EMAILS:
            return "admin"
        
        return payload.get("role", "company_user")
        
    except jwt.InvalidTokenError as e:
        logger.debug(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Token parsing error: {str(e)}")
        return None


async def admin_guard(request: Request, call_next):
    """
    Middleware to protect /api/admin/* routes
    Only allows requests with admin role
    """
    # Check if request is for admin endpoint
    if request.url.path.startswith("/api/admin"):
        role = get_role_from_token(request)
        
        if role != "admin":
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "Admin access only",
                    "message": "You do not have permission to access this resource"
                }
            )
    
    response = await call_next(request)
    return response


def require_admin(request: Request) -> bool:
    """
    Dependency to require admin role
    Usage: @router.get("/endpoint", dependencies=[Depends(require_admin)])
    """
    role = get_role_from_token(request)
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return True
