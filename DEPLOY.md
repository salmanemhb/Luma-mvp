# 🚀 MVP Deployment Guide

## 1. GitHub Setup

```powershell
# After creating GitHub repo at https://github.com/new
cd c:\Users\salmane\Desktop\mvp
git remote add origin https://github.com/salmanemhb/Luma-mvp.git
git branch -M main
git push -u origin main
```

## 2. Backend Deployment (Render)

### Create New Web Service on Render:
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository: `Luma-mvp`
4. Configure:
   - **Name:** `luma-mvp-backend`
   - **Root Directory:** `luma-backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Environment Variables:
```env
DATABASE_URL=<YOUR_RENDER_POSTGRES_URL>
SUPABASE_URL=<YOUR_SUPABASE_URL>
SUPABASE_KEY=<YOUR_SUPABASE_KEY>
SUPABASE_JWT_SECRET=<YOUR_SUPABASE_JWT_SECRET>
SUPABASE_BUCKET=luma-documents
ADMIN_EMAILS=salmane@getluma.es
ADMIN_API_KEY=temp_admin_key_replace_me
DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=https://luma-mvp.vercel.app,http://localhost:5173
UPLOAD_DIR=./uploads
REPORTS_DIR=./reports
MAX_UPLOAD_MB=15
OCR_PROVIDER=tesseract
RATE_LIMIT=30
LANG_DEFAULT=es
USE_SPAIN_FACTORS=false
```

**Important:** Use the SAME `DATABASE_URL` as your landing backend to share the database!

## 3. Frontend Deployment (Vercel)

### Deploy to Vercel:
1. Go to https://vercel.com/new
2. Import Git Repository: `Luma-mvp`
3. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `luma-frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

### Environment Variables:
```env
VITE_API_URL=https://luma-mvp-backend.onrender.com
```

## 4. Run Database Migration

After backend is deployed, connect to your Render PostgreSQL and run:

```sql
CREATE TABLE IF NOT EXISTS waitlist_submissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    company VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_waitlist_email ON waitlist_submissions(email);
CREATE INDEX IF NOT EXISTS idx_waitlist_created_at ON waitlist_submissions(created_at);
CREATE INDEX IF NOT EXISTS idx_waitlist_role ON waitlist_submissions(role);
```

## 5. Test the Deployment

### Test Backend:
```powershell
# Health check
Invoke-RestMethod "https://luma-mvp-backend.onrender.com/api/health"

# Test waitlist endpoint
Invoke-RestMethod "https://luma-mvp-backend.onrender.com/api/admin/waitlist" -Headers @{"X-Admin-Key"="temp_admin_key_replace_me"}
```

### Test Frontend:
1. Open: `https://luma-mvp.vercel.app`
2. Login with your account
3. Navigate to `/admin/waitlist`
4. You should see the waitlist submissions from getluma.es

## 6. Configure Landing Backend

Add this environment variable to your landing backend on Render:
```env
ADMIN_API_KEY=temp_admin_key_replace_me
```

## 🎯 Final Architecture

```
┌─────────────────────┐
│   getluma.es        │ ← Landing (Vercel)
│   (Waitlist Form)   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────────────────────┐
│  luma-api.onrender.com              │ ← Landing Backend (Render)
│  - Submit waitlist                  │
│  - Send confirmation email          │
│  - Admin endpoints (NEW)            │
└──────────┬──────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│  Render PostgreSQL (SHARED)         │ ← Database
│  - waitlist_submissions table       │
│  - companies, documents, etc.       │
└──────────┬──────────────────────────┘
           │
           ↑
┌─────────────────────────────────────┐
│  luma-mvp-backend.onrender.com      │ ← MVP Backend (Render)
│  - Read waitlist                    │
│  - Promote users                    │
│  - Full CSRD dashboard              │
└──────────┬──────────────────────────┘
           │
           ↑
┌─────────────────────┐
│  luma-mvp.vercel.app│ ← MVP Frontend (Vercel)
│  - Admin Dashboard  │
│  - Waitlist Page    │
│  - CSRD Features    │
└─────────────────────┘
```

## ✅ Success Checklist

- [ ] GitHub repo created and pushed
- [ ] Backend deployed on Render
- [ ] Frontend deployed on Vercel
- [ ] Database migration run
- [ ] Landing backend has ADMIN_API_KEY set
- [ ] Can access https://luma-mvp.vercel.app
- [ ] Can see waitlist at /admin/waitlist
- [ ] Can promote users from waitlist

## 🔗 URLs You'll Have

After deployment:
- **MVP Frontend:** `https://luma-mvp.vercel.app`
- **MVP Backend:** `https://luma-mvp-backend.onrender.com`
- **Landing Frontend:** `https://getluma.es` (existing)
- **Landing Backend:** `https://luma-api-lbkc.onrender.com` (existing)
- **Database:** Shared Render PostgreSQL (existing)

---

**Need help?** Let me know if you get stuck on any step!
