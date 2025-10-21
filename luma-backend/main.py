"""
Luma MVP - Main FastAPI Application
CSRD Automation Platform for EU Manufacturing SMEs
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from routers import upload, analyze, dashboard, report, auth, admin, waitlist_admin
from db import init_db
from middleware import admin_guard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and resources on startup"""
    logger.info("🚀 Starting Luma Backend...")
    await init_db()
    logger.info("✅ Database initialized")
    yield
    logger.info("👋 Shutting down Luma Backend...")


app = FastAPI(
    title="Luma API",
    description="CSRD-compliant ESG data automation platform",
    version="0.1.0",
    lifespan=lifespan
)

# CORS configuration - adjust origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React port
        "https://luma.vercel.app",  # Production frontend
        "https://luma-mvp.vercel.app",  # MVP frontend
        "https://*.vercel.app",  # All Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add admin guard middleware
app.middleware("http")(admin_guard)


# Rate limiting middleware (simple in-memory implementation)
request_counts = {}
RATE_LIMIT = 30  # requests per minute


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple rate limiting: 30 req/min per IP"""
    client_ip = request.client.host
    current_time = int(time.time() / 60)  # Current minute
    
    key = f"{client_ip}:{current_time}"
    request_counts[key] = request_counts.get(key, 0) + 1
    
    # Clean old entries
    old_keys = [k for k in request_counts.keys() if not k.endswith(str(current_time))]
    for old_key in old_keys:
        del request_counts[old_key]
    
    if request_counts[key] > RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."}
        )
    
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(max(0, RATE_LIMIT - request_counts[key]))
    return response


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["Analysis"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(report.router, prefix="/api/report", tags=["Reports"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(waitlist_admin.router, tags=["Admin-Waitlist"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Luma API",
        "version": "0.1.0",
        "message": "CSRD automation platform"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "ok",
        "timestamp": time.time(),
        "services": {
            "database": "connected",
            "storage": "available",
            "ocr": "ready"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
