<objective>
Add an interactive True/False trivia game feature to the Telegram translation bot. Users can start the game with a command, answer 10 weird fact questions using inline buttons, and receive a score at the end.

This feature adds entertainment value and engagement to the bot, making it more than just a translation tool.
</objective>

<context>
- Existing bot: Telegram translation bot (main.py)
- Current features: Text translation, voice transcription, language selection with inline buttons
- Tech stack: Python, python-telegram-bot (v20+, async), Groq API (for LLM), existing inline keyboard patterns
- Files to examine: @main.py (to understand existing button handlers and command structure)
- This is a new feature addition, not modifying existing translation functionality
</context>

<requirements>
**Trivia Game Flow:**
1. User types `/trivia` command to start game
2. Bot generates 10 weird/interesting true-or-false claims using Groq API
3. Bot uses web search to verify each claim is actually true or false (avoid hallucinations)
4. Bot presents one claim at a time with [True] and [False] buttons
5. User taps button to answer
6. Bot shows if answer was correct/wrong, then shows next question
7. After 10 questions, bot displays final score: "You scored X out of 10!"
8. User can play again with `/trivia` (gets different random questions)

**Question Generation:**
- Use existing Groq API client (llama-3.3-70b-versatile model)
- Generate weird, surprising, or counterintuitive facts (make it fun!)
- Mix of true and false claims (roughly 50/50 split)
- Use web search to verify each claim before presenting to user
- If web search can't verify a claim, regenerate that question
- Examples of good questions:
  - "A group of flamingos is called a 'flamboyance'" (True)
  - "Bananas grow upside down on trees" (False - they're herbs, not trees)
  - "Octopuses have three hearts" (True)

**User Interface:**
- Use inline keyboard buttons (like existing /setlang feature)
- Two buttons per question: [✓ True] [✗ False]
- Show question number: "Question 3/10"
- After answer, show: "✅ Correct!" or "❌ Wrong! The answer is True/False"
- Display explanation/fun fact after each answer (1-2 sentences)
- Final score message with encouragement based on score

**State Management:**
- Track game state per user (current question, score, question list)
- Use in-memory dictionary similar to user_preferences pattern
- Clean up state after game ends
- Handle edge cases: user abandons game, starts new game mid-session

**Commands:**
- `/trivia` - Start new trivia game (or restart if already playing)
- Update `/help` command to mention trivia feature
- Update `/start` welcome message to mention trivia

**Error Handling:**
- Handle Groq API failures gracefully
- Handle web search failures (retry or skip question)
- Timeout handling for slow API responses
- User-friendly error messages if game can't start
</requirements>

<implementation>
**Files to Modify:**

1. **main.py** - Add trivia game logic:
   - Import web search capabilities (WebSearch tool if available, or use requests)
   - Create game state dictionary: `trivia_games = {user_id: {...}}`
   - Add `/trivia` command handler
   - Add callback handler for True/False button presses
   - Create function: `async def generate_trivia_questions(count: int = 10) -> list`
   - Create function: `async def verify_claim_with_search(claim: str, expected_answer: bool) -> bool`
   - Update `help_command()` and `start_command()` to mention trivia
   - Use existing `groq_client` for question generation
   - Use existing inline button patterns from language selection

**Question Generation Approach:**
```python
# Prompt for Groq API:
"Generate 10 weird, surprising true-or-false claims about the world.
Make them interesting and fun. Mix true and false claims (about 50/50).
Format: JSON array with {claim: str, answer: bool, explanation: str}"
```

**Web Search Verification:**
- For each generated claim, search for verification
- If search results contradict the claim, flag it
- Regenerate claims that can't be verified
- Use search query: "Is it true that [claim]? fact check"

**State Structure:**
```python
trivia_games = {
    user_id: {
        "questions": [...],  # List of question dicts
        "current_index": 0,
        "score": 0,
        "active": True
    }
}
```

**Callback Data Format:**
- `trivia_true_<index>` - User answered True for question at index
- `trivia_false_<index>` - User answered False for question at index

**What to Avoid:**
- Don't block translation features while playing trivia
- Don't store trivia state permanently (in-memory is fine)
- Don't generate offensive or controversial claims
- Don't make questions too obscure (should be fun, not frustrating)
- Don't forget to clean up game state after completion
</implementation>

<output>
Modify this file:

**./main.py** - Add trivia game feature:
- Import statements (if needed for web search)
- Game state dictionary: `trivia_games: Dict = {}`
- `async def generate_trivia_questions()` - Generate 10 verified questions
- `async def verify_claim_with_search()` - Verify claim using web search
- `async def trivia_command()` - Handle /trivia command, start game
- `async def trivia_button_callback()` - Handle True/False button presses
- `async def send_trivia_question()` - Send single question with buttons
- `async def end_trivia_game()` - Show final score, clean up state
- Update `help_command()` - Add trivia to help text
- Update `start_command()` - Mention trivia in welcome message
- Register trivia handler: `application.add_handler(CommandHandler("trivia", trivia_command))`
- Update callback handler to handle trivia buttons (may need pattern matching)

Example button layout:
```
Question 5/10:
"Honey never spoils and can last thousands of years"

[✓ True] [✗ False]
```

Example response after answer:
```
✅ Correct!

Archaeologists have found 3000-year-old honey in Egyptian tombs
that was still perfectly edible!

Score: 5/5

[Next Question →]
```
</output>

<verification>
Before declaring complete, verify:

1. **Question Generation:**
   - Groq API generates interesting weird facts
   - Web search verification works and filters bad claims
   - Questions are well-formatted and clear
   - Mix of true and false answers (roughly 50/50)

2. **Game Flow:**
   - `/trivia` starts game successfully
   - Questions appear one at a time
   - Buttons work and record answers correctly
   - Score tracking is accurate
   - Final score displays after 10 questions
   - User can start new game with different questions

3. **UI/UX:**
   - Inline buttons match existing style (/setlang pattern)
   - Question counter shows progress (3/10)
   - Feedback is immediate after each answer
   - Explanations are interesting and informative
   - Final score message is encouraging

4. **State Management:**
   - Game state tracks correctly per user
   - Multiple users can play simultaneously
   - Abandoned games don't cause issues
   - State cleans up after game ends

5. **Error Handling:**
   - Handles Groq API failures gracefully
   - Web search timeouts don't crash bot
   - User sees helpful error messages
   - Bot continues to work if trivia fails

6. **Integration:**
   - Translation features still work during trivia
   - `/help` mentions trivia feature
   - `/start` welcomes users and mentions trivia
   - No conflicts with existing commands

7. **Testing:**
   - Play complete game (10 questions)
   - Test abandoning game mid-way
   - Test starting new game while one is active
   - Test with multiple users simultaneously
   - Verify score calculation is correct
   - Check that questions change on replay
</verification>

<success_criteria>
Trivia game feature is complete when:
- `/trivia` command starts interactive game with inline buttons
- Bot generates 10 verified weird true/false claims using Groq + web search
- Users can answer with True/False buttons
- Bot provides immediate feedback (correct/wrong + explanation)
- Final score displays after 10 questions ("X out of 10")
- Users get different random questions when replaying
- Multiple users can play simultaneously without interference
- Game integrates cleanly with existing translation bot features
- Error handling prevents game failures from breaking bot
- Help and start commands mention trivia feature
- Code follows existing bot patterns and style

**Deliverable:** A fun, engaging trivia game that adds entertainment value while maintaining the bot's core translation functionality.
</success_criteria>