# Trivia Game OpenTDB Integration Plan

## Objective
Revamp the trivia game to use Open Trivia Database (OpenTDB) API instead of Groq-generated questions, supporting both True/False and Multiple Choice questions with category selection.

## Status: ✅ COMPLETED

## Implementation Steps

### Step 1: Add OpenTDB Categories ✅
- [x] Add `TRIVIA_CATEGORIES` constant with 24+ categories
- [x] Include special "All Categories" option (id: 0)
- [x] Source categories from https://opentdb.com/api_category.php

### Step 2: Create OpenTDB Fetching Function ✅
- [x] Create `fetch_opentdb_questions()` function
- [x] Fetch questions from OpenTDB API
- [x] Decode HTML entities in questions and answers
- [x] Translate content to user's target language using Groq
- [x] Handle both boolean and multiple choice question types
- [x] Randomize multiple choice answers
- [x] Track correct answer index after randomization
- [x] Return same data structure format for compatibility

### Step 3: Update Trivia Command ✅
- [x] Modify `trivia_command()` to show category selection
- [x] Create inline keyboard with category buttons
- [x] Organize categories in 2-column grid
- [x] Use callback data: `trivia_category_{id}`
- [x] Remove immediate question generation

### Step 4: Update Question Display ✅
- [x] Modify `send_trivia_question()` for multiple question types
- [x] Boolean: Display True/False buttons
- [x] Multiple choice: Display 4 answer buttons (A, B, C, D)
- [x] Show options in message text for multiple choice
- [x] Use callback data: `trivia_answer_{q_idx}_{ans_idx}`

### Step 5: Update Callback Handler ✅
- [x] Modify `trivia_button_callback()` to handle new patterns
- [x] Handle `trivia_category_{id}` for category selection
- [x] Handle `trivia_answer_{q_idx}_{ans_idx}` for answers
- [x] Support both boolean (0/1) and multiple (0-3) indices
- [x] Compare selected index with correct answer
- [x] Show appropriate feedback

### Step 6: Clean Up ✅
- [x] Remove `generate_trivia_questions()` function
- [x] Remove `verify_claim_with_search()` function
- [x] Update help command text
- [x] Add `import html` for entity decoding

### Step 7: Documentation ✅
- [x] Create `/docs/OPENTDB_INTEGRATION.md`
- [x] Create `/docs/TRIVIA_OPENTDB_REVAMP.md`
- [x] Document API endpoints and parameters
- [x] Document category list
- [x] Document question format handling
- [x] Document translation approach

### Step 8: Testing ✅
- [x] Validate Python syntax
- [x] Test OpenTDB API integration
- [x] Test HTML entity decoding
- [x] Test answer shuffling logic
- [x] Verify all functions present

## Key Technical Decisions

### 1. HTML Entity Decoding
Use Python's built-in `html.unescape()` to decode entities like `&quot;`, `&#039;`, `&amp;`, etc.

### 2. Translation Pipeline
```
OpenTDB (English) → HTML Decode → Translate to Target Language → Display
```

### 3. Answer Randomization
```python
# Create tuples with correctness flag
answer_tuples = [(correct, True)] + [(ans, False) for ans in incorrect]
random.shuffle(answer_tuples)

# Extract shuffled answers and find correct index
shuffled = [ans for ans, _ in answer_tuples]
correct_idx = next(i for i, (_, is_correct) in enumerate(answer_tuples) if is_correct)
```

### 4. Callback Data Format
- Category: `trivia_category_{id}`
- Answer: `trivia_answer_{q_idx}_{ans_idx}`
  - Boolean: ans_idx = 0 (False) or 1 (True)
  - Multiple: ans_idx = 0-3 (option index)
- Next: `trivia_next_{q_idx}`

### 5. Question Data Structure
```python
{
    "claim": str,           # Translated question
    "answer": bool | int,   # Boolean value or option index
    "type": str,            # "boolean" or "multiple"
    "options": list[str],   # For multiple choice only
    "explanation": str      # "N/A" (OpenTDB has no explanations)
}
```

## Error Handling

### OpenTDB API Errors
- Response code 1: No results → Suggest different category
- Response code 2: Invalid parameter → Show error
- Response code 5: Rate limited → Ask user to wait
- HTTP errors: Network timeout → Suggest retry

### Translation Errors
- If Groq translation fails → Use English text
- Log warning but continue game
- Prevents game interruption

### Empty Results
- Check question count before starting game
- Require minimum 10 questions
- Show error if insufficient

## Testing Checklist

### Code Validation
- [x] Python syntax check passed
- [x] All required imports present
- [x] All functions defined
- [x] Constants properly structured

### API Integration
- [x] Category fetch works
- [x] Boolean questions fetch correctly
- [x] Multiple choice questions fetch correctly
- [x] HTML entities decode properly
- [x] Error codes handled

### Functional Tests
- [ ] Local bot testing with /trivia command
- [ ] Category selection works
- [ ] Both question types display correctly
- [ ] Translation to Russian works
- [ ] HTML entities display correctly
- [ ] Answer randomization works
- [ ] Correct answer detection accurate
- [ ] Score tracking correct
- [ ] Complete game flow functional

## Benefits Achieved

### Quality
- ✅ Curated, fact-checked questions
- ✅ No AI hallucinations
- ✅ Large variety of questions
- ✅ 24+ categories for user choice

### Performance
- ✅ Faster than AI generation
- ✅ Consistent response times
- ✅ Predictable behavior

### Cost
- ✅ Free OpenTDB API
- ✅ Reduced Groq usage (only translation)
- ✅ Scalable without cost increase

### User Experience
- ✅ Category selection
- ✅ Multiple question types
- ✅ Educational content
- ✅ Better replayability

## Unresolved Questions

None. All implementation questions resolved during development.

## Future Enhancements

Ideas for future iterations:
1. Session tokens to prevent duplicate questions
2. Difficulty selection (easy/medium/hard)
3. Caching translated questions
4. Generate explanations with Groq
5. Leaderboards
6. Timed mode
7. Multiplayer support

## Files Changed

### Modified
- `/main.py` - All trivia game code (~400 lines changed)

### Created
- `/docs/OPENTDB_INTEGRATION.md` - API integration documentation
- `/docs/TRIVIA_OPENTDB_REVAMP.md` - Implementation summary
- `/plans/trivia-opentdb-integration.md` - This plan document

## Deployment Readiness

### Completed
- [x] Code implementation
- [x] Syntax validation
- [x] API integration testing
- [x] Documentation

### Pending
- [ ] Local bot testing
- [ ] End-to-end testing with real users
- [ ] Production deployment

## References

- OpenTDB Website: https://opentdb.com/
- Category API: https://opentdb.com/api_category.php
- Question API: https://opentdb.com/api.php?amount=10&category=9

---

**Plan Created**: 2026-01-24
**Implementation Status**: ✅ Complete
**Next Step**: Local testing with Telegram bot
