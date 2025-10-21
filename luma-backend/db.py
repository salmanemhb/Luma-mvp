"""
Database configuration and connection management
Using Supabase PostgreSQL with SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/luma"
)

# For async operations (optional, for future scaling)
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create sync engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session
    Usage in FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """Initialize database tables"""
    try:
        # Import all models to register them with Base
        from models import company, document, record, emission_factor, report
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Load emission factors if not already loaded
        await seed_emission_factors()
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise


async def seed_emission_factors():
    """Load emission factors from CSV if table is empty"""
    from models.emission_factor import EmissionFactor
    import csv
    
    db = SessionLocal()
    try:
        # Check if factors already exist
        count = db.query(EmissionFactor).count()
        if count > 0:
            logger.info(f"📊 Emission factors already loaded ({count} records)")
            return
        
        # Load from CSV
        csv_path = os.path.join(os.path.dirname(__file__), "emission_factors.csv")
        if not os.path.exists(csv_path):
            logger.warning(f"⚠️ Emission factors CSV not found at {csv_path}")
            return
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            factors = []
            for row in reader:
                factor = EmissionFactor(
                    category=row['category'],
                    unit=row['unit'],
                    factor=float(row['factor']),
                    source=row['source'],
                    year=int(row['year'])
                )
                factors.append(factor)
        
        db.bulk_save_objects(factors)
        db.commit()
        logger.info(f"✅ Loaded {len(factors)} emission factors")
        
    except Exception as e:
        logger.error(f"❌ Failed to seed emission factors: {str(e)}")
        db.rollback()
    finally:
        db.close()


# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "luma-documents")

# Storage configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
