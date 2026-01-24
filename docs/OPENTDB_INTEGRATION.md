# Open Trivia Database Integration

This document describes the integration of the Open Trivia Database (OpenTDB) API into the Telegram translation bot's trivia game feature.

## Overview

The trivia game has been revamped to use the Open Trivia Database API instead of AI-generated questions. This provides:
- Curated, fact-checked questions from a reliable source
- 24+ categories covering diverse topics
- Both True/False and Multiple Choice question types
- Consistent quality and variety

## API Details

### Base URL
```
https://opentdb.com/
```

### Endpoints Used

1. **Category List**
   - Endpoint: `https://opentdb.com/api_category.php`
   - Returns: JSON with array of categories (id and name)
   - Used for: Building category selection menu

2. **Question Fetch**
   - Endpoint: `https://opentdb.com/api.php?amount={count}&category={id}`
   - Parameters:
     - `amount`: Number of questions (we use 10)
     - `category`: Category ID (optional, omit for all categories)
   - Returns: JSON with array of question objects

### Response Format

Questions are returned with this structure:

```json
{
  "response_code": 0,
  "results": [
    {
      "type": "boolean",
      "difficulty": "easy",
      "category": "General Knowledge",
      "question": "HTML encoded question text",
      "correct_answer": "True",
      "incorrect_answers": ["False"]
    },
    {
      "type": "multiple",
      "difficulty": "medium",
      "category": "Geography",
      "question": "HTML encoded question text",
      "correct_answer": "Correct answer",
      "incorrect_answers": ["Wrong 1", "Wrong 2", "Wrong 3"]
    }
  ]
}
```

### Response Codes
- `0`: Success
- `1`: No results (category exhausted)
- `2`: Invalid parameter
- `3`: Token not found
- `4`: Token empty (all questions for token used)
- `5`: Rate limit (5 seconds between requests)

## Implementation

### Categories

24 categories are available:

| ID | Category Name |
|----|--------------|
| 0 | All Categories (special) |
| 9 | General Knowledge |
| 10 | Entertainment: Books |
| 11 | Entertainment: Film |
| 12 | Entertainment: Music |
| 13 | Entertainment: Musicals & Theatres |
| 14 | Entertainment: Television |
| 15 | Entertainment: Video Games |
| 16 | Entertainment: Board Games |
| 17 | Science & Nature |
| 18 | Science: Computers |
| 19 | Science: Mathematics |
| 20 | Mythology |
| 21 | Sports |
| 22 | Geography |
| 23 | History |
| 24 | Politics |
| 25 | Art |
| 26 | Celebrities |
| 27 | Animals |
| 28 | Vehicles |
| 29 | Entertainment: Comics |
| 30 | Science: Gadgets |
| 31 | Entertainment: Japanese Anime & Manga |
| 32 | Entertainment: Cartoon & Animations |

### Game Flow

1. **Category Selection**
   - User runs `/trivia` command
   - Bot displays inline keyboard with all categories
   - Categories arranged in 2-column grid for mobile readability

2. **Question Fetching**
   - When category selected, bot calls `fetch_opentdb_questions()`
   - Function fetches 10 questions from OpenTDB API
   - Questions are in English with HTML entities (e.g., `&quot;`, `&#039;`)

3. **HTML Entity Decoding**
   - All questions and answers decoded using `html.unescape()`
   - Prevents display issues with quotes, apostrophes, special characters

4. **Translation**
   - If user's language is not English, translate questions and answers
   - Uses Groq Llama 3.3 70B model for translation
   - Maintains answer correctness by tracking indices, not text matching

5. **Answer Randomization**
   - For multiple choice questions, answers are shuffled
   - Correct answer index tracked after shuffling
   - Prevents users from guessing patterns

6. **Question Display**
   - Boolean questions: Show "Правда" (True) / "Ложь" (False) buttons
   - Multiple choice: Show 4 answer buttons (A, B, C, D format)
   - Question text and options displayed in user's language

7. **Answer Checking**
   - Compare selected answer index with correct answer index
   - Show feedback with correct answer if wrong
   - Track score throughout game

8. **Game Completion**
   - After 10 questions, show final score
   - Display encouraging message based on percentage
   - Allow user to start new game

### Data Structure

Processed questions use this format:

```python
{
    "claim": str,        # Translated question text
    "answer": bool|int,  # Boolean: True/False, Multiple: index 0-3
    "type": str,         # "boolean" or "multiple"
    "options": list,     # For multiple: 4 shuffled translated answers
    "explanation": str   # Always "N/A" (OpenTDB has no explanations)
}
```

### Callback Data Format

Button callbacks use these patterns:

- Category selection: `trivia_category_{category_id}`
- Answer button: `trivia_answer_{question_index}_{answer_index}`
  - For boolean: answer_index is 0 (False) or 1 (True)
  - For multiple: answer_index is 0-3 (corresponds to shuffled options)
- Next question: `trivia_next_{question_index}`

## Error Handling

The implementation handles these error scenarios:

1. **API Connection Failures**
   - Timeout after 15 seconds
   - Show user-friendly error message
   - Suggest trying again

2. **Rate Limiting**
   - OpenTDB limits requests to 1 per 5 seconds
   - Error code 5 detected and shown to user
   - User prompted to wait and retry

3. **Empty Results**
   - Some categories may be exhausted
   - Show error and suggest different category
   - User can select another category

4. **Translation Failures**
   - If Groq translation fails, use English text
   - Log warning but continue game
   - Prevents game interruption

5. **HTML Decoding Issues**
   - Standard library `html.unescape()` handles all cases
   - Covers common entities: `&quot;`, `&#039;`, `&amp;`, etc.

## Benefits Over AI Generation

1. **Quality**: Curated, fact-checked questions
2. **Variety**: Large database with many categories
3. **Reliability**: Consistent quality, no hallucinations
4. **Performance**: Faster than AI generation
5. **Cost**: Free API, reduces Groq usage
6. **Maintenance**: No need to tune prompts or validate AI output

## Limitations

1. **No Explanations**: OpenTDB doesn't provide answer explanations
2. **English Source**: All questions originally in English, require translation
3. **Rate Limits**: 5-second cooldown between requests
4. **Category Exhaustion**: Some categories may run out of questions
5. **Fixed Content**: Questions don't change unless OpenTDB is updated

## Future Enhancements

Potential improvements for future versions:

1. **Session Tokens**: Use OpenTDB session tokens to prevent duplicate questions
2. **Difficulty Selection**: Allow users to choose easy/medium/hard
3. **Caching**: Cache translated questions to reduce API calls
4. **Mixed Categories**: Allow selecting multiple categories
5. **Custom Explanations**: Generate explanations using Groq for educational value
6. **Leaderboards**: Track user scores across games
7. **Timed Mode**: Add optional time limits for answers

## Testing Checklist

Before deploying, verify:

- [ ] Category selection displays all 24+ categories
- [ ] Selecting "All Categories" fetches mixed questions
- [ ] Boolean questions display with True/False buttons
- [ ] Multiple choice questions display with 4 answer buttons
- [ ] Questions are translated to user's selected language
- [ ] HTML entities are properly decoded (no `&quot;` in output)
- [ ] Multiple choice answers are randomized
- [ ] Correct/incorrect answer detection works
- [ ] Score tracking is accurate
- [ ] Final score display shows correct percentage
- [ ] Error handling works for API failures
- [ ] Rate limiting is handled gracefully

## References

- OpenTDB Website: https://opentdb.com/
- API Documentation: https://opentdb.com/api_config.php
- Category Endpoint: https://opentdb.com/api_category.php
- GitHub: https://github.com/opentdb

## Code Location

All trivia game code is in `main.py`:

- Line 54-85: `TRIVIA_CATEGORIES` constant
- Line 799-976: `fetch_opentdb_questions()` function
- Line 1052-1099: `trivia_command()` - Category selection
- Line 1102-1189: `send_trivia_question()` - Question display
- Line 1192-1357: `trivia_button_callback()` - Button handler
- Line 1360-1413: `end_trivia_game()` - Game completion
