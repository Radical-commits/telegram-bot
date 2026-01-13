# Telegram Translation Bot - Deployment Guide

Complete guide for deploying the Telegram Translation Bot to Render.com.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Deployment Steps](#deployment-steps)
3. [Post-Deployment Verification](#post-deployment-verification)
4. [Monitoring and Logs](#monitoring-and-logs)
5. [Troubleshooting](#troubleshooting)
6. [Cost Considerations](#cost-considerations)
7. [Maintenance](#maintenance)

## Pre-Deployment Checklist

Before deploying to Render.com, ensure you have:

### Required Accounts and Keys

- [ ] Telegram Bot Token from [@BotFather](https://t.me/botfather)
- [ ] Groq API Key from [Groq Console](https://console.groq.com/)
- [ ] Render.com account (sign up at [render.com](https://render.com))
- [ ] GitHub account (if deploying from GitHub)

### Code Preparation

- [ ] All code changes committed to your repository
- [ ] `requirements.txt` file is present and up-to-date
- [ ] `.env` file is NOT committed (check `.gitignore`)
- [ ] Code has been tested locally

### Environment Variables Ready

- [ ] `TELEGRAM_BOT_TOKEN` - Your bot token
- [ ] `GROQ_API_KEY` - Your Groq API key
- [ ] `LOG_LEVEL` - Set to `WARNING` for production (optional)

## Deployment Steps

### Option 1: Deploy from GitHub Repository

**Step 1: Push Code to GitHub**

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Prepare for production deployment"

# Add your GitHub repository
git remote add origin https://github.com/yourusername/telegram-bot.git
git push -u origin main
```

**Step 2: Create Web Service on Render.com**

1. Log in to [Render.com](https://render.com)
2. Click "New +" button in the top right
3. Select "Web Service"
4. Connect your GitHub account (if first time)
5. Select your repository from the list
6. Configure the service:

   **Basic Settings:**
   - Name: `telegram-translation-bot` (or your choice)
   - Region: Choose closest to your users
   - Branch: `main`
   - Root Directory: Leave empty (unless bot is in subdirectory)

   **Build Settings:**
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`

   **Instance Type:**
   - Select `Free` (sufficient for low-medium usage)

**Step 3: Set Environment Variables**

In the Render.com service configuration:

1. Scroll to "Environment Variables" section
2. Click "Add Environment Variable"
3. Add each variable:

   ```
   TELEGRAM_BOT_TOKEN = <your_bot_token_here>
   GROQ_API_KEY = <your_groq_api_key_here>
   LOG_LEVEL = WARNING
   ```

   **Important:** Do NOT wrap values in quotes!

**Step 4: Deploy**

1. Click "Create Web Service"
2. Render will start building and deploying your bot
3. Monitor the build logs in real-time
4. Wait for "Live" status (usually 2-5 minutes)

### Option 2: Manual Deploy (Blueprint)

If you prefer using the `render.yaml` configuration:

1. Ensure `render.yaml` is in your repository root
2. On Render.com dashboard, click "New +" → "Blueprint"
3. Connect to your repository
4. Render will detect `render.yaml` and configure automatically
5. Manually add environment variables (they're marked as `sync: false`)
6. Click "Apply" to deploy

## Post-Deployment Verification

### Check 1: Build Success

1. Go to your service on Render.com
2. Check "Events" tab - should show "Deploy succeeded"
3. Review build logs for any warnings or errors

### Check 2: Bot is Running

1. Open Telegram and search for your bot
2. Send `/start` command
3. Verify bot responds with welcome message
4. Test translation:
   ```
   /setlang spanish
   Hello, how are you?
   ```
5. Expected response: Translation to Spanish

### Check 3: Voice Messages

1. Send a voice message to the bot
2. Verify transcription and translation work
3. Check for any error messages

### Check 4: Logs

1. On Render.com, go to "Logs" tab
2. Verify bot startup message appears:
   ```
   Bot is running in production mode.
   ```
3. Check for any ERROR or WARNING messages
4. Send a test message and verify it's logged

## Monitoring and Logs

### Accessing Logs

**Via Render.com Dashboard:**
1. Go to your service
2. Click "Logs" tab
3. View real-time or historical logs
4. Use search/filter to find specific events

**Log Levels in Production:**
- `WARNING` and above are logged by default
- Adjust `LOG_LEVEL` environment variable to change
- Available levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### Key Events to Monitor

**Startup:**
```
Starting bot with log level: WARNING
Groq client initialized successfully
Bot is running in production mode
```

**User Activity:**
```
User 123456 started the bot
User 123456 set language to es
User 123456 sent text message for translation
```

**Errors to Watch:**
```
Rate limit hit in translate_text
Translation timeout after 30s
Transcription failed (APIError)
```

### Health Monitoring

**Automatic Restarts:**
- Render.com automatically restarts crashed services
- Bot will reconnect to Telegram API automatically
- Check "Events" tab for restart notifications

**Manual Health Check:**
1. Send `/start` to your bot daily
2. Verify response time is reasonable
3. Test translation periodically

## Troubleshooting

### Bot Not Responding

**Symptoms:**
- Bot doesn't reply to messages
- Shows as offline in Telegram

**Solutions:**
1. Check Render.com service status - should show "Live"
2. Review logs for errors:
   ```
   TELEGRAM_BOT_TOKEN environment variable is not set
   Failed to start bot
   ```
3. Verify environment variables are set correctly
4. Try manual restart: Render.com → Service → "Manual Deploy" → "Deploy latest commit"

### Authentication Errors

**Symptoms:**
- "Translation service authentication failed"
- "Transcription service authentication failed"

**Solutions:**
1. Verify `GROQ_API_KEY` is correct
2. Check Groq API key is active at [console.groq.com](https://console.groq.com/)
3. Regenerate API key if needed
4. Update environment variable on Render.com
5. Redeploy service

### Rate Limiting

**Symptoms:**
- "Translation service is busy. Please wait a moment and try again"
- Happens repeatedly for same user

**Solutions:**
1. Check Groq API usage at [console.groq.com](https://console.groq.com/)
2. Verify you're within free tier limits:
   - Whisper: 450 requests/minute
   - Llama: 30 requests/minute (free tier)
3. Consider upgrading Groq plan if needed
4. Inform users to wait before retrying

### Timeout Errors

**Symptoms:**
- "Translation took too long"
- "Transcription took too long"

**Solutions:**
1. Check Render.com service logs for patterns
2. Verify Groq API status: [status.groq.com](https://status.groq.com)
3. If persistent, increase timeouts in code:
   ```python
   TRANSLATION_TIMEOUT = 45  # Increase from 30s
   TRANSCRIPTION_TIMEOUT = 90  # Increase from 60s
   ```
4. Redeploy with new timeouts

### Voice Message Failures

**Symptoms:**
- "Audio format is not supported"
- "Transcription failed"

**Solutions:**
1. Verify Telegram voice message format (should be OGG)
2. Check voice message file size (max 20MB)
3. Review logs for specific error:
   ```
   Transcription failed (APIError): Invalid audio format
   ```
4. Test with different voice messages

### Memory Issues (Free Tier)

**Symptoms:**
- Service crashes during voice processing
- "Out of memory" errors in logs

**Solutions:**
1. Free tier has 512MB RAM limit
2. Large voice files may exceed memory
3. Options:
   - Upgrade to paid Render.com plan ($7/month)
   - Reduce max voice file size in code
   - Implement voice file size warnings

## Cost Considerations

### Groq API (Free Tier)

**Included:**
- Whisper transcription: 450 requests/minute, unlimited per day
- Llama translation: 30 requests/minute (free tier)

**Estimated Usage:**
- Average message: 1 translation request
- Average voice: 1 transcription + 1 translation request
- 1000 messages/day ≈ well within free tier

**Costs if Upgrading:**
- Whisper: Free for now (may change)
- Llama: Check current pricing at [groq.com/pricing](https://groq.com/pricing)

### Render.com

**Free Tier:**
- 750 hours/month of runtime (sufficient for 24/7)
- 512MB RAM
- Services spin down after 15 minutes of inactivity
- Spin-up time: ~30-60 seconds

**Paid Tier ($7/month):**
- Always on (no spin-down)
- 512MB RAM (Starter)
- Faster performance
- Custom domains

**Recommendation:**
- Start with free tier
- Upgrade if:
  - Bot needs to be always responsive
  - Handling high volume (>100 users)
  - Memory issues occur

### Monthly Cost Estimate

**Scenario 1: Personal Use (Free)**
- 10-50 users
- 500 messages/day
- Cost: $0/month

**Scenario 2: Small Community (Free/Paid)**
- 50-200 users
- 2000 messages/day
- Render.com: Free or $7/month (if always-on needed)
- Groq API: Free
- Total: $0-7/month

**Scenario 3: Large Community (Paid)**
- 500+ users
- 10,000+ messages/day
- Render.com: $7+/month
- Groq API: May need paid tier
- Total: $20-50/month (estimate)

## Maintenance

### Regular Tasks

**Weekly:**
- [ ] Check bot responsiveness
- [ ] Review logs for errors
- [ ] Test key features (translation, voice)

**Monthly:**
- [ ] Review Groq API usage
- [ ] Check Render.com service health
- [ ] Update dependencies if needed

**As Needed:**
- [ ] Update bot code for new features
- [ ] Rotate API keys if compromised
- [ ] Scale up resources if needed

### Updating the Bot

**For Code Changes:**

1. Make changes locally and test
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update: describe changes"
   git push origin main
   ```
3. Render.com auto-deploys (if enabled)
4. Monitor deployment in Render.com dashboard
5. Verify changes with test messages

**For Environment Variable Changes:**

1. Go to Render.com → Service → Environment
2. Update the variable
3. Click "Save Changes"
4. Service will automatically redeploy

**For Dependency Updates:**

1. Update `pyproject.toml` locally
2. Regenerate `requirements.txt`:
   ```bash
   uv pip compile pyproject.toml -o requirements.txt
   ```
3. Test locally
4. Commit and push
5. Render.com will use new requirements

### Backup and Rollback

**Rollback to Previous Version:**
1. On Render.com, go to "Events" tab
2. Find previous successful deployment
3. Click "Rollback" next to that event
4. Service will redeploy previous version

**Backup User Data:**
- Current implementation stores preferences in memory (lost on restart)
- For persistent storage, consider adding database in future phases
- Export logs periodically for analytics

### Monitoring Best Practices

1. **Set up alerts:** Configure Render.com to email on service failures
2. **Regular health checks:** Test bot daily with `/start` command
3. **Log review:** Scan logs weekly for patterns or issues
4. **Usage tracking:** Monitor Groq API dashboard for usage trends
5. **User feedback:** Encourage users to report issues

---

## Support Resources

- **Render.com Docs:** [https://render.com/docs](https://render.com/docs)
- **Groq API Docs:** [https://console.groq.com/docs](https://console.groq.com/docs)
- **Telegram Bot API:** [https://core.telegram.org/bots/api](https://core.telegram.org/bots/api)
- **python-telegram-bot:** [https://docs.python-telegram-bot.org/](https://docs.python-telegram-bot.org/)

---

**Deployment Complete!** Your bot is now running in production and ready to serve users.
