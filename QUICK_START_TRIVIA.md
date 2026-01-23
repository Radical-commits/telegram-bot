# Quick Start Guide - Trivia Game

## Play Trivia Now!

### 1. Start the Bot
If the bot isn't running yet:
```bash
cd /path/to/telegram-bot
python main.py
```

### 2. Test Question Generation (Optional)
Verify the trivia feature works:
```bash
python test_trivia.py
```

Expected output: "✅ All tests passed!"

### 3. Play in Telegram

1. Open your Telegram bot
2. Type: `/trivia`
3. Wait 2-5 seconds for questions to generate
4. Read the question
5. Tap **[✓ True]** or **[✗ False]**
6. See if you were correct + get an explanation
7. Continue through 10 questions
8. See your final score!
9. Play again: `/trivia`

## Example Game

```
You: /trivia

Bot: 🎮 Starting Trivia Game!
     Generating 10 weird and interesting questions for you...

Bot: 🎮 Trivia Game Started!
     Answer 10 True/False questions.
     You'll get instant feedback after each answer.

     Let's begin!

Bot: Question 1/10

     Honey never spoils and can last thousands of years

     [✓ True] [✗ False]

You: *taps True*

Bot: ✅ Correct!

     Archaeologists have found 3000-year-old honey in Egyptian
     tombs that was still perfectly edible!

     Score: 1/1

Bot: Question 2/10

     Bananas grow on trees

     Current score: 1/1

     [✓ True] [✗ False]

You: *taps True*

Bot: ❌ Wrong! The answer is False.

     Banana plants are actually giant herbs, not trees. They
     have no woody trunk and are technically berries!

     Score: 1/2

[... continues for 10 questions ...]

Bot: 🎮 Game Over!

     Final Score: 8 out of 10
     (80%)

     Excellent work! You really know your facts!

     Want to play again? Use /trivia to start a new game
     with different questions!
```

## Commands

- `/start` - Welcome message (now mentions trivia!)
- `/trivia` - Start a new trivia game
- `/help` - See all commands including trivia details

## Features

- 10 questions per game
- Weird and surprising facts
- Instant feedback (✅ correct / ❌ wrong)
- Explanations for each answer
- Live score tracking
- Final score with encouragement
- Different questions each time
- Multiple players can play at once

## Troubleshooting

### Bot says "Failed to start trivia game"
- Check that GROQ_API_KEY is set in `.env` file
- Run `python test_trivia.py` to diagnose
- Check bot logs for errors

### Questions take too long to generate
- Normal: 2-5 seconds
- If >10 seconds, check internet connection
- Groq API might be busy, try again

### Translation stopped working
- Translation and trivia are independent
- Send any text message to translate (not during trivia)
- Set language first with `/setlang`

### Game got stuck
- Just type `/trivia` again to restart
- Old games are automatically cancelled
- Each user has their own game state

## Technical Details

- **Model**: Groq llama-3.3-70b-versatile
- **API Call**: One call per game (generates 10 questions)
- **Response Time**: 2-5 seconds for generation, instant for answers
- **Cost**: ~5,000 tokens per game
- **State**: In-memory (no database needed)
- **Isolation**: Each user has separate game state

## Files

- `main.py` - Bot code with trivia game
- `test_trivia.py` - Test script
- `TRIVIA_FEATURE.md` - Full documentation
- `IMPLEMENTATION_SUMMARY.md` - Developer notes
- `QUICK_START_TRIVIA.md` - This file

## Having Fun?

Play as many times as you want! Each game has different questions generated on the fly.

**Enjoy the trivia game!** 🎮
