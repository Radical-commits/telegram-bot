<objective>
Build a production-ready Telegram bot in Python that translates text and voice messages to different languages using Groq's API (Llama models for translation, Whisper large-v3 for speech-to-text). The bot should be deployable on Render.com with proper configuration, logging, and user preference management.

This bot will help users communicate across language barriers by providing real-time translation of text messages and transcription/translation of voice messages.
</objective>

<context>
- Project type: Python Telegram bot using python-telegram-bot library
- Package manager: Use `uv` for dependency management
- APIs: Groq API for both translation (Llama models) and speech-to-text (Whisper large-v3)
- Deployment: Render.com (requires proper requirements.txt and configuration)
- State management: In-memory storage for user language preferences
- Working directory: Current directory is the project root
</context>

<requirements>
**Core Functionality:**
1. Text message translation:
   - Command to set target language (e.g., `/setlang spanish`)
   - Automatically translate incoming text messages to user's preferred language
   - Default language preference if none set

2. Voice message support:
   - Download voice message file from Telegram
   - Transcribe using Groq's Whisper large-v3 model
   - Translate transcribed text using Groq's Llama models
   - Send both transcription and translation to user

3. User preference management:
   - Store language preferences in memory (dictionary mapping user_id to language)
   - Persist across bot restarts is not required (in-memory is sufficient)
   - Command to view current language setting (e.g., `/mylang`)

4. Bot commands:
   - `/start` - Welcome message with instructions
   - `/setlang <language>` - Set preferred translation language
   - `/mylang` - Show current language preference
   - `/help` - Display available commands and usage

**Technical Requirements:**
1. Use `uv` for package management (pyproject.toml configuration)
2. Environment variables:
   - `TELEGRAM_BOT_TOKEN` - Telegram bot token
   - `GROQ_API_KEY` - Groq API key
3. Comprehensive logging for debugging (use Python's logging module)
4. Error handling for API failures, network issues, unsupported languages
5. Clean code structure with proper separation of concerns

**Deployment Requirements:**
1. Requirements.txt for Render.com compatibility
2. Render.com configuration (if needed)
3. README.md with:
   - Project description
   - Setup instructions (obtaining API keys, setting environment variables)
   - Local development setup using uv
   - Deployment instructions for Render.com
   - Usage examples
4. .gitignore for Python projects (exclude .env, __pycache__, etc.)
</requirements>

<implementation>
**Project Structure:**
```
./main.py - Main bot application with handlers
./pyproject.toml - uv package configuration
./requirements.txt - Generated from uv for Render.com
./README.md - Comprehensive setup and usage documentation
./.gitignore - Python-specific gitignore
./.python-version - Python version specification (if using uv's Python version management)
```

**Key Implementation Details:**

1. **Groq API Integration:**
   - Use Groq's Python SDK or direct HTTP requests
   - For translation: Use Llama models (e.g., llama-3.3-70b-versatile or similar)
   - For transcription: Use whisper-large-v3 model
   - Include proper error handling and retry logic

2. **Telegram Bot Setup:**
   - Use python-telegram-bot library (v20+ with async/await)
   - Implement handlers for commands and messages
   - Handle both text and voice message types
   - Download voice files to temporary location or memory

3. **Language Preferences:**
   - Use a dictionary: `user_preferences = {user_id: language_code}`
   - Handle language names (e.g., "spanish", "french") and convert to appropriate format
   - Provide clear feedback when language is set or invalid

4. **Logging:**
   - Configure logging at INFO level by default
   - Log all API calls, errors, and user interactions
   - Include timestamps and user IDs for debugging
   - Use structured logging messages

5. **Error Handling:**
   - Gracefully handle API rate limits
   - Inform users of errors with helpful messages
   - Log detailed error information for debugging
   - Handle unsupported voice formats

**What to Avoid and Why:**
- Don't use deprecated synchronous python-telegram-bot APIs - the library is now async-first for better performance
- Don't store API keys in code - always use environment variables to prevent security issues
- Don't skip error handling on API calls - Groq API can fail, and users should receive helpful feedback
- Don't use heavy databases for simple preference storage - in-memory is sufficient for this use case and reduces deployment complexity
- Don't forget to handle voice file cleanup - temporary files can accumulate and cause storage issues
</implementation>

<output>
Create the following files with relative paths:

1. `./main.py` - Main bot application with:
   - Telegram bot initialization
   - Command handlers (/start, /setlang, /mylang, /help)
   - Message handlers (text and voice)
   - Groq API integration functions
   - Logging configuration
   - User preference management

2. `./pyproject.toml` - uv package configuration with:
   - Project metadata
   - Dependencies (python-telegram-bot, groq, python-dotenv, etc.)
   - Python version specification

3. `./requirements.txt` - Generated from uv for Render.com deployment

4. `./README.md` - Comprehensive documentation with:
   - Project overview
   - Features list
   - Prerequisites (API keys)
   - Local setup instructions using uv
   - Environment variable configuration
   - Render.com deployment guide
   - Usage examples with screenshots/command examples
   - Troubleshooting section

5. `./.gitignore` - Python-specific ignores including:
   - .env files
   - __pycache__
   - *.pyc
   - .venv/
   - uv-specific directories

6. `./.python-version` - Python version file (if needed for uv)
</output>

<verification>
Before declaring complete, verify your work:

1. **Code Quality:**
   - All async functions properly use await
   - Error handling implemented for all API calls
   - Logging statements at appropriate levels
   - Code is well-commented for maintainability

2. **Functionality:**
   - All commands (/start, /setlang, /mylang, /help) are implemented
   - Text translation works with user preferences
   - Voice message handling: download → transcribe → translate → respond
   - Language preference storage and retrieval works correctly

3. **Configuration:**
   - Environment variables properly loaded and used
   - pyproject.toml has all required dependencies
   - requirements.txt generated correctly for Render.com

4. **Documentation:**
   - README includes all setup steps
   - Example commands are clear and accurate
   - Render.com deployment instructions are complete
   - Environment variables are documented

5. **Deployment Readiness:**
   - No hardcoded secrets or tokens
   - Application can run on Render.com's platform
   - All dependencies are specified correctly
</verification>

<success_criteria>
The implementation is successful when:
- Bot responds to /start command with welcome message and instructions
- Users can set language preference with /setlang command
- Text messages are automatically translated to user's preferred language
- Voice messages are transcribed and translated correctly
- All errors are logged with sufficient detail for debugging
- README provides clear, step-by-step setup instructions
- Project can be deployed to Render.com following the documentation
- No API keys or secrets are committed to code
</success_criteria>