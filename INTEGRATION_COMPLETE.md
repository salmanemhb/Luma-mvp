# 🔗 Luma Integration - Complete Setup Guide

## What We Built

I've connected your **landing page** (getluma.es) with your **MVP dashboard** to create a seamless waitlist → company account flow.

---

## ✅ Completed Work

### 1. **Landing Backend** (luma-clarity-landing-main)
- ✅ Added `/api/admin/*` endpoints for waitlist management
- ✅ Admin can view all signups (GET `/api/admin/waitlist`)
- ✅ Admin can get stats (GET `/api/admin/stats`)
- ✅ Admin can export CSV (GET `/api/admin/waitlist/export/csv`)
- ✅ Admin can promote users (POST `/api/admin/waitlist/{id}/promote`)
- ✅ Admin can delete signups (DELETE `/api/admin/waitlist/{id}`)

**Files Created:**
- `server/routers/admin.py` - All admin endpoints
- Updated `server/main.py` - Registered admin router

**Deployed**: ✅ Pushed to GitHub → Auto-deploying to Render

---

### 2. **MVP Backend** (mvp/luma-backend)
- ✅ Added `WaitlistSubmission` model to share landing database
- ✅ Created `/api/admin/waitlist/*` endpoints in MVP
- ✅ Can fetch waitlist from landing database
- ✅ Can promote waitlist → company account
- ✅ Created database migration script

**Files Created:**
- `models/waitlist.py` - WaitlistSubmission model
- `routers/waitlist_admin.py` - Waitlist management endpoints
- `migrations/002_add_waitlist_table.sql` - Database migration
- Updated `models/__init__.py` - Registered waitlist model
- Updated `main.py` - Registered waitlist_admin router

**Status**: Ready to deploy

---

### 3. **MVP Frontend** (mvp/luma-frontend)
- ✅ Created `AdminWaitlist.tsx` page with full management UI
- ✅ Search & filter by role
- ✅ View stats (total, last 24h, last 7d)
- ✅ Promote users to company accounts
- ✅ Delete unwanted signups
- ✅ Beautiful table UI with badges

**Files Created:**
- `src/pages/admin/AdminWaitlist.tsx` - Waitlist management page
- Updated `src/lib/api.ts` - Added waitlist API methods

**Status**: Ready to test after `npm install`

---

## 🗄️ Database Strategy

**We're using a SHARED DATABASE approach:**

Both the landing backend and MVP backend connect to the **same Render PostgreSQL database**.

```
Render PostgreSQL
├── waitlist_submissions (landing writes, MVP reads)
├── companies (MVP writes)
├── documents (MVP)
├── records (MVP)
└── ... other MVP tables
```

### Migration Steps:

1. **Run migration on Render PostgreSQL:**
   ```sql
   -- Connect to your Render database and run:
   -- File: mvp/luma-backend/migrations/002_add_waitlist_table.sql
   
   CREATE TABLE IF NOT EXISTS waitlist_submissions (
       id SERIAL PRIMARY KEY,
       name VARCHAR(100) NOT NULL,
       company VARCHAR(150) NOT NULL,
       email VARCHAR(150) UNIQUE NOT NULL,
       role VARCHAR(50) NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );
   ```

2. **Update MVP backend `.env` with Render database URL:**
   ```bash
   DATABASE_URL=postgresql://luma_production_db_user:PASSWORD@dpg-d3psqv8gjchc73asj2sg-a.oregon-postgres.render.com/luma_production_db?sslmode=require
   ```

---

## 🔄 User Flow

```
1. User visits getluma.es
   ↓
2. User submits waitlist form
   ↓
3. Saved to `waitlist_submissions` table
   ↓
4. Email sent via Resend ✅
   ↓
5. Admin logs into MVP dashboard
   ↓
6. Admin goes to /admin/waitlist page
   ↓
7. Admin sees all signups
   ↓
8. Admin clicks "Promote" on a user
   ↓
9. System creates Company account
   ↓
10. User receives invitation email (TODO)
   ↓
11. User can login to MVP dashboard
```

---

## 🚀 Deployment Steps

### **Landing Backend** (Already Deployed)
1. ✅ Pushed to GitHub
2. ✅ Render auto-deploys from `main` branch
3. ✅ Admin endpoints live at: `https://luma-api-lbkc.onrender.com/api/admin/*`

Test: `curl https://luma-api-lbkc.onrender.com/api/admin/stats`

---

### **MVP Backend** (Ready to Deploy)

#### Option A: Deploy to Render (Recommended)
1. Create new Web Service on Render
2. Connect to GitHub repo (`mvp/luma-backend` folder)
3. Set environment variables:
   ```bash
   DATABASE_URL=<same as landing backend database>
   SUPABASE_URL=<your supabase url>
   SUPABASE_KEY=<your supabase key>
   ADMIN_EMAILS=salmane@getluma.es
   ```
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### Option B: Test Locally First
```powershell
cd c:\Users\salmane\Desktop\mvp\luma-backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Set DATABASE_URL to Render PostgreSQL
python -m uvicorn main:app --reload --port 8000
```

---

### **MVP Frontend** (Ready to Deploy)

#### Deploy to Vercel:
1. Push `mvp/luma-frontend` to GitHub
2. Import project in Vercel
3. Set environment variable:
   ```bash
   VITE_API_URL=https://your-mvp-backend.onrender.com
   ```
4. Deploy!

#### Test Locally First:
```powershell
cd c:\Users\salmane\Desktop\mvp\luma-frontend
npm install
npm run dev
```

---

## 🧪 Testing Checklist

### **1. Test Landing Admin Endpoints**
```bash
# Get waitlist stats
curl https://luma-api-lbkc.onrender.com/api/admin/stats

# Get all submissions
curl https://luma-api-lbkc.onrender.com/api/admin/waitlist

# Export CSV
curl https://luma-api-lbkc.onrender.com/api/admin/waitlist/export/csv -o waitlist.csv
```

### **2. Test MVP Waitlist Integration**
```bash
# After MVP backend is deployed:
curl https://your-mvp-backend.onrender.com/api/admin/waitlist

# Promote a user (replace {id})
curl -X POST https://your-mvp-backend.onrender.com/api/admin/waitlist/{id}/promote
```

### **3. Test MVP Frontend**
1. Navigate to `http://localhost:5173/admin/waitlist`
2. Should see all signups from landing page
3. Click "Promote" on a user
4. Check that company account was created
5. Verify user can login with temp password

---

## 📝 TODO / Next Steps

### **Immediate:**
- [ ] Run database migration (`002_add_waitlist_table.sql`) on Render PostgreSQL
- [ ] Update MVP backend `.env` with Render database URL
- [ ] Deploy MVP backend to Render
- [ ] Deploy MVP frontend to Vercel
- [ ] Test end-to-end flow

### **Phase 2:**
- [ ] Add proper JWT authentication to admin endpoints
- [ ] Add email invitation when promoting users
- [ ] Hash passwords properly (currently storing temp passwords)
- [ ] Add admin role check (currently using temp API key)
- [ ] Add audit logging for admin actions
- [ ] Add bulk promote/delete actions

### **Polish:**
- [ ] Add `AdminWaitlistDetail.tsx` page for individual signup view
- [ ] Add charts for signup trends
- [ ] Add email templates for invitations
- [ ] Add "Promoted" status flag to waitlist table
- [ ] Add export functionality in MVP dashboard

---

## 🔐 Security Notes

**Current Security (MVP):**
- ⚠️ Admin endpoints use temporary API key: `temp_admin_key_replace_me`
- ⚠️ Passwords not hashed in promote function
- ⚠️ No admin role check (all authenticated users can access)

**Production Security (TODO):**
- [ ] Implement proper JWT with admin role claim
- [ ] Hash passwords with bcrypt before storing
- [ ] Add admin-only middleware check
- [ ] Rate limit admin endpoints
- [ ] Add CSRF protection
- [ ] Audit log all admin actions

---

## 📊 Database Tables

### `waitlist_submissions` (Shared)
```sql
id          SERIAL PRIMARY KEY
name        VARCHAR(100)
company     VARCHAR(150)
email       VARCHAR(150) UNIQUE
role        VARCHAR(50)  -- sme, consultant, corporate, other
created_at  TIMESTAMP WITH TIME ZONE
```

### `companies` (MVP Only)
```sql
id               SERIAL PRIMARY KEY
name             VARCHAR(200)
email            VARCHAR(150) UNIQUE
password_hash    VARCHAR(255)
sector           VARCHAR(100)
country          VARCHAR(2)
cif              VARCHAR(20)
cnae_code        VARCHAR(20)
last_login       TIMESTAMP
data_points      INTEGER
created_at       TIMESTAMP
```

---

## 🎉 Summary

You now have:
✅ Landing page collecting waitlist signups
✅ Admin endpoints to manage signups
✅ MVP dashboard that can view waitlist
✅ Ability to promote users to company accounts
✅ Shared database between both systems
✅ Complete integration ready to deploy!

**Next action:** Run the database migration and deploy the MVP backend!
