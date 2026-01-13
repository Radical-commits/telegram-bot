# Quick UptimeRobot Setup (5 Minutes)

Your bot now has a built-in health check endpoint! Follow these steps to keep it awake 24/7 on Render.com free tier.

## What Changed

✅ **Health endpoint added:** `https://your-app.onrender.com/health`
✅ **Returns JSON:** `{"status": "ok", "bot": "telegram-translation-bot", "uptime": "1:23:45"}`
✅ **Auto-starts** on Render.com deployment
✅ **No code changes** needed on your end

---

## 5-Minute Setup

### Step 1: Deploy to Render (if not already done)

Your bot is already configured! Just deploy/redeploy:
```bash
git push origin main
```

Render will automatically:
- Install new `aiohttp` dependency
- Start health server on port 10000
- Make `/health` endpoint available

### Step 2: Find Your App URL

Go to https://dashboard.render.com → Your Service

Copy the URL (looks like):
```
https://telegram-bot-xyz123.onrender.com
```

### Step 3: Sign Up for UptimeRobot

1. Go to https://uptimerobot.com
2. Click "Sign Up" (Free account)
3. Verify your email

### Step 4: Create Monitor

1. Click **"+ Add New Monitor"**
2. Fill in:
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `Telegram Bot`
   - **URL:** `https://your-app.onrender.com/health` ⬅️ Use YOUR URL!
   - **Interval:** `Every 10 minutes`
3. Click **"Create Monitor"**

### Step 5: Verify

Wait 10 minutes, then check:
- UptimeRobot dashboard shows green "Up" status ✅
- Your bot responds instantly to Telegram messages ✅

---

## That's It!

Your bot will now stay awake 24/7 for **$0/month**.

**How it works:**
- UptimeRobot pings `/health` every 10 minutes
- Render sees activity → keeps bot awake
- No 15-minute sleep timeout
- Users get instant responses

---

## Need Help?

**Full guide:** `docs/KEEP_AWAKE_GUIDE.md`

**Test health endpoint locally:**
```bash
uv run python main.py
# In another terminal:
curl http://localhost:8080/health
```

**Check if it's working on Render:**
```bash
curl https://your-app.onrender.com/health
```

Should return:
```json
{
  "status": "ok",
  "bot": "telegram-translation-bot",
  "uptime": "0:05:23"
}
```

---

## Common Issues

**"Connection refused"**
→ Bot might still be deploying. Wait 2-3 minutes.

**"404 Not Found"**
→ Make sure URL ends with `/health` (not `/health/`)

**Monitor shows "Down"**
→ Check Render logs for errors

---

**Questions?** See `docs/KEEP_AWAKE_GUIDE.md` for detailed troubleshooting!
