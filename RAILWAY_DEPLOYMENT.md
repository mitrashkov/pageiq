# Railway.app Deployment Guide for PageIQ API

**Better Free Tier Alternative** - Uses Railway.app instead of Render to avoid sleeping issues.

Complete step-by-step instructions to deploy PageIQ to Railway.app with the domain `pageiq.pompora.dev`.

---

## Why Railway.app Instead of Render?

| Feature | Render Free | Railway Free | Winner |
|---------|-------------|--------------|--------|
| **Monthly Credit** | $0 | $5/month | Railway ✅ |
| **Sleep After Inactivity** | 15 mins | Never (with $5 credit) | Railway ✅ |
| **Build Time** | Unlimited | Unlimited | Tie |
| **Always-On** | No | Yes (with $5 credit) | Railway ✅ |
| **GitHub Auto-Deploy** | Yes | Yes | Tie |
| **Starter Plan Cost** | $7/month | Included free | Railway ✅ |

**Bottom Line:** Railway gives you **$5/month free credit**, which is enough to keep your API always-on. Render's free tier sleeps after 15 minutes, breaking RapidAPI health checks.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: Push to GitHub](#phase-1-push-to-github)
3. [Phase 2: Railway Deployment](#phase-2-railway-deployment)
4. [Phase 3: Cloudflare DNS Configuration](#phase-3-cloudflare-dns-configuration)
5. [Phase 4: Verification](#phase-4-verification)
6. [Phase 5: Post-Deployment](#phase-5-post-deployment)
7. [Cost Breakdown](#cost-breakdown)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

You must have:

- ✅ Your code pushed to GitHub
- ✅ A Railway.app account (free tier at https://railway.app)
- ✅ Cloudflare account with `pompora.dev` domain already added
- ✅ Your repository URL (format: `https://github.com/your-username/pageiq-api`)

---

## Phase 1: Push to GitHub

If you haven't pushed yet, do this now:

```bash
cd "e:\pompora-api\PageIQ"

# Check status
git status

# If changes exist, commit them
git add .
git commit -m "fix: Remove problematic OpenTelemetry dependencies and optimize for Railway deployment"

# Push to GitHub
git push -u origin main
```

Verify at: https://github.com/YOUR-USERNAME/pageiq-api

---

## Phase 2: Railway Deployment

### Step 2.1: Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub (recommended - auto-links your repos)
3. Authorize Railway to access your GitHub account

### Step 2.2: Create New Project

1. After login, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Search for and select: `pageiq-api`
4. Click **"Deploy"**

### Step 2.3: Configure Environment Variables

Railway will start building automatically. While it builds:

1. Go to your project dashboard
2. Click the **"Variables"** tab
3. Add each environment variable:

```
DEBUG = false
ENVIRONMENT = production
SERVER_HOST = https://pageiq.pompora.dev
API_HOST = 0.0.0.0
DATABASE_URL = sqlite+pysqlite:///./pageiq.db
REDIS_URL = redis://localhost:6379/0
BACKEND_CORS_ORIGINS = https://pageiq.pompora.dev,https://www.pageiq.com,http://localhost:3000
SECRET_KEY = <generate-a-random-secure-key>
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
LOG_LEVEL = info
```

**To generate `SECRET_KEY`**, run:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 2.4: Check Deployment Status

1. Click the **"Deployments"** tab
2. Watch the build progress
3. Should see:
   - ✅ "Building..."
   - ✅ "pip install requirements.txt"
   - ✅ "Deploying service"
4. Once green checkmark appears, deployment is complete

### Step 2.5: Get Your Railway URL

1. In project dashboard, click the service (e.g., `pageiq-api`)
2. Go to **"Settings"** tab
3. Under **"Environment"**, find and copy the **Public URL**
   - Format: `https://pageiq-api-prod-xxxx.railway.app`
4. **Save this URL** - you need it for Cloudflare DNS

### Step 2.6: Set Start Command (If Needed)

1. Still in service settings, scroll to **"Start Command"**
2. Verify it shows:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. If blank or wrong, set it to above value

---

## Phase 3: Cloudflare DNS Configuration

### Step 3.1: Log in to Cloudflare

1. Go to https://dash.cloudflare.com
2. Select your **"pompora.dev"** domain

### Step 3.2: Add DNS Record

1. Click **"DNS"** in the left sidebar
2. Click **"Add record"**
3. Fill in:

| Field | Value |
|-------|-------|
| **Type** | `CNAME` |
| **Name** | `pageiq` |
| **Target** | `pageiq-api-prod-xxxx.railway.app` (your Railway URL) |
| **TTL** | `Auto` |
| **Proxy status** | ☁️ **Proxied** (orange cloud) |

4. Click **"Save"**

### Step 3.3: Verify DNS is Configured

You should see:
```
pageiq    CNAME    pageiq-api-prod-xxxx.railway.app    Proxied
```

Wait 1-5 minutes for DNS to propagate.

### Step 3.4: Test DNS Resolution

```bash
nslookup pageiq.pompora.dev

# Should show Cloudflare IPs like:
# 104.16.x.x or 172.64.x.x
```

---

## Phase 4: Verification

### Step 4.1: Test Health Endpoint

```bash
curl -v https://pageiq.pompora.dev/api/v1/ping

# Should return 200 OK with:
# {"status":"ok","timestamp":"..."}
```

### Step 4.2: Test API Endpoint

```bash
# This will take 10-30 seconds
curl -X POST https://pageiq.pompora.dev/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'

# Should return analysis data
```

### Step 4.3: Verify SSL Certificate

```bash
curl -I https://pageiq.pompora.dev/api/v1/ping

# Should show:
# HTTP/2 200
# No SSL warnings
```

### Step 4.4: Check Railway Logs

1. Go to Railway dashboard
2. Click your `pageiq-api` service
3. Click **"Logs"** tab
4. Should show:
   - ✅ Build messages
   - ✅ "pip install" output
   - ✅ "Uvicorn running on 0.0.0.0:PORT"
   - ✅ No error messages

### Step 4.5: Test from Multiple Locations

```bash
# From local machine
curl https://pageiq.pompora.dev/api/v1/ping

# From online tool: https://httprequester.com
# Enter: https://pageiq.pompora.dev/api/v1/ping
# Click Send
```

---

## Phase 5: Post-Deployment

### Step 5.1: Update RapidAPI Configuration

1. Go to RapidAPI dashboard (https://rapidapi.com/developer/dashboard)
2. Select **"PageIQ"** API
3. Go to **"API Details" → "Settings"**
4. Update:
   - **Base URL**: `https://pageiq.pompora.dev/api/v1`
5. Click **"Save Changes"**

### Step 5.2: Enable Auto-Deploy from GitHub

1. In Railway project dashboard, go to **"Settings"**
2. Look for **"Auto-Deploy"** setting
3. Toggle **ON** to automatically redeploy when you push to GitHub

### Step 5.3: Set Up Uptime Monitoring (FREE - Keep API Warm)

This prevents the API from becoming inactive:

1. Go to **https://uptimerobot.com**
2. Sign up (free tier)
3. Create new monitor:
   - **Monitor Type**: `HTTPS`
   - **URL**: `https://pageiq.pompora.dev/api/v1/ping`
   - **Check Interval**: `5 minutes`
4. Add email alerts
5. **This pings your API every 5 minutes, keeping it "awake"**

### Step 5.4: Monitor Your Usage

Railway gives you **$5/month free credit**. To monitor:

1. In Railway dashboard, click **"Billing"** (or your project)
2. You should see free credit available
3. Typical costs:
   - Small API: $0-2/month
   - Medium API: $2-5/month
   - Beyond $5: Upgrade to paid plan

---

## Cost Breakdown

### First 3 Months (Free)

| Service | Cost | Notes |
|---------|------|-------|
| Railway.app | $0 | Free $5/month credit |
| Cloudflare DNS | $0 | Free tier |
| **Total** | **$0** | ✅ Completely free |

### After 3 Months (Pay-as-You-Go)

If you exceed $5/month Railway credit:
- **Usage-based pricing** starts
- Typical small API: $2-5/month
- **You can add credit or stop anytime**

---

## Troubleshooting

### ❌ Issue: Deployment Failed

**Solution:**
1. Go to Railway dashboard → **"Deployments"** tab
2. Click the failed deployment
3. Click **"View Logs"**
4. Look for error messages
5. Common issues:
   - Missing environment variables → Add in Variables tab
   - Port binding error → Verify Start Command
   - Python version incompatibility → Check build logs

### ❌ Issue: 502 Bad Gateway

**Solution:**
1. Check Railway logs for crashes
2. Verify all environment variables are set
3. Check if DATABASE_URL is correct
4. Restart deployment: Click service → **"Restart"**

### ❌ Issue: DNS not resolving

**Solution:**
1. Wait 5-10 minutes for DNS propagation
2. Verify Cloudflare CNAME record is correct
3. Ensure proxy status is orange (☁️ Proxied)
4. Check Railway Public URL is correct

### ❌ Issue: API is slow after 10 minutes

**Solution:**
1. This means API is becoming inactive
2. Set up UptimeRobot (Phase 5.3) to keep it warm
3. UptimeRobot pings every 5 minutes, preventing inactivity

### ✅ API is working but credit running out?

**Solution:**
1. Check Railway Billing dashboard
2. Add credit card to continue (optional)
3. Or optimize your API to use less resources:
   - Disable logging in production
   - Use caching more efficiently
   - Optimize database queries

---

## Railway CLI Commands (Optional)

If you install Railway CLI (`npm install -g @railway/cli`):

```bash
# Login to Railway
railway login

# View logs
railway logs

# View service status
railway status

# Deploy
railway up

# View variables
railway variables
```

---

## Next Steps

After deployment is verified:

1. ✅ **Test with RapidAPI**: Submit test API call
2. ✅ **Set up UptimeRobot**: Keep API warm (free monitoring)
3. ✅ **Monitor credit usage**: Check Railway billing
4. ✅ **Launch on RapidAPI**: Publish to marketplace
5. ✅ **Start earning**: Collect first subscriptions

---

## Production Checklist

- [ ] Code pushed to GitHub
- [ ] Deployed to Railway
- [ ] Custom domain `pageiq.pompora.dev` working
- [ ] SSL certificate valid
- [ ] Health check responding
- [ ] Logs show no errors
- [ ] Analysis endpoint working
- [ ] UptimeRobot monitoring set up
- [ ] RapidAPI Base URL updated
- [ ] Auto-deploy enabled
- [ ] Environment variables secured

---

## Congratulations! 🎉

Your PageIQ API is now live at:

```
🌐 https://pageiq.pompora.dev/api/v1
📚 https://pageiq.pompora.dev/docs
```

**With free Railway.app hosting and UptimeRobot monitoring, your API is production-ready at ZERO COST!**

Next: Submit to RapidAPI Marketplace and start earning 💰
