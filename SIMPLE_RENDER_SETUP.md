# SIMPLE Render Deployment - Step by Step (NO CONFUSION)

**This is the ONLY guide you need. Follow it exactly.**

---

## The Goal

Deploy your API to Render so it's accessible at: `https://pageiq-api.onrender.com/api/v1`

Then later, point `pageiq.pompora.dev` to it via Cloudflare (after it's working).

---

## Prerequisites

- ✅ Code is already pushed to GitHub (you did this)
- ✅ Render account (free at https://render.com)
- ✅ That's it!

---

## Step 1: Go to Render Dashboard

1. Go to https://render.com/dashboard
2. Click **"New+"** button
3. Select **"Web Service"**

---

## Step 2: Connect GitHub

1. You'll see: "Build and deploy from a Git repository"
2. Click **"Connect GitHub"**
3. Authorize if needed
4. Search for: `pageiq` or `pageiq-api`
5. Click **"Connect"**

Render will now show deployment form.

---

## Step 3: Fill Out the Form (EXACTLY as shown)

| Field | Value |
|-------|-------|
| **Name** | `pageiq-api` |
| **Environment** | `Python 3` |
| **Region** | `Oregon` or your closest region |
| **Branch** | `main` |
| **Build Command** | `pip install --no-cache-dir -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

---

## Step 4: Expand "Advanced" Section

Click **"Advanced"** to see more options.

---

## Step 5: Add Environment Variables

You will see a section for environment variables. Add NOTHING. Leave it empty.

**Why?** Because your code has default values that work.

---

## Step 6: Select Plan

Under **"Plan"**, select:
- **Free** (if you want free, will sleep after 15 mins)
- **Starter** ($7/mo, always on) - RECOMMENDED

---

## Step 7: Deploy

Click **"Deploy Web Service"**

Watch the build process. It should:
- ✅ Show "Building..."
- ✅ Run "pip install"
- ✅ Say "Uvicorn running on 0.0.0.0:PORT"
- ✅ Show green checkmark "Your service is live"

Takes 2-5 minutes.

---

## Step 8: Get Your URL

Once deployed, Render gives you a public URL like:

```
https://pageiq-api.onrender.com
```

**COPY THIS URL. You'll need it next.**

---

## Step 9: Test It Works

In your terminal, run:

```bash
curl https://pageiq-api.onrender.com/api/v1/ping
```

You should get back:
```json
{"status":"ok","timestamp":"..."}
```

If you see this → **YOUR API IS WORKING** ✅

---

## Step 10: (LATER) Point pageiq.pompora.dev to It

Once it's working, we'll set up Cloudflare DNS so `pageiq.pompora.dev` points to your Render URL.

**But first, verify the API is working with Step 9 above.**

---

## Troubleshooting

### ❌ Build Failed

Go to the **"Logs"** tab and look for the error message.

**Most common:** Missing dependency in requirements.txt
- Let me know the exact error
- I'll fix it

### ❌ 502 Bad Gateway

Check **"Logs"** tab. Look for error in startup.

**Most common:** Same as above, or port not binding.
- Share the error
- I'll fix it

### ❌ Deployment is slow

First deploy takes longer. This is normal. Wait 5-10 minutes.

### ❌ "Service is sleeping"

You selected **Free** plan. This happens after 15 minutes idle.

Solution: Upgrade to **Starter** ($7/mo) or use the UptimeRobot workaround.

---

## Once It's Working

Do NOT do anything else yet. Just:

1. ✅ Verify you can call `/api/v1/ping`
2. ✅ Tell me it's working
3. ✅ Then we'll set up the Cloudflare part

---

## That's It!

This is simpler than the previous guides. Just follow these 10 steps exactly.

If something goes wrong, **share the exact error message** and I'll fix it.

**You should see deployment succeed within 5 minutes.**
