# 🚀 Backend Deployment Guide

## Quick Summary
✅ **Ready to deploy!** Your backend can be hosted on:
- **Render** (Recommended - Easiest)
- Railway
- Fly.io
- PythonAnywhere

---

## 🎯 Easiest Option: Deploy on Render (FREE)

### Step-by-Step Instructions:

### 1️⃣ **Prepare Your Code**
Make sure all changes are committed to Git:
```bash
cd /Users/atharvalade/GitHub-Chat-Frontend
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2️⃣ **Create Render Account**
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### 3️⃣ **Deploy Backend**

**Option A: Using Blueprint (Automatic - Recommended)**
1. Click "New +" → "Blueprint"
2. Connect your GitHub repository
3. Select the repository: `GitHub-Chat-Frontend`
4. Render will auto-detect `render.yaml`
5. Add your environment variables:
   - `GEMINI_API_KEY`: Your Gemini API key (from https://aistudio.google.com/apikey)
6. Click "Apply"
7. Wait 5-10 minutes for deployment ⏳

**Option B: Manual Setup**
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `github-chat-backend` (or any name)
   - **Region**: Choose closest to you
   - **Branch**: `main` (or your branch)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
4. Add Environment Variables:
   - `GEMINI_API_KEY`: Your API key
   - `GEMINI_MODEL`: `gemini-1.5-flash`
   - `ENV`: `production`
5. Click "Create Web Service"

### 4️⃣ **Get Your Backend URL**
After deployment completes, you'll get a URL like:
```
https://github-chat-backend-xxxx.onrender.com
```

### 5️⃣ **Test Your Backend**
```bash
curl https://your-backend-url.onrender.com/healthcheck
```

You should see: `{"status":"ok"}`

### 6️⃣ **Update Frontend**
Edit `frontend/lib/api.ts`:
```typescript
export const API_BASE_URL = 'https://your-backend-url.onrender.com';
```

### 7️⃣ **Deploy Frontend** (Optional)
If you want to deploy the frontend too:
1. Go to https://vercel.com
2. Sign in with GitHub
3. Click "Add New" → "Project"
4. Import your repository
5. Configure:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
6. Deploy!

---

## ⚙️ Alternative: Railway (Also Easy)

### Steps:
1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Click on the service → Settings:
   - **Root Directory**: `/backend`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables in the "Variables" tab:
   - `GEMINI_API_KEY`
   - `GEMINI_MODEL=gemini-1.5-flash`
   - `ENV=production`
7. Railway will auto-deploy!

---

## 🔍 Verification Checklist

Before deploying, verify:
- ✅ CORS is enabled (fixed!)
- ✅ `requirements.txt` exists
- ✅ `GEMINI_API_KEY` is ready
- ✅ Code is pushed to GitHub
- ✅ `.gitignore` includes `.env`

After deploying:
- ✅ Health check works: `/healthcheck`
- ✅ Can initialize repo: `POST /api/repository/initialize`
- ✅ Can chat: `POST /api/chat`

---

## 🐛 Common Issues & Solutions

### Issue: "Module not found"
**Solution**: Make sure `requirements.txt` includes all dependencies

### Issue: "GEMINI_API_KEY not set"
**Solution**: Add the environment variable in Render/Railway dashboard

### Issue: "CORS error from frontend"
**Solution**: Already fixed! CORS is now enabled in production

### Issue: "Port binding error"
**Solution**: Make sure start command uses `$PORT` variable:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Issue: "Cold starts / slow first request"
**Solution**: This is normal on free tier. First request after inactivity takes ~30s

---

## 💰 Free Tier Limits

**Render Free Tier:**
- ✅ 750 hours/month (enough for one service 24/7)
- ✅ Automatic HTTPS
- ✅ Auto-deploy from GitHub
- ⚠️ Sleeps after 15 mins of inactivity (wakes up in ~30s)
- ⚠️ 512 MB RAM

**Railway Free Tier:**
- ✅ $5 free credit/month
- ✅ No sleep time
- ✅ Auto-deploy from GitHub
- ⚠️ Credit runs out if heavily used

---

## 🎉 Next Steps

After deployment:
1. Update frontend API URL
2. Test all endpoints
3. Monitor logs in Render/Railway dashboard
4. Set up custom domain (optional)
5. Consider upgrading to paid tier for production use

---

## 📞 Support

If you encounter issues:
- Check Render/Railway logs
- Verify environment variables are set
- Test locally first: `uvicorn main:app --reload`
- Check CORS configuration

---

**You're all set! 🚀**
Your backend is ready to be deployed in ~10 minutes!

