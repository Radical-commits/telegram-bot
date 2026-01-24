# Testing Guide: Trivia Game with OpenTDB Integration

## Quick Start

To test the revamped trivia game, follow these steps:

### 1. Start the Bot

```bash
cd /path/to/telegram-bot
python3 main.py
```

### 2. Basic Testing Flow

#### Test 1: Category Selection
1. Open Telegram and find your bot
2. Send: `/trivia`
3. **Expected**: Inline keyboard with 24+ category buttons
4. **Verify**:
   - "All Categories" appears at top
   - Categories are organized in 2-column grid
   - Category names are readable (long names truncated with "...")

#### Test 2: Start Game with All Categories
1. Click "All Categories" button
2. **Expected**: Loading message, then welcome message
3. **Expected**: First question appears with answer buttons
4. **Verify**:
   - Loading message shows category and language
   - Welcome message confirms game started
   - First question displays correctly

#### Test 3: Boolean Question
1. Wait for a True/False question
2. **Expected**: Two buttons: "✓ Правда" and "✗ Ложь"
3. Click one of the buttons
4. **Expected**:
   - Feedback message (✅ Правильно! or ❌ Неправильно!)
   - Score shown (e.g., "Счет: 1/1")
   - "Следующий вопрос ➡️" button appears
5. **Verify**:
   - Correct answer detection works
   - Score increments for correct answers
   - Score stays same for incorrect answers

#### Test 4: Multiple Choice Question
1. Wait for a question with 4 options (A, B, C, D)
2. **Expected**: Four answer buttons in 2x2 grid
3. **Expected**: Options also shown in message text
4. Click one of the buttons
5. **Expected**: Feedback with correct answer shown if wrong
6. **Verify**:
   - All 4 options are visible and readable
   - Buttons match options in text
   - Correct answer detection works
   - Answers appear randomized (not always in same order)

#### Test 5: Translation (Russian)
1. Ensure your language is set to Russian: `/setlang russian`
2. Start new game: `/trivia`
3. Select any category
4. **Expected**: Questions in Russian
5. **Expected**: Answer options in Russian
6. **Verify**:
   - Questions are properly translated
   - Answers are properly translated
   - UI labels remain in Russian
   - No untranslated English text

#### Test 6: HTML Entity Decoding
1. Play several questions
2. **Look for**: Questions with quotes, apostrophes, special characters
3. **Verify**:
   - No `&quot;` or `&#039;` visible
   - Quotes display as `"` or `'`
   - Special characters display correctly (é, ñ, etc.)
   - Ampersands display as `&`, not `&amp;`

#### Test 7: Complete Game Flow
1. Start new game
2. Answer all 10 questions
3. **Expected**: After question 10, "Показать результаты 🏆" button
4. Click the button
5. **Expected**: Final score message with:
   - Score (X out of 10)
   - Percentage
   - Encouraging message based on score
   - Prompt to play again
6. **Verify**:
   - Score is accurate
   - Percentage calculated correctly
   - Encouraging message matches score range:
     - 100%: "Идеальный результат!"
     - 80-99%: "Отличная работа!"
     - 60-79%: "Хорошая работа!"
     - 40-59%: "Неплохо!"
     - 0-39%: "Хорошая попытка!"

#### Test 8: Category-Specific Questions
1. Start new game: `/trivia`
2. Select specific category (e.g., "Geography")
3. **Expected**: Questions related to geography
4. Answer all 10 questions
5. **Verify**: Most/all questions are geography-related

#### Test 9: Error Handling - Rate Limit
1. Start multiple games quickly (< 5 seconds apart)
2. **Expected**: May see rate limit error
3. **Expected**: Clear error message in Russian
4. Wait 5 seconds and try again
5. **Expected**: Works normally

#### Test 10: Error Handling - Empty Category
1. Try different categories
2. If any return error (unlikely), **verify**:
   - Clear error message shown
   - User can try different category
   - Bot doesn't crash

## Detailed Testing Scenarios

### Scenario 1: Mixed Question Types
**Goal**: Verify both boolean and multiple choice work in same game

1. Start game with "All Categories"
2. Play through all 10 questions
3. **Count**: How many boolean vs multiple choice
4. **Expected**: Mix of both types
5. **Verify**: Both types display and work correctly

### Scenario 2: Answer Randomization
**Goal**: Verify multiple choice answers are randomized

1. Start game with specific category (e.g., "Science: Computers")
2. Note position of correct answer for multiple choice questions
3. Restart game with same category
4. **Expected**: Correct answers in different positions
5. **Verify**: Not all correct answers are in position A or same position

### Scenario 3: Language Switching
**Goal**: Verify translation works for different languages

1. Set language to English: `/setlang english`
2. Start game: `/trivia`
3. **Verify**: Questions in English
4. Finish game
5. Set language to Spanish: `/setlang spanish`
6. Start game: `/trivia`
7. **Verify**: Questions in Spanish
8. **Verify**: Same categories available

### Scenario 4: Multiple Users
**Goal**: Verify independent game states

1. User A starts game with History category
2. User B starts game with Sports category
3. Both play simultaneously
4. **Verify**:
   - User A gets history questions
   - User B gets sports questions
   - Scores tracked independently
   - No interference between games

## API Testing

### Test OpenTDB API Directly

```bash
# Test category list
curl "https://opentdb.com/api_category.php" | jq .

# Test fetching questions
curl "https://opentdb.com/api.php?amount=5&category=9" | jq .

# Test boolean questions
curl "https://opentdb.com/api.php?amount=5&type=boolean" | jq .

# Test multiple choice
curl "https://opentdb.com/api.php?amount=5&type=multiple" | jq .
```

### Expected API Responses

All requests should return:
```json
{
  "response_code": 0,
  "results": [...]
}
```

Response code meanings:
- `0`: Success
- `1`: No results
- `2`: Invalid parameter
- `5`: Rate limited

## Common Issues and Solutions

### Issue 1: Questions Not Translated
**Symptom**: Questions appear in English despite language setting

**Check**:
1. Is user's language set? Run `/mylang`
2. Is Groq API key valid?
3. Check bot logs for translation errors

**Solution**:
- Set language: `/setlang russian`
- Check `.env` file for `GROQ_API_KEY`
- If translation fails, bot shows English (by design)

### Issue 2: HTML Entities Visible
**Symptom**: Seeing `&quot;` or `&#039;` in questions

**Check**:
1. Is `import html` present in main.py?
2. Is `html.unescape()` called on question text?

**Solution**:
- Verify line 10 has `import html`
- Verify `fetch_opentdb_questions()` calls `html.unescape()`

### Issue 3: Wrong Answer Marked Correct
**Symptom**: Incorrect answer shows as correct

**Check**:
1. For multiple choice: Is answer shuffling working?
2. Is correct index tracked after shuffle?

**Debug**:
- Add logging in `fetch_opentdb_questions()` to show answer indices
- Check `trivia_button_callback()` answer comparison logic

### Issue 4: Category Selection Doesn't Work
**Symptom**: Clicking category does nothing or shows error

**Check**:
1. Are callback handlers registered?
2. Is `trivia_button_callback()` parsing category correctly?

**Debug**:
- Check bot logs for callback data received
- Verify callback data format: `trivia_category_{id}`

### Issue 5: Rate Limited
**Symptom**: Error "Rate limited. Please wait..."

**Solution**:
- Wait 5-10 seconds between game starts
- This is OpenTDB API limitation
- Working as designed

## Performance Testing

### Load Test: Multiple Users
1. Have 5+ users start games simultaneously
2. **Monitor**: Bot logs for errors
3. **Verify**: All users get responses
4. **Expected**: No crashes or hangs

### Stress Test: Rapid Games
1. Single user starts games rapidly (every 10 seconds)
2. Complete 5+ games in a row
3. **Verify**:
   - No memory leaks
   - Responses remain fast
   - No degradation over time

## Checklist

Use this checklist for comprehensive testing:

### Basic Functionality
- [ ] /trivia shows category selection
- [ ] Category selection starts game
- [ ] Boolean questions display correctly
- [ ] Multiple choice questions display correctly
- [ ] Answers are in correct language
- [ ] HTML entities decoded properly
- [ ] Score tracking accurate
- [ ] Game completion works

### Question Types
- [ ] True/False questions work
- [ ] Multiple choice questions work
- [ ] Mixed games have both types
- [ ] Answer randomization works

### Categories
- [ ] All 24+ categories display
- [ ] "All Categories" option works
- [ ] Category-specific questions are relevant
- [ ] Long category names truncated properly

### Translation
- [ ] Russian translation works
- [ ] English questions work (no translation)
- [ ] Other languages work (if supported)
- [ ] Translation failure handled gracefully

### Error Handling
- [ ] Rate limiting shows clear error
- [ ] Empty results show clear error
- [ ] Network errors handled
- [ ] Game state preserved correctly

### User Experience
- [ ] Buttons responsive
- [ ] Messages clear and informative
- [ ] Score display accurate
- [ ] Encouraging messages appropriate
- [ ] Can restart game after completion

### Edge Cases
- [ ] Playing multiple games in succession
- [ ] Switching categories between games
- [ ] Changing language mid-session
- [ ] Multiple users playing simultaneously

## Regression Testing

After any future changes, re-test:

1. **Translation Feature**: Ensure regular translation still works
2. **Voice Messages**: Ensure voice transcription unaffected
3. **Language Selection**: Ensure /setlang still works
4. **Help Command**: Ensure /help shows updated info
5. **Other Commands**: Ensure /start, /mylang work

## Reporting Issues

If you find bugs, report with:

1. **What happened**: Describe the issue
2. **Expected behavior**: What should have happened
3. **Steps to reproduce**: How to recreate the issue
4. **Screenshots**: If applicable
5. **Bot logs**: Error messages from console
6. **Environment**: Python version, OS, etc.

## Success Criteria

The implementation is successful if:

- ✅ All categories display and work
- ✅ Both question types display correctly
- ✅ Translation works for all supported languages
- ✅ HTML entities decode properly
- ✅ Answer randomization works
- ✅ Score tracking accurate
- ✅ Complete game flow functional
- ✅ Error handling graceful
- ✅ No crashes or hangs
- ✅ User experience smooth

---

**Last Updated**: 2026-01-24
**Version**: 1.0
**Status**: Ready for Testing
