# Trivia Game - Architecture & Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Bot Interface                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Command Router                          │
│  - /start, /help, /setlang, /mylang, /trivia               │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│  Translation Features   │   │    Trivia Game          │
│  (existing)             │   │    (new feature)        │
│                         │   │                         │
│  - handle_message()     │   │  - trivia_command()     │
│  - handle_voice()       │   │  - send_question()      │
│  - translate_text()     │   │  - button_callback()    │
│  - transcribe_audio()   │   │  - end_game()           │
└─────────────────────────┘   └─────────────────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│   Button Router         │   │   State Management      │
│   (unified handler)     │   │   (trivia_games dict)   │
│                         │   │                         │
│  lang_* → Language      │   │  user_id → game_state   │
│  trivia_* → Trivia      │   │    - questions          │
└─────────────────────────┘   │    - current_index      │
                              │    - score              │
                              │    - active             │
                              └─────────────────────────┘
                                            │
                                            ▼
                              ┌─────────────────────────┐
                              │    Groq API             │
                              │    (llama-3.3-70b)      │
                              │                         │
                              │  Question Generation    │
                              └─────────────────────────┘
```

## Data Flow - Starting a Game

```
User                Bot                 Groq API            State
 │                   │                      │                │
 │  /trivia          │                      │                │
 ├──────────────────>│                      │                │
 │                   │  Check existing game │                │
 │                   ├─────────────────────────────────────>│
 │                   │                      │                │
 │  "Generating..."  │                      │                │
 │<──────────────────┤                      │                │
 │                   │  Generate questions  │                │
 │                   ├─────────────────────>│                │
 │                   │                      │                │
 │                   │  10 questions JSON   │                │
 │                   │<─────────────────────┤                │
 │                   │  Initialize state    │                │
 │                   ├─────────────────────────────────────>│
 │                   │                      │                │
 │  "Game Started!"  │                      │                │
 │<──────────────────┤                      │                │
 │                   │                      │                │
 │  Question 1/10    │                      │                │
 │  [True] [False]   │                      │                │
 │<──────────────────┤                      │                │
```

## Data Flow - Answering Questions

```
User                Bot                              State
 │                   │                                 │
 │  *taps True*      │                                 │
 ├──────────────────>│                                 │
 │                   │  Get game state                │
 │                   ├────────────────────────────────>│
 │                   │  {questions, index, score}     │
 │                   │<────────────────────────────────┤
 │                   │  Validate index                 │
 │                   │  Check answer                   │
 │                   │  Update score                   │
 │                   ├────────────────────────────────>│
 │  ✅ Correct!      │                                 │
 │  Explanation...   │                                 │
 │  Score: 1/1       │                                 │
 │<──────────────────┤                                 │
 │                   │  Increment index                │
 │                   ├────────────────────────────────>│
 │  [1.5s pause]     │                                 │
 │                   │                                 │
 │  Question 2/10    │                                 │
 │  [True] [False]   │                                 │
 │<──────────────────┤                                 │
```

## Data Flow - Game End

```
User                Bot                              State
 │                   │                                 │
 │  *answers Q10*    │                                 │
 ├──────────────────>│                                 │
 │                   │  Check answer                   │
 │                   │  Update final score             │
 │                   ├────────────────────────────────>│
 │  ✅ Correct!      │                                 │
 │  Explanation...   │                                 │
 │  Score: 8/10      │                                 │
 │<──────────────────┤                                 │
 │                   │  Calculate percentage           │
 │                   │  Generate encouragement         │
 │  🎮 Game Over!    │                                 │
 │  Final: 8/10      │                                 │
 │  (80%)            │                                 │
 │  Excellent work!  │                                 │
 │<──────────────────┤                                 │
 │                   │  Clean up state                 │
 │                   ├────────────────────────────────>│
 │                   │  delete trivia_games[user_id]  │
 │                   │                                 │
```

## State Lifecycle

```
Start Game (/trivia)
        │
        ▼
┌─────────────────┐
│   NO STATE      │
│   user_id not   │
│   in dict       │
└─────────────────┘
        │
        ▼ generate_trivia_questions()
┌─────────────────┐
│   INITIALIZING  │
│   Generating    │
│   questions     │
└─────────────────┘
        │
        ▼ trivia_games[user_id] = {...}
┌─────────────────┐
│   ACTIVE        │
│   active: True  │
│   index: 0      │
│   score: 0      │
└─────────────────┘
        │
        ▼ User answers questions
┌─────────────────┐
│   IN PROGRESS   │
│   index: 0-9    │
│   score: 0-10   │
└─────────────────┘
        │
        ▼ After question 10
┌─────────────────┐
│   COMPLETED     │
│   Show final    │
│   score         │
└─────────────────┘
        │
        ▼ trivia_games.pop(user_id)
┌─────────────────┐
│   CLEANED UP    │
│   State removed │
│   from memory   │
└─────────────────┘
```

## Function Call Hierarchy

```
trivia_command()
    │
    ├─> generate_trivia_questions()
    │       │
    │       └─> groq_client.chat.completions.create()
    │
    ├─> Initialize trivia_games[user_id]
    │
    └─> send_trivia_question()
            │
            └─> Creates InlineKeyboardMarkup with buttons

button_callback_router()
    │
    └─> trivia_button_callback()
            │
            ├─> Validate question index
            ├─> Check answer correctness
            ├─> Update score
            ├─> Display feedback
            │
            ├─> send_trivia_question() [if more questions]
            │
            └─> end_trivia_game() [if last question]
                    │
                    ├─> Calculate final score
                    ├─> Generate encouragement
                    └─> Clean up trivia_games[user_id]
```

## Error Handling Flow

```
                  Function Call
                       │
                       ▼
              ┌────────────────┐
              │   Try Block    │
              └────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
    Success      Rate Limit      Timeout
         │             │             │
         ▼             ▼             ▼
    Continue     Inform User    Retry (3x)
                      │             │
                      │             ▼
                      │        Max Retries?
                      │             │
                      │        ┌────┴────┐
                      │        │         │
                      │       Yes       No
                      │        │         │
                      ▼        ▼         │
              User-Friendly  Continue  ◄─┘
              Error Message
```

## Callback Data Structure

```
Format: trivia_{answer}_{index}

Examples:
├─ trivia_true_0   → User answered True for question 0
├─ trivia_false_0  → User answered False for question 0
├─ trivia_true_5   → User answered True for question 5
└─ trivia_false_9  → User answered False for question 9

Parsing:
parts = callback_data.split("_")
# parts[0] = "trivia"
# parts[1] = "true" or "false"
# parts[2] = "0" to "9" (index)

user_answer = (parts[1] == "true")  # Boolean
question_index = int(parts[2])       # 0-9
```

## State Storage

```python
trivia_games = {
    123456: {  # user_id
        "questions": [
            {
                "claim": "Honey never spoils...",
                "answer": True,
                "explanation": "Archaeologists found..."
            },
            # ... 9 more questions
        ],
        "current_index": 3,  # Currently on question 4
        "score": 2,          # Got 2 out of 3 correct so far
        "active": True       # Game is in progress
    },
    789012: {  # Another user playing simultaneously
        "questions": [...],
        "current_index": 7,  # Different progress
        "score": 5,
        "active": True
    }
}
```

## Integration Points

### With Existing Features

```
┌───────────────────────────────────────┐
│     Telegram Update Handler           │
└───────────────────────────────────────┘
                  │
                  ▼
         Is it a command?
                  │
        ┌─────────┴─────────┐
        │                   │
       Yes                 No
        │                   │
        ▼                   ▼
  ┌─────────┐      ┌─────────────┐
  │ Commands│      │  Messages   │
  └─────────┘      └─────────────┘
        │                   │
        ▼                   ▼
  /trivia?        Text/Voice Message
        │                   │
       Yes                 No
        │                   │
        ▼                   ▼
  trivia_command()  handle_message()
                    handle_voice()
```

### With Button System

```
┌───────────────────────────────────────┐
│     CallbackQueryHandler              │
└───────────────────────────────────────┘
                  │
                  ▼
      button_callback_router()
                  │
        ┌─────────┴─────────┐
        │                   │
   Starts with          Starts with
    "lang_"              "trivia_"
        │                   │
        ▼                   ▼
language_button_    trivia_button_
   callback()          callback()
        │                   │
        ▼                   ▼
  Set user           Check answer,
  language           update score,
  preference         send next Q
```

## Performance Characteristics

```
Operation                Time        Memory      API Calls
─────────────────────────────────────────────────────────────
Start game (/trivia)     2-5s        ~10 KB      1 (Groq)
Answer question          <100ms      -           0
Send next question       <100ms      -           0
End game                 <100ms      -10 KB      0
Total per game           2-6s        0 net       1

Concurrent users:        Unlimited   10KB/user   1/user
```

## Security Considerations

1. **State Isolation**: Each user has separate game state (keyed by user_id)
2. **Validation**: Question index validated to prevent double-answering
3. **Cleanup**: State removed after game ends (no memory leaks)
4. **API Keys**: Reuses existing GROQ_API_KEY from .env
5. **Error Handling**: All errors caught and logged, never exposed to user
6. **Rate Limiting**: Groq API rate limits respected (no retry on 429)

## Testing Strategy

1. **Unit Tests**: Test each function in isolation
2. **Integration Tests**: Test full game flow
3. **Concurrent Tests**: Multiple users playing simultaneously
4. **Error Tests**: API failures, timeouts, invalid JSON
5. **Edge Cases**: Abandoned games, double-answering, expired games

## Monitoring & Logging

```
Log Entry Format:
[TIMESTAMP] - [LEVEL] - [FUNCTION] Message

Examples:
INFO - User 12345 started trivia game
INFO - Generating 10 trivia questions...
INFO - Successfully generated 10 trivia questions
INFO - Trivia game initialized for user 12345 with 10 questions
INFO - User 12345 answered question 1: correct
WARNING - Only 8 valid questions out of 10
ERROR - Trivia generation failed (TimeoutError): Request timeout
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Render.com Server                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Health Check Server (port 8080)                  │  │
│  │  - GET / → Bot info                               │  │
│  │  - GET /health → Status JSON                      │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Telegram Bot (main.py)                           │  │
│  │  ├─ Translation Features                          │  │
│  │  ├─ Trivia Game Feature ← NEW                     │  │
│  │  └─ Error Handlers                                │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  In-Memory State                                  │  │
│  │  ├─ user_preferences (language)                   │  │
│  │  └─ trivia_games (game state) ← NEW              │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
   │  Telegram    │ │   Groq API   │ │   Logs       │
   │  API         │ │   (llama)    │ │   (stdout)   │
   └──────────────┘ └──────────────┘ └──────────────┘
```

This architecture shows how the trivia game integrates seamlessly with the existing bot infrastructure while maintaining clean separation of concerns.
