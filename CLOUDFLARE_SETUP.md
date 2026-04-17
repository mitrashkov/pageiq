# Cloudflare DNS Setup - 5 Simple Steps

Your API is live at: `https://pageiq-api.onrender.com/api/v1`

Now we'll make it accessible at: `https://pageiq.pompora.dev/api/v1`

---

## Step 1: Log in to Cloudflare

1. Go to https://dash.cloudflare.com
2. Log in with your account
3. Select **"pompora.dev"** domain from the list

---

## Step 2: Go to DNS Records

1. In left sidebar, click **"DNS"**
2. You'll see existing DNS records for your domain

---

## Step 3: Add New Record

1. Click **"Add record"** button
2. Fill in the form:

| Field | Value |
|-------|-------|
| **Type** | `CNAME` |
| **Name** | `pageiq` |
| **Target** | `pageiq-api.onrender.com` |
| **TTL** | `Auto` |
| **Proxy status** | ☁️ **Proxied** (orange cloud - IMPORTANT) |

3. Click **"Save"**

---

## Step 4: Verify DNS Record

You should now see in your DNS records:

```
pageiq    CNAME    pageiq-api.onrender.com    Proxied (☁️)
```

---

## Step 5: Wait for Propagation

DNS can take 1-5 minutes to propagate globally.

While waiting, you can test:

```bash
# Check DNS is resolving
nslookup pageiq.pompora.dev

# Should show Cloudflare IPs (104.16.x.x or 172.64.x.x)
```

---

## Test It Works

After 2-5 minutes, test:

```bash
curl https://pageiq.pompora.dev/api/v1/ping
```

Should return:
```json
{"status":"ok","message":"pong"}
```

✅ **If this works, you're DONE!** Your API is now live at `https://pageiq.pompora.dev/api/v1`

---

## What You've Accomplished

✅ Code pushed to GitHub
✅ API deployed to Render
✅ API responding at `pageiq-api.onrender.com`
✅ DNS configured in Cloudflare
✅ Custom domain `pageiq.pompora.dev` pointing to API
✅ SSL/TLS automatic (Cloudflare)

---

## 🚀 Your API is Production Ready!

**Accessible at:**
- `https://pageiq.pompora.dev/api/v1/ping` - Health check
- `https://pageiq.pompora.dev/docs` - API documentation (Swagger)
- `https://pageiq.pompora.dev/redoc` - ReDoc documentation

---

## Next Steps (Optional)

1. **RapidAPI Setup**: Update Base URL to `https://pageiq.pompora.dev/api/v1`
2. **Monitoring**: Set up UptimeRobot for alerts
3. **Analytics**: Check Render dashboard for usage stats

---

## That's It! 🎉

Your PageIQ API is now live and production-ready!
