# Render Deployment Guide for PageIQ API

Complete step-by-step instructions to deploy PageIQ to Render.com with the domain `pageiq.pompora.dev`.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: GitHub Setup](#phase-1-github-setup)
3. [Phase 2: Render Deployment](#phase-2-render-deployment)
4. [Phase 3: Cloudflare DNS Configuration](#phase-3-cloudflare-dns-configuration)
5. [Phase 4: Verification](#phase-4-verification)
6. [Phase 5: Post-Deployment](#phase-5-post-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

You must have:

- ✅ A GitHub account with this repository pushed to it
- ✅ A Render.com account (free tier available at https://render.com)
- ✅ Cloudflare account with `pompora.dev` domain already added
- ✅ Your repository URL (format: `https://github.com/your-username/pageiq-api`)

---

## Phase 1: GitHub Setup

### Step 1.1: Initialize Git Repository (If Not Already Done)

```bash
cd e:\pompora-api\PageIQ

# Check if already a git repo
git status

# If not initialized:
git init
git add .
git commit -m "Initial commit: PageIQ API ready for Render deployment"
git branch -M main
```

### Step 1.2: Add Remote Repository

```bash
# Replace YOUR-USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR-USERNAME/pageiq-api.git
git push -u origin main
```

### Step 1.3: Verify on GitHub

- Go to https://github.com/YOUR-USERNAME/pageiq-api
- You should see all files including:
  - ✅ `requirements.txt`
  - ✅ `render.yaml`
  - ✅ `Procfile`
  - ✅ `.env.example`
  - ✅ `app/` folder
  - ✅ `README.md`

---

## Phase 2: Render Deployment

### Step 2.1: Create New Web Service on Render

1. Go to **https://render.com/dashboard**
2. Click **"New+" → "Web Service"**
3. Select **"Build and deploy from a Git repository"**

### Step 2.2: Connect Your GitHub Repository

1. Click **"Connect GitHub"** (if not already connected)
2. Authorize Render to access your GitHub account
3. Search for and select: `pageiq-api` repository
4. Click **"Connect"**

### Step 2.3: Configure Web Service Settings

Fill in the following fields:

| Field | Value | Notes |
|-------|-------|-------|
| **Name** | `pageiq-api` | Service identifier on Render |
| **Environment** | `Python 3` | Required for FastAPI |
| **Region** | `Oregon (US West)` | Or closest to your users |
| **Branch** | `main` | Deploy from main branch |
| **Build Command** | `pip install --no-cache-dir -r requirements.txt` | Installs all dependencies |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | Runs FastAPI server |

### Step 2.4: Set Environment Variables

Click **"Advanced"** to expand options, then:

1. Click **"Add Environment Variable"** for each:

```
DEBUG = false
ENVIRONMENT = production
SERVER_HOST = https://pageiq.pompora.dev
API_HOST = 0.0.0.0
DATABASE_URL = sqlite+pysqlite:///./pageiq.db
REDIS_URL = redis://localhost:6379/0
BACKEND_CORS_ORIGINS = https://pageiq.pompora.dev,https://www.pageiq.com,http://localhost:3000,http://localhost:8080
SECRET_KEY = <generate-a-random-secure-key>
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
LOG_LEVEL = info
```

**To generate `SECRET_KEY`**, run in your terminal:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 2.5: Select Plan

1. Under **"Plan"**, select:
   - **"Starter"** - $7/month (Recommended for production)
     - Always-on instance
     - 1 GB RAM
     - Faster cold starts
   - *Note: Free tier will sleep after 15 mins inactivity - causes RapidAPI health checks to fail*

### Step 2.6: Deploy

1. Click **"Deploy Web Service"**
2. You'll see a blue progress indicator
3. Wait for deployment to complete (2-5 minutes)
4. ✅ When complete, you'll see "Your service is live"

### Step 2.7: Get Your Render URL

After deployment succeeds:

1. On the service page, you'll see a URL like: `https://pageiq-api.onrender.com`
2. **Save this URL** - you need it for Cloudflare DNS

---

## Phase 3: Cloudflare DNS Configuration

### Step 3.1: Log in to Cloudflare

1. Go to **https://dash.cloudflare.com**
2. Select your **"pompora.dev"** domain

### Step 3.2: Add DNS Record

1. Click **"DNS"** in the left sidebar
2. Click **"Add record"**
3. Fill in:

| Field | Value |
|-------|-------|
| **Type** | `CNAME` |
| **Name** | `pageiq` |
| **Target** | `pageiq-api.onrender.com` |
| **TTL** | `Auto` |
| **Proxy status** | ☁️ **Proxied** (orange cloud) |

4. Click **"Save"**

### Step 3.3: Verify DNS is Configured

1. You should see your new record:
   ```
   pageiq    CNAME    pageiq-api.onrender.com    Proxied
   ```

2. Wait 1-5 minutes for DNS to propagate

### Step 3.4: Test DNS Resolution

In terminal, run:

```bash
# Test DNS lookup
nslookup pageiq.pompora.dev

# Should show Cloudflare IPs like:
# 104.16.x.x or 172.64.x.x
```

---

## Phase 4: Verification

### Step 4.1: Test Health Endpoint

```bash
# Test that API is responding
curl -v https://pageiq.pompora.dev/api/v1/ping

# Should return 200 OK with:
# {"status":"ok","timestamp":"..."}
```

### Step 4.2: Test Full Analyze Endpoint (Optional)

```bash
# This will take 10-30 seconds
curl -X POST https://pageiq.pompora.dev/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'

# Should return website analysis data
```

### Step 4.3: Verify SSL Certificate

```bash
# Check SSL is valid
curl -I https://pageiq.pompora.dev/api/v1/ping

# Should show:
# HTTP/2 200
# And no SSL certificate warnings
```

### Step 4.4: Check Render Logs

1. Go to **https://render.com/dashboard**
2. Click **"pageiq-api"** service
3. Click **"Logs"** tab
4. Should show:
   - ✅ "Building..." messages
   - ✅ "pip install" output
   - ✅ "Uvicorn running on 0.0.0.0:PORT"
   - ✅ No error messages

### Step 4.5: Test from Different Locations

Test from multiple locations to ensure global accessibility:

```bash
# From your local machine
curl https://pageiq.pompora.dev/api/v1/ping

# From online tools like: https://httprequester.com
# Enter: https://pageiq.pompora.dev/api/v1/ping
# Click Send
```

---

## Phase 5: Post-Deployment

### Step 5.1: Update RapidAPI Configuration

1. Go to your RapidAPI API dashboard (https://rapidapi.com/developer/dashboard)
2. Select **"PageIQ"** API
3. Go to **"API Details" → "Settings"**
4. Update:
   - **Base URL**: `https://pageiq.pompora.dev/api/v1`
   - Keep Authentication: API Key (Header: `X-API-Key`)
   - Keep Rate limiting: Enabled
5. Click **"Save Changes"**

### Step 5.2: Configure Health Check in Render (Optional)

1. In Render service page, click **"Settings"**
2. Scroll to **"Health Check"**
3. Enable and set:
   - **Health Check Path**: `/api/v1/ping`
   - **Health Check Protocol**: `HTTPS`
   - **Initial Delay**: `30s`
   - **Interval**: `5m`

### Step 5.3: Set Up Uptime Monitoring

Use a free service like **UptimeRobot** to monitor your API:

1. Go to **https://uptimerobot.com**
2. Sign up (free tier)
3. Create new monitor:
   - **Monitor Type**: `HTTPS`
   - **URL**: `https://pageiq.pompora.dev/api/v1/ping`
   - **Check Interval**: `5 minutes`
4. Add email alerts

### Step 5.4: Enable Auto-Deploy from GitHub

To automatically redeploy when you push to GitHub:

1. In Render dashboard, go to **"pageiq-api" service**
2. Go to **"Settings"**
3. Under **"Git Configuration"**, enable:
   - ✅ "Auto-Deploy on Push"
4. This means: every `git push` to main automatically redeploys

### Step 5.5: Test Auto-Deploy (Optional)

1. Make a small change to a file (e.g., README.md)
2. Commit and push:
   ```bash
   git add .
   git commit -m "Test auto-deploy"
   git push origin main
   ```
3. Go to Render dashboard
4. You should see deployment starting automatically
5. After 2 minutes, deployment completes

---

## Troubleshooting

### ❌ Issue: 502 Bad Gateway

**Symptoms:**
- `curl https://pageiq.pompora.dev/api/v1/ping` returns 502 error

**Causes & Solutions:**

1. **API crashed during startup**
   - Go to Render dashboard → **pageiq-api** → **Logs**
   - Look for error messages
   - Common issues:
     - Missing environment variables → Add them in Settings
     - Import errors → Check requirements.txt is complete
     - Database error → Reset with `DATABASE_URL = sqlite+pysqlite:///./pageiq.db`

2. **Free tier sleeping**
   - Render free instances sleep after 15 minutes
   - Upgrade to **Starter plan** ($7/month)
   - Or upgrade temporarily to test

3. **Build command failed**
   - Check if `requirements.txt` has all dependencies
   - Run locally: `pip install -r requirements.txt`
   - Fix any errors, commit, push

### ❌ Issue: DNS not resolving

**Symptoms:**
- `nslookup pageiq.pompora.dev` shows SERVFAIL or doesn't resolve

**Solutions:**

1. Check Cloudflare DNS record:
   ```bash
   # Wait 5-10 minutes for propagation
   # Then retry:
   nslookup pageiq.pompora.dev
   ```

2. Verify CNAME record in Cloudflare:
   - DNS should show: `pageiq CNAME pageiq-api.onrender.com Proxied`
   - If not, re-add it

3. Check Render URL is correct:
   - Go to Render dashboard
   - Copy exact URL from service page
   - Should be: `pageiq-api.onrender.com` (no https://)

### ❌ Issue: SSL Certificate Error

**Symptoms:**
- `curl: (60) SSL certificate problem`

**Solution:**

1. Cloudflare provides SSL automatically when proxied (orange cloud)
2. Wait 10 minutes for SSL to provision
3. If still failing:
   - In Cloudflare, click the record
   - Ensure **Proxy status is orange** (☁️ Proxied, not grey)
   - Save and wait 5 more minutes

### ❌ Issue: 429 Too Many Requests

**Symptoms:**
- `curl` returns 429 status code

**Causes:**

1. You're hitting rate limit (expected for free tier)
   - Check `X-RateLimit-Remaining` header
   - Wait for `X-RateLimit-Reset` time

2. Cloudflare rate limiting (if you configured it)
   - Temporarily disable in Cloudflare settings
   - Or whitelist your IP

### ❌ Issue: Requests timing out

**Symptoms:**
- `curl` hangs or times out after 30 seconds

**Causes & Solutions:**

1. **Analysis takes too long**
   - `/api/v1/analyze` can take 10-30 seconds normally
   - This is expected
   - Wait for response

2. **Render instance too slow (free tier)**
   - Upgrade to Starter plan for better performance
   - Or optimize code performance

3. **Network latency**
   - Try from different location
   - Try different URL: `https://pageiq-api.onrender.com/api/v1/ping`

### ✅ Service is slow after deployment

**Cause:** Render cold-start for free tier

**Solutions:**
1. First request after 15 minutes is slow (free tier)
2. Upgrade to Starter plan to eliminate cold starts
3. Use UptimeRobot to keep service "warm"

---

## Useful Render Commands (via CLI)

If you install Render CLI (`npm install -g @render-com/cli`):

```bash
# View logs
render logs pageiq-api

# Restart service
render restart pageiq-api

# View service status
render list

# View detailed info
render info pageiq-api
```

---

## Next Steps

After deployment is verified:

1. ✅ **Test with RapidAPI**: Submit test API call from RapidAPI console
2. ✅ **Set up monitoring**: Use UptimeRobot or Sentry for alerts
3. ✅ **Configure backups**: Set up database backups if using PostgreSQL
4. ✅ **Document endpoints**: Ensure `/docs` is publicly accessible
5. ✅ **Launch on RapidAPI**: Publish to RapidAPI Marketplace

---

## Production Checklist

Before considering this production-ready:

- [ ] Deployed to Render
- [ ] Custom domain `pageiq.pompora.dev` configured
- [ ] SSL certificate valid
- [ ] Health check endpoint responding
- [ ] Logs show no errors
- [ ] Analysis endpoint responds within 30s
- [ ] Rate limiting working
- [ ] Uptime monitoring configured
- [ ] RapidAPI Base URL updated
- [ ] Auto-deploy from GitHub working
- [ ] Environment variables secured (not in code)

---

## Support & Help

If you encounter issues:

1. **Check Render Logs**: Always check the Logs tab first
2. **Check Cloudflare Status**: Verify DNS is "Proxied" (orange)
3. **Test Locally**: Run `python -m uvicorn app.main:app` locally to debug
4. **Review this guide**: Re-read the Troubleshooting section
5. **Check GitHub Issues**: See if others had same problem

---

## Congratulations! 🎉

Your PageIQ API is now live at:

```
🌐 https://pageiq.pompora.dev/api/v1
📚 https://pageiq.pompora.dev/docs
```

Next, submit to RapidAPI Marketplace and start earning from API subscriptions!
