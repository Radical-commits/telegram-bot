<objective>
Integrate Groq API for text translation using Llama models. Enable automatic translation of user text messages to their preferred language set in Phase 1. This adds the core translation functionality to the bot.

This phase transforms the bot from a command-only skeleton into a working translation service.
</objective>

<context>
- Building on Phase 1: Bot skeleton with commands and language preferences
- Adding: Groq API integration for text-to-text translation
- Existing files to modify: main.py, pyproject.toml, README.md
- New environment variable: GROQ_API_KEY
- This is Phase 2 of 4
</context>

<requirements>
**Groq API Integration:**
1. Use Groq Python SDK or direct API calls
2. Model: Use Llama model suitable for translation (e.g., llama-3.3-70b-versatile)
3. Translate incoming text messages to user's preferred language
4. Handle users with no language preference (prompt them to use /setlang)

**Translation Function:**
- Input: source text, target language
- Output: translated text
- Error handling: API failures, rate limits, network issues
- Logging: Log all translation requests and responses
- Return original text if translation fails (graceful degradation)

**Message Handler Update:**
- Replace echo functionality from Phase 1
- Check if user has language preference set
- If set: translate message and send translation
- If not set: prompt user to use /setlang command
- Show original text and translation clearly (formatted response)

**Enhanced Error Handling:**
- Invalid/missing API key
- API rate limiting (inform user, suggest waiting)
- Unsupported language combinations
- Network timeouts
- Malformed API responses

**User Experience:**
- Fast response times (async API calls)
- Clear indication that text is translated (e.g., "🌐 Translation: ...")
- Helpful error messages in Telegram
- Option to show both original and translated text
</requirements>

<implementation>
**Files to Modify:**

1. **main.py:**
   - Import Groq SDK
   - Add GROQ_API_KEY environment variable loading
   - Create translation function: `async def translate_text(text: str, target_language: str) -> str`
   - Update message handler to call translation function
   - Add error handling for API calls
   - Format translated responses clearly

2. **pyproject.toml:**
   - Add dependency: groq (official Groq Python SDK)

3. **README.md:**
   - Update features section: "✅ Text translation with Groq API"
   - Add GROQ_API_KEY to environment variables section
   - Add instructions for obtaining Groq API key (https://console.groq.com/)
   - Update usage examples with translation examples
   - Update roadmap: "Phase 2 complete. Voice support coming in Phase 3"

**Translation Implementation Details:**

1. **Groq API Setup:**
   - Initialize Groq client with API key
   - Use chat completion endpoint
   - System prompt: "You are a translator. Translate the following text to {target_language}. Only provide the translation, no explanations."
   - User prompt: The text to translate

2. **Response Format:**
   - Original text (if user wants context)
   - Translated text with clear indicator
   - Example: "🌐 *Spanish translation:*\n[translated text]"

3. **Caching/Optimization:**
   - No caching needed for Phase 2 (keep it simple)
   - Each message is translated independently

4. **Language Handling:**
   - Map language names from Phase 1 (e.g., "spanish") to clear language instructions for Groq
   - Support the same languages as Phase 1

**What to Avoid:**
- Don't add voice support yet - that's Phase 3
- Don't optimize for deployment yet - that's Phase 4
- Don't over-engineer with caching or database - keep in-memory preferences
- Don't use deprecated Groq API endpoints
</implementation>

<output>
Modify these files:

1. `./main.py` - Add/update:
   - Groq client initialization
   - `translate_text()` async function
   - Updated message handler with translation logic
   - GROQ_API_KEY environment variable loading
   - Enhanced error handling and logging
   - Formatted translation responses

2. `./pyproject.toml` - Add:
   - groq dependency

3. `./README.md` - Update:
   - Features section (mark translation as complete)
   - Environment variables (add GROQ_API_KEY)
   - Groq API key acquisition instructions
   - Usage examples showing translation in action
   - Updated roadmap/status

4. Optionally create `./config.py` if you want to separate configuration:
   - API configuration
   - Language mappings
   - Response templates
</output>

<verification>
Before declaring complete, verify:

1. **Translation Functionality:**
   - Text messages are translated to user's preferred language
   - Translation is accurate and natural (test with multiple languages)
   - Original text is preserved in response (for context)
   - Users without language preference get helpful prompt

2. **API Integration:**
   - Groq API calls succeed with valid key
   - Invalid API key is caught and logged
   - API errors are handled gracefully
   - Rate limiting is detected and communicated

3. **Code Quality:**
   - Async/await used correctly for API calls
   - All errors are caught and logged
   - No blocking operations
   - Clean separation between bot logic and translation logic

4. **User Experience:**
   - Responses are fast (within 2-3 seconds)
   - Translation responses are clearly formatted
   - Error messages are user-friendly
   - Commands from Phase 1 still work correctly

5. **Testing:**
   - Test with multiple languages (Spanish, French, Japanese, etc.)
   - Test with user who hasn't set language
   - Test with invalid API key (error handling)
   - Test with long messages
   - Verify all Phase 1 commands still work

6. **Documentation:**
   - README shows how to get Groq API key
   - Environment variables section is complete
   - Usage examples demonstrate translation
</verification>

<success_criteria>
Phase 2 is complete when:
- Incoming text messages are automatically translated using Groq API
- Translation quality is good across multiple languages
- Users without language preference receive helpful guidance
- API errors are handled gracefully without crashing the bot
- All Phase 1 functionality remains intact
- README is updated with Groq API setup instructions
- Bot is ready for Phase 3 (voice message support)
</success_criteria>