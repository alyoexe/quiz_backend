# Deploy to Render - Complete Guide

## 📋 Prerequisites

- GitHub account (to push your code)
- Render account (sign up at https://render.com)
- Your Django project with PostgreSQL configured

## 🚀 Step 1: Prepare Your Project

### 1.1 Update requirements.txt
Your `requirements.txt` should include:
```
Django==5.1.6
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-allauth==0.65.0
python-dotenv==1.0.0
groq==0.10.0
google-auth==2.31.0
PyJWT==2.8.1
requests==2.31.0
Pillow==10.1.0
PyPDF2==4.0.1
psycopg2-binary==2.9.9
gunicorn==23.0.0
```

✅ Already done!

### 1.2 Verify Procfile exists
```
web: gunicorn quiz_backend.wsgi:application --bind 0.0.0.0:$PORT
```

✅ Already created!

### 1.3 Verify render.yaml exists
This file configures your Render deployment automatically.

✅ Already created!

---

## 📤 Step 2: Push to GitHub

### 2.1 Create a GitHub Repository

1. Go to https://github.com/new
2. Name: `quiz_backend`
3. Make it **Public** (for free Render deployment)
4. Click "Create repository"

### 2.2 Push Your Code

Run these commands in PowerShell from your project directory:

```powershell
cd C:\Users\lenovo\Desktop\quiz_backend

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial Quiz Backend commit"

# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/quiz_backend.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Expected output:**
```
Enumerating objects: ...
Counting objects: ...
Writing objects: ...
Total 123 (delta 45)
remote:
remote: Create a pull request for 'main' on GitHub by visiting:
remote: https://github.com/YOUR_USERNAME/quiz_backend/pull/new/main
```

✅ Code is now on GitHub

---

## 🔧 Step 3: Deploy on Render

### 3.1 Connect GitHub to Render

1. Go to https://render.com
2. Sign in (or create account)
3. Click "New+" → "Blueprint"
4. Click "Connect a Repository"
5. Authorize GitHub and select `quiz_backend`
6. Click "Connect"

### 3.2 Deploy from render.yaml

Render will automatically:
- ✅ Read `render.yaml`
- ✅ Create PostgreSQL database
- ✅ Deploy Django app
- ✅ Run migrations
- ✅ Start the web service

The deployment will start automatically!

---

## 🔐 Step 4: Configure Environment Variables

### 4.1 In Render Dashboard

1. Go to your `quiz-backend` service
2. Click "Environment"
3. Add these variables:

```
SECRET_KEY = [Auto-generated, keep as is]
DEBUG = False
ALLOWED_HOSTS = *.onrender.com,yourdomain.com
CORS_ALLOWED_ORIGINS = https://yourdomain.com
GOOGLE_CLIENT_ID = your-google-client-id-here
GROQ_API_KEY = your-groq-api-key-here
```

### 4.2 Get Your Render URL

1. Click on your `quiz-backend` service
2. Find the URL at the top (e.g., `https://quiz-backend-xxxxx.onrender.com`)
3. Add this to Google OAuth:
   - Go to Google Cloud Console
   - Credentials → Your OAuth Client
   - Authorized JavaScript origins: Add `https://quiz-backend-xxxxx.onrender.com`

---

## ✅ Step 5: Verify Deployment

### 5.1 Check if Running

```
https://quiz-backend-xxxxx.onrender.com/api/register/
```

Should return:
```json
{
  "error": "POST method required"
}
```

(This shows the API is working!)

### 5.2 Check Logs

In Render Dashboard:
- Click `quiz-backend` service
- Click "Logs"
- Should see "Starting development server..."

### 5.3 Test an Endpoint

```bash
# Test registration endpoint
curl -X POST https://quiz-backend-xxxxx.onrender.com/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"testpass123"}'
```

You should get a response!

---

## 🎯 Common Issues & Solutions

### Issue: "Build failed - ModuleNotFoundError"

**Solution:**
- Check `requirements.txt` has all packages
- Verify `psycopg2-binary` is included
- Redeploy after fixing

### Issue: "Database connection error"

**Solution:**
- Render automatically provides `DB_*` env vars
- Don't manually set them
- Check Render PostgreSQL service is running
- Check migrations tab in Render

### Issue: "504 Bad Gateway"

**Solution:**
- Wait 2-3 minutes for cold start
- Check application logs
- Redeploy from Render dashboard

### Issue: "CSRF verification failed"

**Solution:**
Update `CORS_ALLOWED_ORIGINS` in environment:
```
https://yourdomain.com,https://www.yourdomain.com
```

---

## 📊 Render Free Tier Limits

- **Compute**: 0.5 CPU, 512 MB RAM
- **Database**: 100 MB PostgreSQL
- **Bandwidth**: Unlimited
- **Inactive spins down**: After 15 min with no traffic

To upgrade:
- Click "Settings" on service
- Change plan from "Free" to "Starter" ($7/month)

---

## 🔄 Deploying Updates

Every time you push to GitHub:

```powershell
# Make changes
# ...

# Commit and push
git add .
git commit -m "Your message"
git push origin main
```

Render will **automatically redeploy** in 1-2 minutes!

---

## 🎯 Next Steps

1. **Update Google OAuth**
   - Add `https://quiz-backend-xxxxx.onrender.com` to authorized origins
   - Update frontend API URL to your Render URL

2. **Update Frontend**
   - Change API URL from `http://localhost:8000` to `https://quiz-backend-xxxxx.onrender.com`
   - Update CORS in frontend

3. **Custom Domain** (Optional)
   - Render → Settings → Custom Domain
   - Point your domain to Render
   - Get free SSL certificate

4. **Monitor Performance**
   - Render Dashboard → Metrics
   - Check CPU, Memory, Response times

---

## 📞 Troubleshooting Commands

```bash
# View build logs
# In Render: Service → Events

# Clear cache & redeploy
# In Render: Service → More → Clear Build Cache → Redeploy

# SSH into service (Starter plan only)
# In Render: Service → Shell
```

---

## 🚀 You're Live!

Your Quiz Backend is now deployed on Render! 🎉

**Your API URL:**
```
https://quiz-backend-xxxxx.onrender.com
```

**Available Endpoints:**
- `POST /api/register/` - Create account
- `POST /api/login/` - Login
- `POST /api/google-auth/` - Google OAuth
- `POST /api/upload-pdf/` - Upload and generate quiz
- `GET /api/user/quiz-history/` - Get quiz history

---

## 📚 Resources

- **Render Docs**: https://render.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/5.1/howto/deployment/
- **Gunicorn Docs**: https://docs.gunicorn.org/

---

**Deployment Status: ✅ LIVE**

Good luck! Your backend is now production-ready! 🚀
