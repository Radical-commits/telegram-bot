<objective>
Add voice message support to the Telegram bot using Groq's Whisper large-v3 model for speech-to-text transcription, followed by translation using the existing translation pipeline from Phase 2.

This phase enables users to send voice messages in any language and receive both transcription and translation.
</objective>

<context>
- Building on Phase 2: Working bot with text translation via Groq API
- Adding: Voice message handling with Whisper large-v3 transcription
- Existing files to modify: main.py, README.md
- Using same GROQ_API_KEY for both Whisper and Llama models
- This is Phase 3 of 4
</context>

<requirements>
**Voice Message Handling:**
1. Detect incoming voice messages from Telegram
2. Download voice file to temporary location (or memory)
3. Transcribe using Groq Whisper large-v3 model
4. Translate transcription using existing translation function
5. Send response with both transcription and translation
6. Clean up temporary files after processing

**Whisper Integration:**
- Model: whisper-large-v3 via Groq API
- Input: Voice file (OGG format from Telegram)
- Output: Transcribed text
- Handle audio format conversion if needed
- Error handling: Unsupported formats, empty audio, API failures

**Response Format:**
- Clear distinction between transcription and translation
- Example format:
  ```
  🎤 Transcription (detected: English):
  "Hello, how are you today?"

  🌐 Translation (Spanish):
  "Hola, ¿cómo estás hoy?"
  ```

**File Handling:**
- Download voice files efficiently (stream if possible)
- Store in temporary location: `/tmp/` or memory buffer
- Delete files immediately after processing
- Handle file size limits (Telegram max: 20MB)
- Verify file before processing

**Enhanced User Experience:**
- Show "typing" indicator while processing
- Inform users if processing takes time (large files)
- Handle users without language preference (show transcription only)
- Support multiple voice message formats (OGG, MP3, M4A if possible)
</requirements>

<implementation>
**Files to Modify:**

1. **main.py:**
   - Add voice message handler using MessageHandler with filters.VOICE
   - Create `async def handle_voice_message(update, context)` function
   - Create `async def transcribe_audio(file_path: str) -> str` function
   - Download voice file: `file = await update.message.voice.get_file()`
   - Call Whisper API for transcription
   - Reuse existing `translate_text()` function from Phase 2
   - Format and send combined response
   - Add file cleanup logic
   - Enhanced error handling for audio-specific errors

2. **pyproject.toml:**
   - Add dependencies if needed: aiofiles (for async file operations)
   - May need: pydub or ffmpeg-python if audio conversion required

3. **README.md:**
   - Update features: "✅ Voice message transcription and translation"
   - Add usage examples for voice messages
   - Note supported audio formats
   - Update roadmap: "Phase 3 complete. Deployment setup in Phase 4"

**Voice Message Processing Flow:**
```
1. Receive voice message
2. Send "typing" indicator
3. Download voice file → /tmp/voice_{message_id}.ogg
4. Call Groq Whisper API for transcription
5. Call existing translate_text() for translation
6. Format response with transcription + translation
7. Send response to user
8. Delete temporary file
9. Log completion
```

**Whisper API Implementation:**
- Use Groq SDK's audio transcription endpoint
- Endpoint: `client.audio.transcriptions.create()`
- Model parameter: "whisper-large-v3"
- File parameter: Open file in binary mode
- Response: Transcribed text

**Error Scenarios to Handle:**
- Voice file too short/empty (< 1 second)
- Unsupported audio format
- Whisper API failure/timeout
- Download failure
- File I/O errors
- Disk space issues

**What to Avoid:**
- Don't store voice files permanently - delete immediately after processing
- Don't process extremely long audio (set reasonable limit: 5-10 minutes)
- Don't block during file download - use async operations
- Don't forget file cleanup (use try/finally)
- Don't deploy yet - that's Phase 4
</implementation>

<output>
Modify these files:

1. `./main.py` - Add/update:
   - Import for voice message handling
   - `handle_voice_message()` async function
   - `transcribe_audio()` async function
   - Voice file download logic
   - Groq Whisper API integration
   - Combined transcription + translation response formatting
   - File cleanup with try/finally
   - Enhanced logging for voice processing
   - Register voice handler with Application

2. `./pyproject.toml` - Add if needed:
   - aiofiles (for async file operations)
   - Any audio processing libraries if required

3. `./README.md` - Update:
   - Features section: Add voice message support
   - Usage section: Add voice message examples
   - Technical details: Note Whisper model used
   - Roadmap: Mark Phase 3 complete

4. Optionally create `./utils.py` if voice handling is complex:
   - File download helper functions
   - Audio validation functions
   - Cleanup utilities
</output>

<verification>
Before declaring complete, verify:

1. **Voice Message Functionality:**
   - Bot receives and processes voice messages
   - Transcription is accurate (test multiple languages)
   - Translation works on transcribed text
   - Response clearly shows both transcription and translation
   - Users without language preference see transcription only

2. **File Handling:**
   - Voice files are downloaded successfully
   - Files are deleted after processing
   - No leftover files in /tmp/ directory
   - Large files are handled appropriately
   - File I/O errors are caught

3. **API Integration:**
   - Whisper API calls succeed
   - Transcription quality is good
   - API errors are handled gracefully
   - Timeouts don't crash the bot

4. **Performance:**
   - Processing completes in reasonable time (< 30 seconds for short messages)
   - No blocking operations
   - Async operations used throughout
   - "Typing" indicator provides user feedback

5. **Error Handling:**
   - Empty/invalid audio is detected
   - API failures show user-friendly messages
   - File cleanup happens even on error (finally block)
   - All errors are logged with context

6. **Testing:**
   - Test voice messages in different languages (English, Spanish, Japanese)
   - Test very short audio (< 1 second)
   - Test longer audio (2-3 minutes)
   - Test with no language preference set
   - Verify all Phase 1 and Phase 2 features still work
   - Check /tmp/ directory for file cleanup

7. **Code Quality:**
   - No blocking file operations
   - Clean error handling
   - Comprehensive logging
   - Code is well-structured and commented
</verification>

<success_criteria>
Phase 3 is complete when:
- Voice messages are transcribed using Groq Whisper large-v3
- Transcriptions are accurate across multiple languages
- Transcribed text is translated to user's preferred language
- Responses clearly show both transcription and translation
- Temporary files are reliably cleaned up
- All error scenarios are handled gracefully
- All Phase 1 and Phase 2 functionality remains intact
- README reflects voice message capabilities
- Bot is ready for Phase 4 (production deployment)
</success_criteria>