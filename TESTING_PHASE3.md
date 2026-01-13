# Phase 3 Testing Checklist

## Voice Message Functionality

### Basic Voice Transcription
- [ ] Send a short voice message (5-10 seconds) in English
  - Expected: Transcription displayed correctly
  - Expected: Translation to set language (if any)

- [ ] Send a voice message in Spanish
  - Expected: Transcription in Spanish
  - Expected: Translation to set language

- [ ] Send a voice message in Japanese
  - Expected: Transcription in Japanese
  - Expected: Translation to set language

### File Handling
- [ ] Check /tmp/ directory before sending voice message
- [ ] Send voice message and verify file is created temporarily
- [ ] After bot responds, verify temporary file is deleted
- [ ] Send multiple voice messages and verify no leftover files

### Edge Cases
- [ ] Send a very short voice message (< 1 second)
  - Expected: Error message about message being too short

- [ ] Send a voice message without setting language preference
  - Expected: Transcription only, with message to set language

- [ ] Send a longer voice message (2-3 minutes)
  - Expected: Successful transcription and translation
  - Expected: Typing indicator during processing

### Error Handling
- [ ] Temporarily disable internet and send voice message
  - Expected: Connection error message

- [ ] Test with invalid Groq API key
  - Expected: Authentication error message

### User Experience
- [ ] Verify typing indicator appears while processing
- [ ] Verify response format is clear and readable
- [ ] Verify both transcription and translation are shown
- [ ] Verify original language is preserved in transcription

## Integration with Existing Features

### Text Translation (Phase 2)
- [ ] Send text message after voice message
  - Expected: Text translation still works

- [ ] Change language preference with /setlang
  - Expected: Both text and voice use new language

### Commands (Phase 1)
- [ ] /start command
  - Expected: Updated welcome message mentions voice support

- [ ] /help command
  - Expected: Help text includes voice message information

- [ ] /setlang and /mylang commands
  - Expected: Commands work as before

### Multiple Users
- [ ] User A sets Spanish preference, sends voice in English
- [ ] User B sets French preference, sends voice in English
- [ ] Verify each user gets translation in their language

## Performance

- [ ] Voice message processing completes in < 30 seconds
- [ ] No memory leaks after processing multiple messages
- [ ] Temporary files are cleaned up even on errors

## Code Quality

- [ ] All error scenarios have proper logging
- [ ] No blocking operations in async code
- [ ] Temporary file cleanup happens in finally block
- [ ] All Phase 1 and Phase 2 features remain functional

## Documentation

- [ ] README updated with voice message features
- [ ] Usage examples show voice message workflow
- [ ] Technical details mention Whisper model
- [ ] Roadmap shows Phase 3 complete

## Ready for Phase 4

- [ ] All Phase 3 requirements met
- [ ] No critical bugs or issues
- [ ] All existing functionality intact
- [ ] Documentation up to date
