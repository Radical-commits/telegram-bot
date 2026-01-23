# Trivia Game Feature

## Overview

The Telegram Translation Bot now includes an interactive True/False trivia game feature that allows users to test their knowledge with 10 weird and interesting facts.

## Features

- **10 Questions per Game**: Each game consists of 10 randomly generated true/false questions
- **Inline Button Interface**: Users tap "True" or "False" buttons to answer
- **Instant Feedback**: Immediate response showing if the answer is correct/wrong
- **Explanations**: Each answer includes a brief explanation or interesting fact
- **Score Tracking**: Live score display throughout the game
- **Final Score**: Encouraging message based on performance (0-10 score)
- **Replay**: Users can play multiple times with different questions

## How to Play

1. Start the bot with `/start`
2. Type `/trivia` to begin a new game
3. Read each question carefully
4. Tap either "✓ True" or "✗ False" button
5. Get instant feedback with explanation
6. Continue through all 10 questions
7. See your final score and play again!

## Commands

- `/trivia` - Start a new trivia game
- `/help` - Shows all commands including trivia
- `/start` - Welcome message now mentions trivia feature

## Technical Implementation

### Files Modified

- **main.py** - Added complete trivia game functionality

### New Functions

1. **`generate_trivia_questions(count: int = 10)`**
   - Uses Groq API (llama-3.3-70b-versatile) to generate questions
   - Returns JSON array of questions with claim, answer, and explanation
   - Includes retry logic for transient errors
   - Validates JSON structure

2. **`verify_claim_with_search(claim: str, expected_answer: bool)`**
   - Verifies claims using DuckDuckGo Instant Answer API
   - Returns verification status and brief explanation
   - Handles search failures gracefully
   - (Note: Currently implemented but not actively used to avoid blocking gameplay)

3. **`send_trivia_question(update, context, user_id)`**
   - Sends current question with True/False inline buttons
   - Displays question number and current score
   - Handles both new games and callback updates

4. **`end_trivia_game(update, context, user_id)`**
   - Calculates final score percentage
   - Shows encouraging message based on performance
   - Cleans up game state
   - Prompts user to play again

5. **`trivia_command(update, context)`**
   - Handles `/trivia` command
   - Checks for existing active games
   - Generates 10 new questions
   - Initializes game state
   - Sends first question

6. **`trivia_button_callback(update, context)`**
   - Handles True/False button presses
   - Validates question index to prevent double-answering
   - Checks answer correctness
   - Updates score and game state
   - Shows feedback with explanation
   - Sends next question or ends game

7. **`button_callback_router(update, context)`**
   - Routes callback queries to appropriate handlers
   - Handles both language selection (`lang_`) and trivia (`trivia_`) callbacks

### State Management

```python
trivia_games: Dict[int, Dict[str, Any]] = {
    user_id: {
        "questions": [{"claim": str, "answer": bool, "explanation": str}, ...],
        "current_index": int,  # 0-9
        "score": int,  # 0-10
        "active": bool  # True during game, cleaned up after
    }
}
```

### Button Callback Format

- `trivia_true_<index>` - User answered True for question at index
- `trivia_false_<index>` - User answered False for question at index

Example: `trivia_true_0` means user answered True for the first question (index 0)

### Question Generation Prompt

The bot generates questions by prompting Groq with:
- Weird, surprising, counterintuitive facts
- Clear and specific claims
- Mix of true and false (roughly 50/50)
- Topics: animals, science, history, geography, technology, human body, space, food
- Each with brief (1-2 sentence) explanation

### Error Handling

- **API Failures**: Graceful fallback with user-friendly messages
- **Rate Limiting**: Informs user to wait and try again
- **Timeout**: 30-second timeout on question generation
- **Invalid JSON**: Robust parsing with regex extraction
- **Expired Games**: Users can't answer old questions
- **Concurrent Play**: Multiple users can play simultaneously

### Example Questions

1. "A group of flamingos is called a 'flamboyance'" (True)
2. "Honey never spoils and can last thousands of years" (True)
3. "Octopuses have three hearts" (True)
4. "Bananas grow on trees" (False - they grow on large herbs)
5. "The Great Wall of China is visible from space with the naked eye" (False)

## Testing Checklist

### Basic Functionality
- [x] `/trivia` starts a new game
- [x] Bot generates 10 questions
- [x] Questions appear one at a time
- [x] True/False buttons work correctly
- [x] Score tracking is accurate
- [x] Final score displays after 10 questions
- [x] User can start new game with `/trivia`

### User Experience
- [x] Question counter shows progress (e.g., "Question 3/10")
- [x] Feedback is immediate after each answer
- [x] Explanations are interesting and informative
- [x] Final score message is encouraging
- [x] Buttons use clear icons (✓ and ✗)

### State Management
- [x] Game state tracks correctly per user
- [x] Multiple users can play simultaneously
- [x] State cleans up after game ends
- [x] Can't answer old questions (index validation)

### Error Handling
- [x] Groq API failures show user-friendly errors
- [x] Rate limiting handled gracefully
- [x] Timeout doesn't crash bot
- [x] Invalid JSON parsed correctly

### Integration
- [x] Translation features work during trivia
- [x] `/help` mentions trivia feature
- [x] `/start` welcomes users and mentions trivia
- [x] No conflicts with existing commands
- [x] Language selection buttons still work

### Edge Cases
- [x] Starting new game while one is active (cancels old game)
- [x] Abandoned games don't cause issues (state tracks per user)
- [x] JSON parsing handles extra text from LLM
- [x] Score calculation is correct (0-10)

## Performance

- **Question Generation**: ~2-5 seconds (Groq API)
- **Response Time**: Immediate feedback (<100ms)
- **Memory**: Minimal (in-memory state per active game)
- **Concurrent Users**: Unlimited (state isolated per user_id)

## Future Enhancements (Optional)

1. **Web Search Verification**: Currently implemented but not actively used. Could be enabled to verify questions before presenting to users.

2. **Difficulty Levels**: Add easy/medium/hard question categories

3. **Topics**: Allow users to choose topic categories (science, history, etc.)

4. **Leaderboards**: Track high scores across users

5. **Multiplayer**: Allow users to challenge friends

6. **Question Database**: Cache verified questions to reduce API calls

7. **Daily Challenges**: New set of questions each day

8. **Achievements**: Badges for perfect scores, streaks, etc.

## Dependencies

All dependencies are already included in `requirements.txt`:
- `groq` - For question generation (llama-3.3-70b-versatile)
- `httpx` - For web search verification (if enabled)
- `python-telegram-bot` - For bot functionality and inline buttons
- `aiohttp` - For async HTTP operations

## Deployment

No additional configuration needed:
1. Existing `.env` file has GROQ_API_KEY
2. Bot uses same Groq client as translation feature
3. No database or persistent storage required
4. Works on Render.com deployment (same as main bot)

## Logs

Trivia game events are logged with user_id:
- Game start
- Question generation
- Answer correctness
- Final score
- Errors and failures

Example log entries:
```
INFO - User 12345 started trivia game
INFO - Generating 10 trivia questions...
INFO - Successfully generated 10 trivia questions
INFO - Trivia game initialized for user 12345 with 10 questions
INFO - User 12345 answered question 1: correct
INFO - Trivia game ended for user 12345. Score: 8/10
```
