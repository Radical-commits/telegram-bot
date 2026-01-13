# Keep Bot Awake on Render.com Free Tier

## The Problem

Render.com free tier instances **sleep after 15 minutes of inactivity**. When a user tries to chat with your bot after it's asleep, they experience a 30-60 second delay while the instance wakes up.

## The Solution

**Health Check Endpoint + External Ping Service**

Your bot now includes a built-in HTTP health check server. An external service (UptimeRobot) will ping it every 10 minutes to keep it awake.

---

## Step 1: Deploy Your Bot to Render ✅

Your bot already has the health check endpoint built in! When you deploy to Render.com:

1. The bot starts on the PORT provided by Render (usually 10000)
2. Health endpoint is available at: `https://your-app.onrender.com/health`
3. Root endpoint shows status at: `https://your-app.onrender.com/`

**Health Check Response:**
```json
{
  "status": "ok",
  "bot": "telegram-translation-bot",
  "uptime_seconds": 3600,
  "uptime": "1:00:00",
  "timestamp": "2024-01-13T12:00:00",
  "message": "Bot is running"
}
```

---

## Step 2: Set Up UptimeRobot (5 minutes)

### 1. Sign Up for UptimeRobot

Go to https://uptimerobot.com and create a free account.

**Free Plan Includes:**
- 50 monitors
- 5-minute check intervals
- Email/SMS/Webhook alerts
- 100% free forever

### 2. Create a New Monitor

After logging in:

1. Click **"+ Add New Monitor"**
2. Fill in the details:

   **Monitor Type:** `HTTP(s)`

   **Friendly Name:** `Telegram Translation Bot`

   **URL:** `https://your-app-name.onrender.com/health`
   *(Replace `your-app-name` with your actual Render app name)*

   **Monitoring Interval:** `Every 10 minutes` ⭐
   *(Free tier allows 5-minute minimum, but 10 is sufficient)*

   **Monitor Timeout:** `30 seconds`

   **Alert Contacts:** Your email (optional - for downtime notifications)

3. Click **"Create Monitor"**

### 3. Verify It's Working

Within 10 minutes:
- Check UptimeRobot dashboard
- Status should show **"Up"** with green indicator
- Response time should be < 1 second

---

## Step 3: Find Your Render App URL

### Option 1: From Render Dashboard
1. Go to https://dashboard.render.com
2. Click on your bot service
3. Look for the URL at the top (e.g., `https://telegram-bot-abc123.onrender.com`)

### Option 2: Check Deploy Logs
```
==> Deploying...
==> Your service is live at https://telegram-bot-abc123.onrender.com
```

### Option 3: Test Locally First
Before deploying, test the health endpoint locally:
```bash
# Terminal 1: Start the bot
uv run python main.py

# Terminal 2: Test health endpoint
curl http://localhost:8080/health
```

You should see JSON response with status "ok".

---

## Alternative Ping Services

### Cron-job.org (Alternative to UptimeRobot)

**URL:** https://cron-job.org

**Setup:**
1. Sign up for free
2. Create new cron job
3. URL: `https://your-app.onrender.com/health`
4. Schedule: Every 10 minutes (`*/10 * * * *`)
5. Method: GET

**Pros:**
- Unlimited free jobs
- More flexible scheduling
- No monitor limits

### BetterUptime (Premium Alternative)

**URL:** https://betteruptime.com

**Free Plan:**
- 3 monitors
- 30-second checks
- Advanced alerting

---

## How It Works

```
┌─────────────┐
│ UptimeRobot │ ──Every 10 min──> GET /health
└─────────────┘

┌──────────────────┐
│  Your Bot on     │ <── Ping received!
│  Render.com      │ ──> Returns: {"status": "ok"}
└──────────────────┘
        │
        ├─ Stays awake (no 15min timeout)
        ├─ Responds to Telegram messages instantly
        └─ Uptime tracked by UptimeRobot
```

---

## Expected Behavior

### ✅ With Health Checks (Recommended)
- Bot responds instantly 24/7
- No delays for users
- ~99.9% uptime
- Free

### ❌ Without Health Checks
- Bot sleeps after 15 minutes
- First message after sleep: 30-60 second delay
- Users think bot is broken
- Poor user experience

---

## Monitoring & Alerts

### Set Up Downtime Alerts

In UptimeRobot:
1. Go to "My Settings"
2. Click "Add Alert Contact"
3. Add your email/SMS
4. Enable alerts for your monitor

**You'll be notified if:**
- Bot goes down
- Health check fails
- Response time is slow

### Check Uptime Statistics

UptimeRobot provides:
- **Uptime percentage** (goal: 99%+)
- **Response time graphs**
- **Downtime logs**
- **Public status pages**

---

## Troubleshooting

### Monitor Shows "Down"

**Check Render logs:**
```
Dashboard → Your Service → Logs
```

Look for:
- `Health check server started on port 10000` ✅
- Any error messages
- Deployment status

**Common issues:**
1. **Wrong URL** - Make sure it ends with `/health`
2. **Port not set** - Render should auto-provide PORT env var
3. **Bot crashed** - Check Render logs for errors

### Monitor Shows "Paused"

UptimeRobot free tier pauses monitors after 30 days of downtime. If your bot is down for over a month, UptimeRobot stops checking.

**Solution:** Fix the bot and unpause the monitor.

### Health Check Times Out

If response takes > 30 seconds:
- Bot might be overloaded
- Groq API might be slow
- Consider upgrading Render plan

---

## Cost Analysis

### Completely Free Setup (Recommended)
- **Render.com:** Free tier (750 hours/month = 31 days)
- **UptimeRobot:** Free (50 monitors)
- **Monthly cost:** $0

**Limitation:** Technically Render free tier is 750 hours/month. With 24/7 uptime, you'll hit this limit. However, Render's monthly cycle usually resets, and downtime is minimal.

### If You Hit 750 Hour Limit

**Symptoms:**
- Bot stops mid-month
- "Out of free hours" message

**Solutions:**
1. **Upgrade to Starter ($7/month)** - Unlimited hours
2. **Use multiple free accounts** (not recommended)
3. **Switch to Fly.io** - More generous limits

---

## Advanced: Multiple Health Endpoints

If you want redundancy, set up multiple monitors:

```
Monitor 1: /health (main)
Monitor 2: / (backup)
Monitor 3: /health (from different Upt imeRobot region)
```

---

## Next Steps

1. ✅ Deploy bot to Render.com
2. ✅ Sign up for UptimeRobot
3. ✅ Create monitor with /health URL
4. ✅ Verify status shows "Up"
5. ✅ Test by messaging bot after 20 minutes

**Your bot will stay awake 24/7! 🎉**

---

## Quick Reference

**Health Endpoint:** `https://your-app.onrender.com/health`

**UptimeRobot URL:** https://uptimerobot.com

**Ping Interval:** Every 10 minutes

**Expected Response:**
```json
{"status": "ok", "bot": "telegram-translation-bot"}
```

**Setup Time:** 5 minutes

**Monthly Cost:** $0

---

## FAQ

**Q: Will this use up my Render free hours?**
A: Yes, but it keeps your bot running. You get 750 hours/month (31.25 days), which covers most of the month.

**Q: What happens if I hit the 750-hour limit?**
A: Your bot will sleep until the next billing cycle (monthly reset) or you can upgrade to $7/month for unlimited hours.

**Q: Can I use a different ping service?**
A: Yes! Any service that can make HTTP GET requests every 5-10 minutes will work.

**Q: Does the health check affect performance?**
A: No. It's a simple HTTP response that takes <10ms to generate.

**Q: Can I disable the health check?**
A: Yes, but your bot will sleep after 15 minutes of inactivity. Not recommended.

**Q: What if UptimeRobot goes down?**
A: Your bot will sleep after 15 minutes. Consider using multiple ping services for redundancy.

---

**Version:** v0.4.0
**Status:** ✅ Production Ready
**Last Updated:** 2024-01-13
