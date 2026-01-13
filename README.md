# Telegram Translation Bot

A production-ready Python Telegram bot for translating text and transcribing voice messages between languages using Groq AI. Features automatic retry logic, rate limiting, timeout configuration, and graceful shutdown.

## Current Status: Phase 4 Complete - Production Ready

All 4 phases are complete! The bot is now production-ready with comprehensive deployment documentation and hardened for real-world use on Render.com or similar platforms.

## Features

### Production Hardening (Phase 4)

- **Automatic Retry**: Exponential backoff for transient API failures (1s, 2s, 4s delays)
- **Timeout Protection**: Configurable timeouts (30s translation, 60s transcription, 30s downloads)
- **Rate Limit Handling**: Detects and gracefully handles Groq API rate limits
- **Graceful Shutdown**: SIGINT/SIGTERM handlers for clean shutdown
- **Production Logging**: Configurable log levels with sensitive data redaction
- **Memory Management**: Efficient temporary file cleanup for voice messages
- **Error Recovery**: User-friendly error messages with retry guidance

### Voice Message Support

- **Voice Transcription**: Powered by Groq Whisper large-v3 model
- **Multi-language Support**: Transcribe voice messages in any language
- **Automatic Translation**: Transcribed text is translated to your preferred language
- **Smart Processing**: Shows typing indicator while processing voice messages
- **Efficient Handling**: Automatic cleanup of temporary files after processing

### Translation Service

- **Real-time Translation**: Powered by Groq AI with Llama 3.3 70B model
- **Fast Response**: Translation typically completes in 1-2 seconds
- **High Quality**: Natural, accurate translations across multiple languages
- **Clear Format**: Shows both original text/transcription and translation for easy comparison
- **Robust Error Handling**: Automatic retries with helpful error messages

### Available Commands

- `/start` - Welcome message explaining the bot's purpose and available commands
- `/setlang <language>` - Set your preferred translation language (e.g., `/setlang spanish`)
- `/mylang` - Display your current language preference
- `/help` - Show detailed help for all commands

### Supported Languages

The bot currently supports the following languages for preference storage:

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- Hindi (hi)

Use `/setlang help` in the bot to see the complete list.

### Current Functionality

- **Real-time Translation**: Text messages are automatically translated to your preferred language
- **Voice Transcription**: Voice messages are transcribed using Whisper large-v3 and translated
- **Command Processing**: All commands work and provide helpful responses
- **User Preferences**: Language preferences are stored in memory per user
- **Input Validation**: Invalid language names are caught with helpful error messages
- **API Integration**: Groq API with Llama 3.3 70B for translations and Whisper large-v3 for transcription
- **Logging**: All bot operations, translations, and transcriptions are logged with timestamps and user IDs
- **Error Recovery**: Failed translations/transcriptions return helpful error messages
- **File Management**: Temporary voice files are automatically cleaned up after processing

## Prerequisites

- **Python**: Version 3.11 or newer
- **uv**: Fast Python package manager ([installation guide](https://github.com/astral-sh/uv))
- **Telegram Bot Token**: Obtained from [@BotFather](https://t.me/botfather) on Telegram
- **Groq API Key**: Free API key from [Groq Console](https://console.groq.com/)

## Getting Your API Keys

### Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Start a chat and send `/newbot`
3. Follow the prompts to:
   - Choose a name for your bot (e.g., "My Translation Bot")
   - Choose a username (must end in "bot", e.g., "my_translation_bot")
4. BotFather will provide your bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Save this token - you'll need it for setup

### Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in (free account available)
3. Navigate to API Keys section
4. Click "Create API Key"
5. Give it a name (e.g., "Telegram Bot")
6. Copy the generated API key (starts with `gsk_`)
7. Save this key - you'll need it for setup

**Note**: Groq offers a generous free tier with fast API responses, perfect for this bot.

## Local Setup

### 1. Clone or Download the Project

```bash
cd /path/to/telegram-bot
```

### 2. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Install Dependencies

```bash
uv sync
```

This will create a virtual environment and install all required packages:
- `python-telegram-bot` (v20+) - Telegram Bot API wrapper
- `python-dotenv` - Environment variable management
- `groq` (v0.4+) - Groq AI API client for translation

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Create the file
touch .env
```

Add your API keys to the `.env` file:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
```

Replace:
- `your_bot_token_here` with the token from BotFather
- `your_groq_api_key_here` with your Groq API key (starts with `gsk_`)

**Important**: The `.env` file is already in `.gitignore` to prevent accidental key exposure.

### 5. Run the Bot

```bash
uv run python main.py
```

You should see:

```
Bot is running successfully!
Press Ctrl+C to stop.
```

The bot is now active and will respond to commands in Telegram.

## Usage Examples

### Starting the Bot

1. Open Telegram and search for your bot by username
2. Click "Start" or send `/start`
3. The bot will greet you and show available commands

### Setting Your Language Preference

```
/setlang spanish
```

Response:
```
Your preferred language has been set to Spanish (es).

Now send me any text message and I'll translate it to your preferred language!
```

### Checking Your Language

```
/mylang
```

Response:
```
Your current language preference: Spanish (es)

Use /setlang <language> to change it.
```

### Getting Help

```
/help
```

Shows detailed information about all commands.

### Translating Text

Send any text message:
```
Hello world, how are you today?
```

Response (if Spanish is set):
```
Original text:
Hello world, how are you today?

Translation to Spanish:
Hola mundo, ¿cómo estás hoy?
```

The translation is done in real-time using Groq AI with the Llama 3.3 70B model.

### Transcribing Voice Messages

Send a voice message in any language:
```
[Voice message: "Hola, ¿cómo estás?"]
```

Response (if Spanish is set as your language):
```
Transcription:
Hola, ¿cómo estás?

Translation to Spanish:
Hola, ¿cómo estás?
```

If you send an English voice message with Spanish set:
```
[Voice message: "Hello, how are you today?"]
```

Response:
```
Transcription:
Hello, how are you today?

Translation to Spanish:
Hola, ¿cómo estás hoy?
```

If no language preference is set, you'll see the transcription only:
```
Transcription:
Hello, how are you today?

To get translations, set your language with /setlang <language>
```

### Invalid Language Handling

```
/setlang klingon
```

Response:
```
Language 'klingon' is not supported.

Supported languages:
arabic, chinese, english, french, german, hindi, italian, japanese, korean, portuguese, russian, spanish
```

## Project Structure

```
telegram-bot/
├── main.py              # Main bot application
├── pyproject.toml       # uv package configuration
├── README.md            # This file
├── .env                 # Environment variables (create this, not in git)
├── .gitignore           # Git ignore rules
├── .python-version      # Python version specification (3.12)
└── .venv/               # Virtual environment (created by uv)
```

## Development

### Logging

The bot logs all important operations:

- Bot startup and shutdown
- Command usage (with user IDs)
- Language preference changes
- Errors and exceptions

Logs appear in the console with format:
```
2024-01-13 10:30:15,123 - __main__ - INFO - User 123456 (username) started the bot
```

### Code Structure

- **Command Handlers**: Each command has an async handler function
- **User Preferences**: Stored in `user_preferences` dictionary (in-memory)
- **Language Validation**: `validate_language()` function checks input
- **Error Handling**: Global error handler catches and logs exceptions
- **Message Handlers**:
  - Text messages: Processes non-command text messages
  - Voice messages: Transcribes using Whisper, then translates
- **Voice Processing**:
  - Downloads voice files to temporary location
  - Transcribes with Groq Whisper large-v3
  - Automatically cleans up temporary files

### Running in Development

The bot uses polling (not webhooks) for simplicity in local development:

```bash
uv run python main.py
```

Press `Ctrl+C` to stop the bot gracefully.

## Deployment to Render.com

The bot is production-ready and can be deployed to Render.com (or similar platforms) in minutes.

### Quick Deploy

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/telegram-bot.git
   git push -u origin main
   ```

2. **Create Web Service on Render.com:**
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python main.py`
     - **Instance**: Free tier

3. **Set Environment Variables:**
   In Render.com service settings, add:
   ```
   TELEGRAM_BOT_TOKEN = <your_bot_token>
   GROQ_API_KEY = <your_groq_api_key>
   LOG_LEVEL = WARNING
   ```

4. **Deploy:**
   - Click "Create Web Service"
   - Wait for build to complete (2-5 minutes)
   - Bot is live!

### Production Configuration

The bot includes production-ready features:

- **Automatic Retries**: API failures are automatically retried with exponential backoff
- **Timeout Protection**: Long-running operations timeout after configured limits
- **Rate Limit Handling**: Groq API rate limits are detected and handled gracefully
- **Graceful Shutdown**: Clean shutdown on SIGINT/SIGTERM signals
- **Production Logging**: `LOG_LEVEL=WARNING` redacts sensitive data and reduces verbosity

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Your Telegram bot token from @BotFather |
| `GROQ_API_KEY` | Yes | - | Your Groq API key from console.groq.com |
| `LOG_LEVEL` | No | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL |

**Production Recommendation:** Set `LOG_LEVEL=WARNING` to reduce log verbosity and protect user privacy.

### Monitoring

**View Logs on Render.com:**
1. Go to your service dashboard
2. Click "Logs" tab
3. Monitor for errors or warnings

**Key Log Messages:**
- `Bot is running in production mode` - Startup successful
- `User 123456 sent text message` - Normal activity
- `Rate limit hit` - Groq API rate limit reached
- `Translation timeout` - Translation took too long

### Cost Estimate

**Render.com Free Tier:**
- 750 hours/month runtime (24/7 coverage)
- 512MB RAM
- Services spin down after 15 min inactivity
- **Cost:** Free

**Groq API Free Tier:**
- Whisper: 450 requests/minute (unlimited daily)
- Llama: 30 requests/minute
- **Cost:** Free for low-medium usage

**Estimated Monthly Cost:**
- Personal use (10-50 users): $0/month
- Small community (50-200 users): $0-7/month (upgrade Render for always-on)
- Large community (500+ users): $20-50/month (paid tiers)

### Complete Deployment Guide

For detailed step-by-step instructions, troubleshooting, and maintenance procedures, see:

**[DEPLOYMENT.md](./DEPLOYMENT.md)** - Complete deployment guide including:
- Pre-deployment checklist
- Step-by-step Render.com setup
- Post-deployment verification
- Monitoring and logging
- Troubleshooting common issues
- Cost breakdown and estimates
- Maintenance procedures

## Troubleshooting

### "TELEGRAM_BOT_TOKEN environment variable is not set"

- Ensure you created the `.env` file in the project root
- Verify the token is on a line like: `TELEGRAM_BOT_TOKEN=123456789:ABC...`
- Make sure there are no spaces around the `=` sign
- The `.env` file should be in the same directory as `main.py`

### "GROQ_API_KEY environment variable is not set"

- Add `GROQ_API_KEY=gsk_...` to your `.env` file
- Get your free API key from [Groq Console](https://console.groq.com/)
- Make sure the key starts with `gsk_`
- Verify there are no spaces around the `=` sign

### Bot doesn't respond to commands

- Check that the bot is running (you should see "Bot is running successfully!")
- Verify you're messaging the correct bot in Telegram
- Try `/start` first to wake up the bot
- Check the console logs for error messages

### Translation fails or returns errors

- Verify your `GROQ_API_KEY` is valid and active
- Check your Groq API usage limits (free tier has limits)
- Ensure you have internet connectivity
- Look at console logs for specific error messages
- Try setting your language preference again with `/setlang`

### "Package not found" errors

- Run `uv sync` to install all dependencies
- Ensure you're using Python 3.11 or newer: `python --version`
- Try removing `.venv/` and running `uv sync` again

## Roadmap

### Phase 1: Foundation (Complete)
- [x] Basic bot structure with uv
- [x] Command handlers (/start, /setlang, /mylang, /help)
- [x] User preference storage (in-memory)
- [x] Language validation
- [x] Logging and error handling
- [x] Message echo functionality

### Phase 2: Translation (Complete)
- [x] Groq API integration for text translation
- [x] Real-time translation functionality
- [x] Support for 12 languages
- [x] Error handling and graceful degradation
- [x] Clear response formatting with original and translated text

### Phase 3: Voice Support (Complete)
- [x] Voice message handling with Telegram API
- [x] Speech-to-text using Groq Whisper large-v3
- [x] Automatic translation of transcribed text
- [x] Temporary file management and cleanup
- [x] Error handling for audio-specific issues
- [x] Typing indicators during processing
- [x] Support for users without language preference

### Phase 4: Production Deployment (Complete)
- [x] Production-ready configuration with retry logic
- [x] Exponential backoff for transient errors
- [x] Timeout configuration for all operations
- [x] Rate limiting detection and handling
- [x] Graceful shutdown (SIGINT/SIGTERM handlers)
- [x] Production logging with sensitive data redaction
- [x] requirements.txt generation for Render.com
- [x] render.yaml deployment configuration
- [x] .env.example template for environment variables
- [x] Complete deployment guide (DEPLOYMENT.md)
- [x] README with quick deploy instructions
- [x] Troubleshooting documentation
- [x] Cost estimation and monitoring guide

## Technical Details

- **Python Version**: 3.11+
- **Package Manager**: uv (development), pip (production)
- **Telegram Library**: python-telegram-bot v22.5 (async/await)
- **Translation API**: Groq AI with Llama 3.3 70B Versatile model
- **Transcription API**: Groq Whisper large-v3 model
- **Environment Management**: python-dotenv
- **Architecture**: Event-driven with async handlers
- **Error Handling**:
  - Automatic retry with exponential backoff (1s, 2s, 4s)
  - Max 3 retry attempts for transient errors
  - Rate limit detection and user notification
- **Timeouts**:
  - Text translation: 30 seconds
  - Voice transcription: 60 seconds
  - File download: 30 seconds
- **Logging**:
  - Production level: WARNING (configurable via LOG_LEVEL)
  - Sensitive data redacted (no user messages or API keys logged)
  - Structured format with function names
- **Response Time**:
  - Text translation: 1-2 seconds
  - Voice transcription + translation: 3-10 seconds (depends on audio length)
- **File Handling**: Temporary files in system temp directory, auto-cleanup
- **Supported Audio Formats**: OGG (Telegram voice format), may support MP3, M4A
- **Deployment**: Ready for Render.com, Heroku, Railway, or any Python hosting platform

## License

This project is for educational and personal use.

## Contributing

This is a personal project built in phases. Feel free to fork and adapt for your own use.

## Support

For issues with:
- **Telegram Bot API**: See [python-telegram-bot documentation](https://docs.python-telegram-bot.org/)
- **uv package manager**: See [uv documentation](https://github.com/astral-sh/uv)
- **Getting a bot token**: Message [@BotFather](https://t.me/botfather) on Telegram

---

**All Phases Complete!** The Telegram Translation Bot is production-ready and deployable. See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete deployment instructions.
