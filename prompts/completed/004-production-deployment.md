<objective>
Prepare the Telegram translation bot for production deployment on Render.com. Generate deployment configuration, harden error handling, optimize logging for production, and create comprehensive deployment documentation.

This final phase makes the bot production-ready and deployable.
</objective>

<context>
- Building on Phase 3: Fully functional bot with text and voice translation
- Adding: Production hardening, deployment configuration, requirements.txt
- Target platform: Render.com (free tier compatible)
- This is Phase 4 of 4 - final deployment phase
</context>

<requirements>
**Deployment Configuration:**
1. Generate `requirements.txt` from uv for Render.com compatibility
2. Create Render.com configuration (render.yaml or via UI guidance)
3. Environment variable documentation for Render.com
4. Health check or keep-alive mechanism if needed
5. Graceful shutdown handling

**Production Hardening:**
1. Enhanced error handling with retry logic for API calls
2. Rate limiting consideration (handle Groq API rate limits)
3. Production-ready logging:
   - Structured logging format
   - Log levels appropriate for production (WARNING+)
   - Sensitive data redaction (don't log tokens or API keys)
4. Timeout configuration for long-running operations
5. Memory management for voice file handling

**Monitoring & Debugging:**
1. Comprehensive logging for production debugging
2. Error tracking (consider adding health check endpoint)
3. User activity metrics (optional, privacy-respecting)
4. Clear error messages that help diagnose issues

**Documentation:**
1. Complete deployment guide for Render.com
2. Environment variable reference
3. Troubleshooting section
4. Monitoring and maintenance guide
5. Cost considerations (API usage, Render.com limits)
</requirements>

<implementation>
**Files to Create/Modify:**

1. **requirements.txt (NEW):**
   - Generate from uv: `uv pip compile pyproject.toml -o requirements.txt`
   - Ensure all dependencies are pinned with versions
   - Include platform-specific dependencies if needed

2. **render.yaml (NEW - optional):**
   ```yaml
   services:
     - type: web
       name: telegram-translation-bot
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: python main.py
       envVars:
         - key: TELEGRAM_BOT_TOKEN
           sync: false
         - key: GROQ_API_KEY
           sync: false
   ```

3. **main.py - Production Enhancements:**
   - Add retry logic for API calls (use tenacity or custom implementation)
   - Implement exponential backoff for rate limits
   - Add timeout configuration (e.g., 30s for translation, 60s for voice)
   - Configure production logging (WARNING level, structured format)
   - Redact sensitive data in logs
   - Add graceful shutdown handler
   - Optional: Add keep-alive or health check endpoint

4. **README.md - Complete Deployment Section:**
   - Prerequisites for deployment
   - Step-by-step Render.com deployment guide:
     - Create new Web Service
     - Connect GitHub repository (if applicable)
     - Set environment variables
     - Deploy and monitor
   - Environment variables configuration
   - Monitoring and logs access
   - Troubleshooting common deployment issues
   - Cost estimation (Groq API usage, Render.com free tier limits)
   - Maintenance guide (updating bot, monitoring health)

5. **.env.example (NEW):**
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   GROQ_API_KEY=your_groq_api_key_here
   LOG_LEVEL=INFO
   ```

**Production Best Practices:**

1. **Error Handling & Retry Logic:**
   - Retry transient API failures (network errors, 5xx responses)
   - Exponential backoff: 1s, 2s, 4s delays
   - Max retries: 3 attempts
   - Don't retry 4xx errors (client errors)

2. **Rate Limiting:**
   - Detect Groq API rate limit responses (429 status)
   - Inform user: "Translation service temporarily busy, please try again"
   - Log rate limit events for monitoring

3. **Logging for Production:**
   - Use structured logging (JSON format optional)
   - Log levels: ERROR for failures, INFO for key events, DEBUG off in production
   - Include correlation IDs (message_id or user_id) for tracing
   - Never log API keys, tokens, or user message content (privacy)

4. **Timeout Configuration:**
   - Text translation: 30 second timeout
   - Voice transcription: 60 second timeout
   - File download: 30 second timeout
   - Bot polling: Default timeout

5. **Memory Management:**
   - Limit concurrent voice processing (if many users)
   - Clean up files immediately after processing
   - Monitor memory usage (log warnings if high)

6. **Graceful Shutdown:**
   - Handle SIGINT and SIGTERM signals
   - Complete in-flight requests before shutdown
   - Log shutdown event

**Render.com Specific Configuration:**

1. **Service Type:** Web Service (not background worker, as bot uses polling)
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `python main.py`
4. **Environment Variables:** Set in Render.com dashboard (not in code)
5. **Health Check:** Optional - bot will auto-reconnect if it crashes
6. **Pricing:** Free tier sufficient for low-medium usage

**What to Avoid:**
- Don't commit .env file or secrets to git
- Don't use DEBUG logging in production (too verbose)
- Don't skip retry logic (makes bot fragile)
- Don't ignore rate limits (will get API blocked)
- Don't over-engineer (keep it simple and maintainable)
</implementation>

<output>
Create/modify these files:

1. **./requirements.txt (NEW)** - Generate with:
   - All dependencies with pinned versions
   - Platform compatibility ensured
   - Comment at top: "# Generated from pyproject.toml for Render.com deployment"

2. **./render.yaml (NEW - optional)** - Render.com config:
   - Service definition
   - Build and start commands
   - Environment variable placeholders

3. **./.env.example (NEW)** - Template for environment variables:
   - All required env vars
   - Placeholder values
   - Comments explaining each variable

4. **./main.py - Production Updates:**
   - Import retry libraries (if using tenacity)
   - Add `@retry` decorators to API calls
   - Implement exponential backoff logic
   - Configure production logging level
   - Add graceful shutdown handler
   - Timeout configurations
   - Rate limit detection and handling

5. **./README.md - Complete Documentation:**
   - Full deployment section with screenshots or detailed steps
   - Environment variable reference table
   - Troubleshooting section:
     - Bot not responding
     - API key errors
     - Rate limiting issues
     - Voice message failures
   - Monitoring guide:
     - Viewing logs on Render.com
     - Common error patterns
   - Cost section:
     - Groq API pricing
     - Render.com free tier limits
     - Estimated monthly costs
   - Maintenance guide:
     - Updating dependencies
     - Redeploying changes
     - Monitoring bot health

6. **./DEPLOYMENT.md (NEW - optional)** - Detailed deployment guide:
   - Pre-deployment checklist
   - Step-by-step Render.com setup
   - Post-deployment verification
   - Rollback procedures
</output>

<verification>
Before declaring complete, verify:

1. **Deployment Readiness:**
   - requirements.txt is generated and complete
   - All environment variables documented
   - Render.com configuration is correct
   - No secrets or keys in code/config files

2. **Production Hardening:**
   - Retry logic implemented for API calls
   - Rate limiting is detected and handled
   - Timeouts configured appropriately
   - Graceful shutdown works correctly
   - Memory management is efficient

3. **Logging:**
   - Production log level set (WARNING or INFO)
   - No sensitive data in logs
   - Logs provide adequate debugging info
   - Structured and parseable log format

4. **Error Handling:**
   - All error paths tested
   - User-facing error messages are clear
   - Critical errors are logged with context
   - Bot doesn't crash on API failures

5. **Documentation:**
   - README deployment section is complete and accurate
   - All environment variables documented
   - Troubleshooting section covers common issues
   - Cost information is provided
   - Maintenance procedures are clear

6. **Testing:**
   - Generate requirements.txt and verify it installs cleanly
   - Test bot locally with production logging level
   - Simulate API failures (invalid key) - verify retry logic
   - Test graceful shutdown (CTRL+C)
   - Verify all Phase 1-3 features still work
   - Test with .env.example (renamed to .env with real values)

7. **Deployment Simulation:**
   - Follow deployment guide step-by-step
   - Verify all steps are accurate
   - Ensure a new developer could deploy using only the README
   - Confirm free tier is sufficient for expected usage

8. **Final Checks:**
   - .gitignore includes all secrets (.env, etc.)
   - No TODO comments or placeholder code
   - Code is clean and production-quality
   - All phases' features are working together seamlessly
</verification>

<success_criteria>
Phase 4 (and entire project) is complete when:
- requirements.txt is generated and ready for Render.com
- Production hardening is implemented (retry, rate limits, timeouts)
- Logging is configured appropriately for production
- README provides complete deployment guide
- All environment variables are documented with .env.example
- Bot can be deployed to Render.com following the documentation
- Troubleshooting section helps resolve common issues
- No secrets are committed to repository
- All Phase 1-3 features work correctly in production configuration
- Bot is production-ready and maintainable

**Final deliverable:** A fully functional, production-ready Telegram translation bot that can be deployed to Render.com with comprehensive documentation.
</success_criteria>