# Quick Start Guide - Phase 3 Voice Support

## Prerequisites
- Python 3.11+ installed
- uv package manager installed
- Telegram Bot Token (from @BotFather)
- Groq API Key (from console.groq.com)

## Setup (if not already done)

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set up environment variables:**
   Create `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_token
   GROQ_API_KEY=your_groq_api_key
   ```

## Running the Bot

```bash
uv run python main.py
```

You should see:
```
Bot is running successfully with voice support!
Send text or voice messages to translate.
Press Ctrl+C to stop.
```

## Testing Voice Support

### Test 1: Basic Voice Transcription
1. Open your Telegram bot
2. Send `/setlang spanish`
3. Record and send a voice message saying: "Hello, how are you?"
4. Expected response:
   ```
   Transcription:
   Hello, how are you?

   Translation to Spanish:
   Hola, ¿cómo estás?
   ```

### Test 2: Voice Without Language Preference
1. Send `/mylang` to check current language
2. If set, start fresh conversation or clear preference
3. Send a voice message
4. Expected response:
   ```
   Transcription:
   [Your transcribed text]

   To get translations, set your language with /setlang <language>
   ```

### Test 3: Different Languages
1. Set language to English: `/setlang english`
2. Send a voice message in Spanish: "Hola, ¿cómo estás?"
3. Expected response:
   ```
   Transcription:
   Hola, ¿cómo estás?

   Translation to English:
   Hello, how are you?
   ```

### Test 4: File Cleanup
1. Check temp directory before test:
   ```bash
   ls /tmp/ | grep -E "\.ogg$" | wc -l
   ```
2. Send multiple voice messages (3-5)
3. Wait for all responses
4. Check temp directory again - should have same or fewer files
5. Old voice files should be cleaned up

### Test 5: Error Handling
1. Send a very short voice message (< 1 second)
2. Expected: Error about message being too short

## Verifying All Features Work

### Text Translation (Phase 2)
```
/setlang french
[Send text]: Hello world
Expected: Translation to French
```

### Commands (Phase 1)
```
/start     - Should show updated welcome message
/help      - Should mention voice support
/setlang   - Should work as before
/mylang    - Should show current language
```

## Monitoring and Logs

The bot logs all operations. Watch the console for:

**Voice message received:**
```
INFO - User 123456 (username) sent voice message (duration: 5s, size: 50000 bytes)
```

**Download and transcription:**
```
INFO - Downloading voice file for user 123456...
INFO - Voice file downloaded to /tmp/tmpXXXXXX.ogg
INFO - Transcribing audio file: /tmp/tmpXXXXXX.ogg
INFO - Transcription successful: Hello, how are you?...
```

**Translation (if applicable):**
```
INFO - Translating text to Spanish: Hello, how are you?...
INFO - Translation successful: Hola, ¿cómo estás?...
```

**File cleanup:**
```
INFO - Deleted temporary file: /tmp/tmpXXXXXX.ogg
```

## Common Issues

### "Voice message is too short"
- Voice must be at least 1 second long
- Try holding the record button longer

### "Transcription service authentication failed"
- Check your GROQ_API_KEY in .env
- Verify key is valid at console.groq.com
- Ensure key starts with 'gsk_'

### "Transcription service is busy"
- Groq API rate limit reached
- Wait a moment and try again
- Check your Groq usage at console.groq.com

### Temporary files not cleaning up
- Check logs for errors in cleanup
- Verify /tmp/ directory permissions
- May indicate file system issues

### Voice messages not being detected
- Ensure bot is running (check console)
- Verify you're using voice messages (not audio files)
- Check Telegram app is up to date

## Performance Expectations

- **Short voice message (5-10 seconds)**: 4-6 seconds to process
- **Medium voice message (30-60 seconds)**: 8-12 seconds to process
- **Long voice message (2-3 minutes)**: 15-30 seconds to process

You should see typing indicator during processing.

## Next Steps

After verifying voice support works:

1. ✅ Test with multiple languages
2. ✅ Verify file cleanup is working
3. ✅ Test error scenarios
4. ✅ Verify all Phase 1 and Phase 2 features still work
5. ✅ Review logs for any warnings or errors

Then proceed to Phase 4: Deployment setup!

## Troubleshooting

### No response from bot
- Check bot is running (console output)
- Verify Telegram bot token is correct
- Check internet connection
- Look for errors in console logs

### Transcription is wrong
- Whisper may struggle with:
  - Very quiet audio
  - Heavy background noise
  - Multiple speakers
  - Strong accents
- Try re-recording in quiet environment

### Translation is wrong
- Check source language was correctly detected
- Try more clear/simple phrasing
- Check language preference is set correctly
- Some phrases may not translate literally

## Support

For issues:
1. Check console logs for error messages
2. Review TESTING_PHASE3.md for comprehensive tests
3. Check README.md for detailed documentation
4. Verify all environment variables are set correctly
