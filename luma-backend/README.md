# Luma MVP - Backend

**CSRD-compliant ESG data automation platform for EU manufacturing SMEs**

Built with FastAPI + PostgreSQL (Supabase) + Tesseract OCR

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **PostgreSQL** (or Supabase account)
- **Tesseract OCR** (for document parsing)
- **Poppler** (for PDF processing)

### Installation

1. **Clone and navigate**
   ```bash
   cd luma-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install system dependencies**

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr tesseract-ocr-spa poppler-utils
   ```

   **macOS:**
   ```bash
   brew install tesseract tesseract-lang poppler
   ```

   **Windows:**
   - Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
   - Download Poppler: https://github.com/oschwartz10612/poppler-windows/releases/

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

6. **Setup database**
   ```bash
   # Run migrations
   psql -U postgres -d luma -f migrations/001_initial_schema.sql
   
   # Or use Supabase SQL Editor to run the migration
   ```

7. **Run the server**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

8. **Access API docs**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

## 🗂️ Project Structure

```
luma-backend/
├── main.py                 # FastAPI application entry point
├── db.py                   # Database configuration
├── middleware.py           # Admin guard & auth middleware
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── emission_factors.csv   # Emission factor database
├── models/                # SQLAlchemy ORM models
│   ├── company.py
│   ├── document.py
│   ├── record.py
│   ├── emission_factor.py
│   ├── report.py
│   ├── usage_log.py
│   └── company_stats.py
├── routers/               # API route handlers
│   ├── auth.py           # Authentication
│   ├── upload.py         # File uploads
│   ├── analyze.py        # Document analysis
│   ├── dashboard.py      # Analytics dashboard
│   ├── report.py         # CSRD report generation
│   └── admin.py          # Admin endpoints
├── utils/                 # Utility functions
│   ├── ocr.py            # OCR text extraction
│   ├── parser.py         # Document parsing (CSV/Excel/text)
│   ├── calculator.py     # Emission calculations
│   ├── report_generator.py # PDF/Excel generation
│   └── audit.py          # Usage logging
├── migrations/            # Database migrations
│   └── 001_initial_schema.sql
├── uploads/               # Uploaded documents (gitignored)
└── reports/               # Generated reports (gitignored)
```

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/signup` - Register company
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Documents
- `POST /api/upload/` - Upload document (PDF/CSV/XLSX)
- `GET /api/upload/documents` - List documents
- `DELETE /api/upload/documents/{id}` - Delete document

### Analysis
- `POST /api/analyze/{document_id}` - Analyze document
- `GET /api/analyze/status/{document_id}` - Check status

### Dashboard
- `GET /api/dashboard/` - Get emission analytics
- `GET /api/dashboard/records` - List emission records
- `GET /api/dashboard/stats` - Quick statistics

### Reports
- `POST /api/report/{company_id}` - Generate CSRD report
- `GET /api/report/list` - List reports
- `GET /api/report/{report_id}/download/pdf` - Download PDF
- `GET /api/report/{report_id}/download/excel` - Download Excel

### Admin (requires admin role)
- `GET /api/admin/companies` - List all companies
- `GET /api/admin/company/{id}` - Company details
- `GET /api/admin/activity` - Usage log
- `GET /api/admin/insights` - Platform analytics
- `GET /api/admin/export` - Export data (CSV/XLSX)
- `POST /api/admin/aggregate-stats` - Run monthly aggregation

---

## 🔐 Admin Access

To promote a user to admin:

1. Add email to `.env`:
   ```
   ADMIN_EMAILS=salmane@getluma.es,admin@getluma.es
   ```

2. Restart server

3. Admin users can access `/api/admin/*` endpoints

---

## 🧪 Testing

### Manual Testing
```bash
# Health check
curl http://localhost:8000/

# Test OCR setup
python utils/ocr.py
```

### With Postman/Thunder Client
Import the collection (see `/docs` for examples)

### Unit Tests
```bash
pytest tests/
```

---

## 🐳 Docker (Optional)

Run with Docker Compose:

```bash
docker-compose up -d
```

Includes:
- FastAPI backend
- PostgreSQL database
- pgAdmin (database UI)
- MinIO (S3-compatible storage)

---

## 📊 Database Migrations

### Apply migrations
```bash
# PostgreSQL
psql -U postgres -d luma -f migrations/001_initial_schema.sql

# Supabase
# Copy migration SQL to Supabase SQL Editor and run
```

### Seed emission factors
Automatically loaded on first run from `emission_factors.csv`

---

## 🛠️ Configuration

### OCR Provider
```env
OCR_PROVIDER=tesseract  # or 'vision' for Google Cloud Vision
```

### Spain-specific emission factors
```env
USE_SPAIN_FACTORS=true
```

### File upload limits
```env
MAX_UPLOAD_MB=15
```

### Rate limiting
```env
RATE_LIMIT=30  # requests per minute
```

---

## 🔧 Troubleshooting

### Tesseract not found
```bash
# Linux
sudo apt-get install tesseract-ocr

# Check installation
tesseract --version
```

### PDF processing fails
```bash
# Install poppler
sudo apt-get install poppler-utils  # Linux
brew install poppler                 # Mac
```

### Database connection error
- Check `DATABASE_URL` in `.env`
- Ensure PostgreSQL is running
- Test connection: `psql -U postgres`

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📝 Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_JWT_SECRET` - JWT signing secret
- `ADMIN_EMAILS` - Comma-separated admin emails
- `OCR_PROVIDER` - tesseract or vision
- `MAX_UPLOAD_MB` - Maximum file size

---

## 🚢 Deployment

### Render / Railway
1. Connect GitHub repo
2. Set environment variables
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Docker
```bash
docker build -t luma-backend .
docker run -p 8000:8000 --env-file .env luma-backend
```

---

## 📄 License

Luma MVP © 2025 - All rights reserved

---

## 🤝 Support

For issues or questions:
- Email: salmane@getluma.es
- Docs: https://docs.getluma.es

---

**Built with ❤️ for EU manufacturing SMEs**
