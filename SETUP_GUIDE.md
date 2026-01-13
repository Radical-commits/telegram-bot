# Quick Setup Guide - Phase 2

## Prerequisites

1. Python 3.11 or newer
2. uv package manager installed
3. Telegram Bot Token from @BotFather
4. **NEW**: Groq API Key from console.groq.com

## Setup Steps

### 1. Get Your Groq API Key

1. Visit https://console.groq.com/
2. Sign up or log in (free tier available)
3. Go to API Keys section
4. Create new API key
5. Copy the key (starts with `gsk_`)

### 2. Install Dependencies

```bash
cd /path/to/telegram-bot
uv sync
```

This will install:
- python-telegram-bot
- python-dotenv
- groq (NEW in Phase 2)

### 3. Configure Environment Variables

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```
TELEGRAM_BOT_TOKEN=your_telegram_token_here
GROQ_API_KEY=gsk_your_groq_key_here
```

### 4. Run the Bot

```bash
uv run python main.py
```

You should see:
```
2026-01-13 13:00:00,000 - __main__ - INFO - Groq client initialized successfully
2026-01-13 13:00:00,000 - __main__ - INFO - Starting Telegram Translation Bot (Phase 2)...

Bot is running successfully!
Press Ctrl+C to stop.
```

## Testing the Bot

### 1. Start the Bot

In Telegram, find your bot and send:
```
/start
```

### 2. Set Your Language

```
/setlang spanish
```

Bot responds:
```
Your preferred language has been set to Spanish (es).
Now send me any text message and I'll translate it to your preferred language!
```

### 3. Test Translation

Send any text:
```
Hello, how are you?
```

Bot responds:
```
Original text:
Hello, how are you?

Translation to Spanish:
Hola, ¿cómo estás?
```

## Common Issues

### "GROQ_API_KEY environment variable is not set"

- Make sure you created `.env` file
- Check the key starts with `gsk_`
- No spaces around `=` in .env

### Translation Fails

- Verify your Groq API key is active
- Check you're within free tier limits
- Ensure internet connectivity
- Check console logs for details

### Bot Doesn't Respond

- Verify bot is running (check console)
- Try `/start` command first
- Check your Telegram bot token is correct

## Supported Languages

- English, Spanish, French, German
- Italian, Portuguese, Russian
- Chinese, Japanese, Korean
- Arabic, Hindi

Use `/setlang help` to see the full list in the bot.

## What's New in Phase 2

- Real-time translation with Groq AI
- Llama 3.3 70B Versatile model
- Fast responses (1-2 seconds)
- Clear formatting (original + translation)
- Graceful error handling
- User-friendly error messages

## Next: Phase 3

Voice message support coming soon!
