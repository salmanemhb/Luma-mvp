# Luma MVP Deployment Guide

## 🚀 Deployment Status

### Backend (Render)
- **URL**: https://luma-mvp-backend.onrender.com
- **Status**: ✅ Deployed
- **Health Check**: https://luma-mvp-backend.onrender.com/health

### Frontend (Vercel)
- **Repository**: https://github.com/salmanemhb/Luma-mvp
- **Status**: 🔄 Deploying
- **Expected URL**: https://luma-mvp.vercel.app

---

## ⚙️ Vercel Configuration

### 1. Environment Variables (CRITICAL)

Go to your Vercel project settings and add this environment variable:

```
Key: VITE_API_URL
Value: https://luma-mvp-backend.onrender.com
```

**Steps:**
1. Go to https://vercel.com/dashboard
2. Select your `Luma-mvp` project
3. Go to **Settings** → **Environment Variables**
4. Add `VITE_API_URL` with the value above
5. Make sure it's enabled for **Production**, **Preview**, and **Development**
6. Click **Save**
7. Trigger a new deployment (Deployments → Click on latest → Redeploy)

### 2. Build Settings

Your Vercel configuration should be:

- **Framework Preset**: Vite
- **Root Directory**: `luma-frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

---

## 🔗 Backend CORS Configuration

The backend is already configured to accept requests from:
- `http://localhost:5173` (local development)
- `https://luma-mvp.vercel.app` (production)
- `https://*.vercel.app` (preview deployments)

✅ CORS is properly configured!

---

## 🗄️ Database Configuration

### Shared PostgreSQL (Render)

Both the landing page backend and MVP backend share the same database:

- **Host**: `dpg-d3psqv8gjchc73asj2sg-a.oregon-postgres.render.com`
- **Database**: Connected via `DATABASE_URL` environment variable
- **Tables**:
  - `waitlist_submissions` - Shared between landing and MVP
  - `companies` - MVP only
  - `users` - MVP only
  - `uploads`, `analyses`, `reports` - MVP only

### Run Database Migration (If Not Done)

Connect to the database and run:
```sql
-- File: luma-backend/migrations/002_add_waitlist_table.sql
-- (Already created, just needs execution if table doesn't exist)
```

---

## 🧪 Testing the Integration

### 1. Test Backend Health
```bash
curl https://luma-mvp-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": 1234567890.123,
  "services": {
    "database": "connected",
    "storage": "available",
    "ocr": "ready"
  }
}
```

### 2. Test Frontend (After Deployment)

1. **Login Page**: https://luma-mvp.vercel.app/login
2. **Dashboard**: https://luma-mvp.vercel.app/dashboard (requires login)
3. **Admin Waitlist**: https://luma-mvp.vercel.app/admin/waitlist

### 3. Test End-to-End Flow

1. Go to https://getluma.es (landing page)
2. Submit waitlist form
3. Check email for confirmation
4. Go to https://luma-mvp.vercel.app/admin/waitlist
5. Login with admin credentials
6. See the waitlist entry
7. Click "Promote to Company"
8. User should be able to login with temporary password

---

## 🔐 Admin Access

### Temporary API Key
Current admin endpoints use: `temp_admin_key_replace_me`

**To use admin endpoints**, include this header:
```
X-Admin-API-Key: temp_admin_key_replace_me
```

### Admin Emails
Configure in Render backend environment variables:
```
ADMIN_EMAILS=salmane.mohib@gmail.com
```

---

## 📝 Next Steps

### High Priority
1. ✅ Set `VITE_API_URL` in Vercel environment variables
2. ✅ Verify frontend deployment succeeds
3. ⏳ Test login flow
4. ⏳ Test waitlist integration
5. ⏳ Replace temporary API key with real JWT authentication

### Medium Priority
- Update CORS origins with actual Vercel URL (currently using wildcards)
- Configure custom domain (optional)
- Set up monitoring and error tracking
- Add rate limiting

### Low Priority
- Implement real-time notifications
- Add analytics tracking
- Configure CDN for assets
- Set up automated backups

---

## 🆘 Troubleshooting

### Issue: Frontend shows unstyled content
**Solution**: CSS is already fixed in commit `3a76b1a`

### Issue: API calls return CORS errors
**Solution**: 
1. Check Vercel URL matches CORS configuration
2. Backend updated in commit `ee7ed27` to allow Vercel deployments
3. Render will auto-deploy the update

### Issue: "getDashboardData is not exported"
**Solution**: Fixed in commit `a20996e` - standalone exports added

### Issue: Missing i18n translations
**Solution**: Fixed in commit `b7dffac` - i18n config added

### Issue: 401 Unauthorized on admin endpoints
**Solution**: 
1. Make sure request includes `X-Admin-API-Key` header
2. Or implement proper JWT authentication

---

## 📊 Deployment URLs Summary

| Service | URL | Status |
|---------|-----|--------|
| Landing Frontend | https://getluma.es | ✅ Live |
| Landing Backend | https://luma-api-lbkc.onrender.com | ✅ Live |
| MVP Backend | https://luma-mvp-backend.onrender.com | ✅ Live |
| MVP Frontend | https://luma-mvp.vercel.app | 🔄 Deploying |
| Database | Render PostgreSQL (shared) | ✅ Live |

---

## 🎉 When Everything Works

You should be able to:
1. ✅ Visit https://luma-mvp.vercel.app and see styled login page
2. ✅ Login with test credentials
3. ✅ Navigate to dashboard and see charts
4. ✅ Upload files for analysis
5. ✅ Generate reports
6. ✅ Access admin panel at /admin/waitlist
7. ✅ See waitlist submissions from getluma.es
8. ✅ Promote waitlist users to company accounts

---

## 📞 Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check Render backend logs
3. Check browser console for errors
4. Verify environment variables are set correctly
