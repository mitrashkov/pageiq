# Keep Render API Awake for FREE - Workaround Guide

If you prefer **Render** but want to avoid the free tier sleeping issue, use this free workaround with **UptimeRobot**.

---

## The Problem

Render's free tier puts services to sleep after **15 minutes of inactivity**. This breaks:
- ❌ RapidAPI health checks
- ❌ First-time API users (slow response)
- ❌ Production reliability

---

## The Free Solution: UptimeRobot

**UptimeRobot** is a FREE service that pings your API every 5 minutes, keeping it "awake".

### How It Works

```
UptimeRobot (Free) 
    ↓
Every 5 minutes, sends HTTP GET request to your API
    ↓
Your API responds (wakes up if sleeping)
    ↓
Render keeps instance alive
    ↓
Result: No sleeping, no cost 🎉
```

---

## Setup Instructions

### Step 1: Create UptimeRobot Account

1. Go to https://uptimerobot.com
2. Click **"Sign Up"** (free tier available)
3. Enter email and password
4. Verify email
5. Log in

### Step 2: Create Monitor

1. Click **"Add New Monitor"** (or "+" button)
2. Fill in:

| Field | Value |
|-------|-------|
| **Monitor Type** | `HTTPS` |
| **Friendly Name** | `PageIQ API Health Check` |
| **URL** | `https://pageiq.pompora.dev/api/v1/ping` |
| **Monitoring Interval** | `5 minutes` |
| **Enable Notifications** | ✅ Yes (so you know if it goes down) |

3. Click **"Create Monitor"**

### Step 3: Add Email Alerts (Optional)

1. Click the monitor you just created
2. Click **"Alert Contacts"** tab
3. Add your email
4. Set alert frequency: `Alert once when down, after 15 minutes of monitoring`

### Step 4: Verify It's Working

1. Wait 5 minutes
2. Go back to UptimeRobot dashboard
3. Your monitor should show:
   - ✅ Green checkmark (up)
   - ✅ Last check time: ~5 minutes ago
   - ✅ Uptime: 100%

---

## Cost: $0 🎉

- UptimeRobot: Free
- Render API: Free (no sleeping because UptimeRobot pings it)
- Total: **$0/month**

---

## How Long Will This Keep It Awake?

UptimeRobot pings every 5 minutes → Render never goes to sleep → Indefinite uptime

---

## What Happens During Peak Usage?

When real users hit your API (e.g., 100 requests/day):
- ✅ Users are also "pinging" the API
- ✅ UptimeRobot continues pinging every 5 minutes
- ✅ Render free tier never sleeps

---

## Comparison

| Feature | Render Free + UptimeRobot | Railway Free |
|---------|---------------------------|--------------|
| **Base Cost** | $0 | $0 (with $5 credit) |
| **API Sleeping** | NO (UptimeRobot prevents) | NO (built-in) |
| **Setup Complexity** | Easy (2 steps) | Easy (1 step) |
| **Reliability** | Very Good | Excellent |
| **Credit** | None needed | $5/month given |
| **Overall** | ✅ Recommended | ✅ Also Great |

---

## ⚠️ Important Notes

1. **UptimeRobot Health Check Request**
   - Adds ~1 request every 5 minutes (tiny impact)
   - ~288 requests/month from UptimeRobot
   - Your tier includes millions of requests

2. **If API Really Goes Down**
   - UptimeRobot will send you an email alert
   - You'll know instantly to investigate

3. **This Works Indefinitely**
   - UptimeRobot has been running free for 10+ years
   - Very reliable service
   - Millions of users trust it

---

## Alternative: Hybrid Approach

**Best of Both Worlds:**

1. Use **Railway.app** ($5/month credit = always-on built-in)
2. Also use **UptimeRobot** (free monitoring + alerts)
3. Get professional-grade uptime without extra cost

---

## Quick Start

**To deploy on Render with FREE keep-alive workaround:**

1. Follow [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) to deploy
2. Follow these instructions to set up UptimeRobot
3. ✅ Your API now has 99.9% uptime at ZERO COST

---

## Recommendation

Choose one:

### Option A: Render + UptimeRobot
- Cost: $0
- Setup: 15 minutes
- Uptime: 99%
- Best for: Bootstrapped startups

### Option B: Railway.app
- Cost: $0 (free $5/month credit)
- Setup: 10 minutes
- Uptime: 99.9%
- Best for: Professional deployment

**My recommendation: Go with Railway.app** - simpler, no workarounds needed, built-in reliability.

But if you're deeply committed to Render, Option A works perfectly!
