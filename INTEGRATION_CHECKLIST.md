# Backend Integration Checklist

## ✅ COMPLETED

### Frontend Setup
- ✅ Complete styled CSS from luma-shine-report
- ✅ All UI components (60+ shadcn components)
- ✅ Tailwind config (TypeScript version with proper theme)
- ✅ PostCSS configuration
- ✅ i18n setup (English & Spanish)
- ✅ All pages (Dashboard, Upload, Report, Login, Admin pages)
- ✅ API client with all endpoints
- ✅ Environment variables (.env.production)
- ✅ Dashboard connected to backend with data transformation

### Backend Setup
- ✅ FastAPI backend deployed on Render
- ✅ CORS configured for Vercel
- ✅ Database migrations ready
- ✅ All routers (auth, upload, analyze, dashboard, report, admin, waitlist)
- ✅ Admin endpoints for waitlist management

---

## ⚠️ NEEDS VERIFICATION

### 1. Database Setup
**Status**: Migration script exists but may not be executed

**What to check:**
```sql
-- Connect to your Render PostgreSQL database and verify these tables exist:
-- Run: \dt in psql to list all tables

Required tables:
✓ waitlist_submissions (shared with landing page)
? companies
? users
? documents
? uploads
? records
? analyses
? reports
? activity_log
```

**How to fix if missing:**
1. Go to Render dashboard → PostgreSQL database
2. Click "Connect" → Copy connection string
3. Connect via psql or use Render SQL console
4. Run migration files in `luma-backend/migrations/` folder

---

### 2. Environment Variables

#### Backend (Render - luma-mvp-backend)
**Go to**: Render Dashboard → luma-mvp-backend → Environment

**Required variables:**
```bash
DATABASE_URL=<your-render-postgres-url>
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-anon-key>
SUPABASE_JWT_SECRET=<your-supabase-jwt-secret>
ADMIN_EMAILS=salmane.mohib@gmail.com
ADMIN_API_KEY=temp_admin_key_replace_me
DEBUG=False
CORS_ORIGINS=https://luma-mvp.vercel.app,http://localhost:5173
```

**Status**: DATABASE_URL, SUPABASE_* probably set. Need to verify ADMIN_API_KEY.

#### Frontend (Vercel - Luma-mvp)
**Go to**: Vercel Dashboard → Luma-mvp → Settings → Environment Variables

**Required variables:**
```bash
VITE_API_URL=https://luma-mvp-backend.onrender.com
```

**Status**: ⚠️ **CRITICAL - YOU MUST SET THIS**

---

### 3. Test User Account

**Status**: Unknown if test company exists in database

**What you need:**
- At least one company account in the database to test login
- Test credentials to access the dashboard

**Options:**
1. **Promote from waitlist**: 
   - Go to landing page (getluma.es)
   - Submit form
   - Use admin endpoint to promote to company
   
2. **Create via signup endpoint**:
   ```bash
   curl -X POST https://luma-mvp-backend.onrender.com/api/auth/signup \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "test123",
       "company_name": "Test Company",
       "sector": "Manufacturing",
       "country": "Spain"
     }'
   ```

3. **Direct database insert** (if needed)

---

### 4. Landing Backend Admin API Key

**Status**: ⚠️ Needs to be set

**Where**: Render Dashboard → luma-api (landing backend) → Environment

**Add this variable:**
```bash
ADMIN_API_KEY=temp_admin_key_replace_me
```

**Why**: Without this, the MVP backend cannot call the landing backend's admin endpoints to fetch waitlist data.

---

## 🧪 TESTING CHECKLIST

### Frontend Tests
Once Vercel `VITE_API_URL` is set and deployed:

1. **Login Page**
   - [ ] Navigate to https://luma-mvp.vercel.app/login
   - [ ] Page loads with beautiful sage green styling
   - [ ] Form fields are styled correctly
   - [ ] Language toggle works (EN/ES)

2. **Authentication**
   - [ ] Can signup with new account
   - [ ] Can login with existing account
   - [ ] Gets redirected to /dashboard after login
   - [ ] Invalid credentials show error
   - [ ] Logout works and redirects to /login

3. **Dashboard**
   - [ ] KPI cards show correct values from backend
   - [ ] Monthly emissions chart displays
   - [ ] Scope breakdown pie chart displays
   - [ ] Recent uploads table shows uploaded documents
   - [ ] "Generate Report" button navigates to /report
   - [ ] All styling is correct (sage green theme)

4. **Upload**
   - [ ] Drag and drop zone works
   - [ ] Can select files (PDF, CSV, XLSX, images)
   - [ ] Upload progress bar shows
   - [ ] File uploads successfully to backend
   - [ ] Success message appears
   - [ ] Redirects to dashboard after upload

5. **Report**
   - [ ] Report page loads
   - [ ] Can download PDF (when implemented)
   - [ ] Can download Excel (when implemented)
   - [ ] Report metadata displays correctly

6. **Admin Panel**
   - [ ] Navigate to /admin/waitlist
   - [ ] See list of waitlist submissions from getluma.es
   - [ ] Can view submission details
   - [ ] Can promote user to company account
   - [ ] Can delete submission
   - [ ] Stats/KPIs show correct numbers

### Backend Tests

1. **Health Check**
   ```bash
   curl https://luma-mvp-backend.onrender.com/health
   # Should return: {"status":"ok","services":{...}}
   ```

2. **Signup Test**
   ```bash
   curl -X POST https://luma-mvp-backend.onrender.com/api/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"email":"test@test.com","password":"test123","company_name":"Test Co"}'
   # Should return: {"access_token":"...","user_id":"..."}
   ```

3. **Dashboard API Test**
   ```bash
   # First login to get token, then:
   curl https://luma-mvp-backend.onrender.com/api/dashboard/ \
     -H "Authorization: Bearer YOUR_TOKEN"
   # Should return: {"summary":{...},"monthly_data":[...],...}
   ```

### Integration Tests

1. **Landing → MVP Flow**
   - [ ] Submit form on https://getluma.es
   - [ ] Receive confirmation email
   - [ ] Entry appears in MVP admin panel (/admin/waitlist)
   - [ ] Click "Promote to Company"
   - [ ] User can login with temporary password
   - [ ] User sees empty dashboard (no data yet)
   - [ ] User can upload first document
   - [ ] Dashboard updates with real data

---

## 🚨 CRITICAL ISSUES TO FIX

### Issue #1: Vercel Environment Variable
**Priority**: CRITICAL ⚠️
**Status**: Not set
**Action**: Add `VITE_API_URL=https://luma-mvp-backend.onrender.com` in Vercel settings
**Impact**: Without this, frontend will try to connect to localhost instead of production backend

### Issue #2: Database Tables
**Priority**: HIGH
**Status**: Unknown
**Action**: Verify all tables exist, run migrations if needed
**Impact**: Backend will crash or return errors if tables don't exist

### Issue #3: Test Account
**Priority**: HIGH
**Status**: Unknown
**Action**: Create at least one company account to test with
**Impact**: Cannot test login/dashboard without an account

### Issue #4: Landing Backend Admin Key
**Priority**: MEDIUM
**Status**: Not set
**Action**: Add `ADMIN_API_KEY` to landing backend environment
**Impact**: Cannot fetch waitlist submissions in MVP admin panel

---

## 📋 WHAT'S MISSING FROM BACKEND

Based on the frontend pages, here's what might need to be added:

### 1. Report Generation (Backend)
**Frontend expects**: `/api/report/{company_id}` POST endpoint to generate reports
**Backend has**: ✅ Already implemented in `routers/report.py`
**Status**: Should work, needs testing

### 2. Upload Processing
**Frontend expects**: Upload file → Analyze → Show results
**Backend has**: ✅ Upload endpoint + Analyze endpoint
**Status**: Should work, needs OCR/extraction logic verification

### 3. Admin Dashboard Stats
**Frontend expects**: KPIs like total companies, total emissions, reports generated
**Backend has**: ✅ `/api/admin/insights` endpoint
**Status**: Should work, needs testing

### 4. Company Management (Admin)
**Frontend expects**: List companies, view details, activity logs
**Backend has**: ✅ All implemented in `routers/admin.py`
**Status**: Should work, needs testing

---

## 🎯 IMMEDIATE NEXT STEPS

### Step 1: Set Vercel Environment Variable (5 minutes)
1. Go to https://vercel.com/dashboard
2. Find "Luma-mvp" project
3. Settings → Environment Variables
4. Add: `VITE_API_URL` = `https://luma-mvp-backend.onrender.com`
5. Save and redeploy

### Step 2: Verify Database Tables (10 minutes)
1. Go to Render → PostgreSQL database
2. Connect via SQL console or psql
3. Run: `\dt` to list tables
4. If missing, run migration scripts from `luma-backend/migrations/`

### Step 3: Create Test Account (5 minutes)
```bash
curl -X POST https://luma-mvp-backend.onrender.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "salmane.mohib@gmail.com",
    "password": "TestPassword123",
    "company_name": "Luma Test Company",
    "sector": "Manufacturing",
    "country": "Spain"
  }'
```
Save the returned access_token or just use the credentials to login via frontend.

### Step 4: Test Frontend (10 minutes)
1. Wait for Vercel to redeploy after env var change
2. Visit https://luma-mvp.vercel.app/login
3. Login with test account
4. Verify dashboard loads with data
5. Try uploading a test document

### Step 5: Set Landing Backend Admin Key (2 minutes)
1. Render → luma-api service
2. Environment → Add `ADMIN_API_KEY=temp_admin_key_replace_me`
3. Save (will auto-redeploy)

---

## 📞 SUPPORT COMMANDS

### Check Backend Logs
```bash
# Go to Render dashboard → luma-mvp-backend → Logs
# Look for errors during requests
```

### Check Frontend Build Logs
```bash
# Go to Vercel dashboard → Luma-mvp → Deployments → Click latest
# Check build logs for errors
```

### Test API Endpoints
```bash
# Health check
curl https://luma-mvp-backend.onrender.com/health

# Signup
curl -X POST https://luma-mvp-backend.onrender.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"pass","company_name":"Test"}'

# Login
curl -X POST https://luma-mvp-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"pass"}'
```

---

## ✅ SUCCESS CRITERIA

You'll know everything is working when:
1. ✅ Frontend loads at https://luma-mvp.vercel.app with beautiful sage green styling
2. ✅ Can login with test credentials
3. ✅ Dashboard shows real data from backend
4. ✅ Can upload a document
5. ✅ Can navigate to all pages without errors
6. ✅ Admin panel shows waitlist from getluma.es
7. ✅ No console errors in browser
8. ✅ No 404 or 500 errors from backend
