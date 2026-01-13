<objective>
Build the foundational Telegram bot in Python with basic command structure, logging, and project setup using uv. This phase establishes the bot skeleton that will be extended with translation features in later phases.

This creates a working bot that responds to commands and provides the foundation for adding translation capabilities.
</objective>

<context>
- Project type: Python Telegram bot using python-telegram-bot library (v20+ async)
- Package manager: Use `uv` for dependency management
- Working directory: Current directory is the project root
- This is Phase 1 of 4 - focusing on bot foundation
</context>

<requirements>
**Bot Commands:**
1. `/start` - Welcome message explaining the bot's purpose (translation bot) and available commands
2. `/setlang <language>` - Set preferred translation language (store in memory, validate input)
3. `/mylang` - Display current language preference (or "not set" message)
4. `/help` - Show all available commands with descriptions

**User Preference Storage:**
- In-memory dictionary: `{user_id: language_code}`
- Handle new users (no preference set)
- Validate language input (provide list of common languages)
- Provide clear feedback when language is set/changed

**Technical Setup:**
1. Project structure using uv
2. Environment variable loading (TELEGRAM_BOT_TOKEN)
3. Comprehensive logging configuration (INFO level, timestamps, user IDs)
4. Error handling for bot initialization and command errors
5. Async/await pattern throughout

**Message Handling:**
- For now, echo text messages back with a note: "Translation coming in Phase 2"
- This confirms the bot is receiving messages correctly

**Documentation:**
- README with project overview, local setup using uv, environment variables
- Clear instructions for obtaining Telegram bot token
- Usage examples for all commands
</requirements>

<implementation>
**Project Structure:**
```
./main.py - Main bot application
./pyproject.toml - uv package configuration
./README.md - Setup and usage documentation
./.gitignore - Python-specific ignores
./.python-version - Python version file
```

**Key Implementation Details:**

1. **Dependencies (pyproject.toml):**
   - python-telegram-bot (v20+)
   - python-dotenv
   - Specify Python version (3.11 or newer recommended)

2. **Logging Setup:**
   - Configure at module level
   - Format: timestamp, level, message
   - Log bot start, command usage, errors
   - Include user_id in relevant logs

3. **Command Handlers:**
   - Use CommandHandler for each command
   - Async functions with proper await
   - Send helpful responses to users
   - Handle invalid /setlang input gracefully

4. **Language Validation:**
   - Support common languages: english, spanish, french, german, italian, portuguese, russian, chinese, japanese, korean, arabic, hindi
   - Case-insensitive matching
   - Provide suggestions if invalid language entered

5. **Error Handling:**
   - Try/except around bot initialization
   - Handle invalid tokens gracefully
   - Log all errors with context

**What to Avoid:**
- Don't implement translation yet - that's Phase 2
- Don't add voice handling - that's Phase 3
- Don't create requirements.txt yet - that's Phase 4
- Don't use synchronous APIs - python-telegram-bot v20+ is async-first
</implementation>

<output>
Create the following files:

1. `./main.py` - Bot application with:
   - Environment variable loading
   - Logging configuration
   - Bot initialization
   - Command handlers (/start, /setlang, /mylang, /help)
   - Message handler (echo for now)
   - User preference dictionary
   - Language validation function
   - Main function with bot.run_polling()

2. `./pyproject.toml` - uv configuration with:
   - Project name: "telegram-translation-bot"
   - Dependencies listed above
   - Python version requirement

3. `./README.md` - Documentation with:
   - Project description (translation bot, phase 1 complete)
   - Features (list current commands)
   - Prerequisites (Python, uv, Telegram bot token)
   - Local setup instructions
   - Environment variable setup (TELEGRAM_BOT_TOKEN)
   - How to get a Telegram bot token from @BotFather
   - Usage examples for each command
   - Roadmap note: "Translation coming in Phase 2"

4. `./.gitignore` - Standard Python ignores:
   - .env
   - __pycache__/
   - *.pyc
   - .venv/
   - .uv/

5. `./.python-version` - Specify Python version (e.g., 3.11)
</output>

<verification>
Before declaring complete, verify:

1. **Bot Functionality:**
   - Bot starts successfully with valid token
   - All 4 commands respond appropriately
   - /setlang validates and stores language preference
   - /mylang correctly shows stored preference
   - Text messages are echoed back with "Phase 2" note

2. **Code Quality:**
   - All functions are async with proper await usage
   - Logging statements at key points
   - Error handling implemented
   - Code is clean and commented

3. **Configuration:**
   - pyproject.toml has correct dependencies
   - .env.example or README shows required env vars
   - .gitignore prevents committing secrets

4. **Documentation:**
   - README clearly explains setup steps
   - Bot token acquisition instructions are clear
   - Command examples are accurate

5. **Testing:**
   - Run: `uv run python main.py`
   - Test each command in Telegram
   - Verify logging output in console
   - Confirm language preferences persist across messages
</verification>

<success_criteria>
Phase 1 is complete when:
- Bot responds to all 4 commands correctly
- Language preferences are stored and retrieved accurately
- Text messages receive the "Phase 2" echo response
- Logging provides clear visibility into bot operations
- README enables a new developer to run the bot locally
- No errors or warnings during normal operation
- Code is ready to add Groq translation in Phase 2
</success_criteria>