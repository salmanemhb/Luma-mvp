# 🚀 Quick Start - Integration Setup

## ✅ What's Done
- Landing backend admin endpoints (deploying)
- MVP backend waitlist integration (ready)
- MVP frontend waitlist page (ready)
- Database migration script (ready)

---

## 📋 Deployment Checklist

### 1. Landing Backend ⏳
- [x] Code pushed to GitHub
- [ ] Wait for Render deployment (3-5 min)
- [ ] Test: `curl https://luma-api-lbkc.onrender.com/api/admin/stats`

### 2. Database Migration
```sql
-- Run on Render PostgreSQL:
CREATE TABLE IF NOT EXISTS waitlist_submissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    company VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 3. MVP Backend
- [ ] Create Render web service
- [ ] Set DATABASE_URL to Render PostgreSQL
- [ ] Deploy from `mvp/luma-backend`

### 4. MVP Frontend
- [ ] Deploy to Vercel
- [ ] Set `VITE_API_URL` environment variable
- [ ] Visit `/admin/waitlist` page

---

## 🧪 Quick Test

```powershell
# 1. Check landing admin endpoints
Invoke-RestMethod "https://luma-api-lbkc.onrender.com/api/admin/stats"

# 2. Check MVP can read waitlist
Invoke-RestMethod "https://your-mvp-backend.onrender.com/api/admin/waitlist"

# 3. Test promote function
Invoke-RestMethod "https://your-mvp-backend.onrender.com/api/admin/waitlist/1/promote" -Method POST
```

---

## 📁 Key Files

**Landing Backend:**
- `server/routers/admin.py` - Admin endpoints
- `server/main.py` - Registered router

**MVP Backend:**
- `models/waitlist.py` - Waitlist model
- `routers/waitlist_admin.py` - Waitlist endpoints
- `migrations/002_add_waitlist_table.sql` - DB migration

**MVP Frontend:**
- `src/pages/admin/AdminWaitlist.tsx` - Waitlist page
- `src/lib/api.ts` - API methods
- `src/App.tsx` - Routes

---

## 🎯 User Flow

1. User → getluma.es → Submit form
2. Email → waitlist_submissions table
3. Admin → MVP dashboard → /admin/waitlist
4. Admin → Click "Promote"
5. System → Create Company account
6. User → Login with temp password

---

## ⚡ Environment Variables

**MVP Backend:**
```
DATABASE_URL=<Render PostgreSQL URL>
SUPABASE_URL=<Supabase URL>
SUPABASE_KEY=<Supabase key>
ADMIN_EMAILS=salmane@getluma.es
```

**MVP Frontend:**
```
VITE_API_URL=<MVP backend URL>
```

---

**See INTEGRATION_SUMMARY.md for full details**
