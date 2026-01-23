<objective>
Improve the existing trivia game feature with two key enhancements:
1. Questions and answers should be in the user's selected language (from /setlang)
2. Each trivia session should generate completely new questions (not from a pool)

This makes the trivia game more personalized and ensures unlimited replay value.
</objective>

<context>
- Existing trivia game: Working /trivia command with 10 True/False questions
- Current behavior: Questions are in English only, may repeat across sessions
- User language preferences: Already stored in `user_preferences` dictionary
- File to modify: @main.py (specifically the trivia-related functions)
- Groq API: Already integrated and used for question generation
</context>

<requirements>
**1. Language-Aware Questions:**
- When user starts `/trivia`, check their language preference from `user_preferences[user_id]`
- If user has no language preference, default to English
- Generate ALL trivia content in the user's language:
  - Questions/claims
  - Explanations
  - Feedback messages ("Correct!", "Wrong!")
  - Final score message
- Update Groq prompt to specify target language
- Example: Spanish user sees "El pulpo tiene tres corazones" instead of "Octopuses have three hearts"

**2. Fresh Questions Every Session:**
- Remove any question caching or reuse logic
- Each `/trivia` command should:
  - Generate completely new set of 10 questions
  - Use Groq API with temperature=0.8 for variety
  - Ensure no repetition within same session
- Users should never see the same question twice (or very rarely due to randomness)
- No need to track "used questions" - let Groq generate fresh content

**3. Language Handling Details:**
- Map language codes to language names for Groq:
  - "en" → "English"
  - "es" → "Spanish"
  - "fr" → "French"
  - etc. (all 12 supported languages)
- Groq prompt should be clear: "Generate in [Language]. All text must be in [Language]."
- Keep button labels language-agnostic or translate them:
  - Option A: Keep "✓ True" / "✗ False" (universally understood)
  - Option B: Translate to target language ("✓ Verdadero" / "✗ Falso" for Spanish)

**4. User Experience:**
- Show language in game start message: "🎮 Trivia Game (Spanish)!"
- If user has no language set, prompt them: "Set your language first with /setlang to play trivia in your language, or continue in English."
- Maintain all existing functionality (scoring, explanations, replay, etc.)
</requirements>

<implementation>
**Functions to Modify:**

1. **`generate_trivia_questions()`** - Add language parameter:
   ```python
   async def generate_trivia_questions(language_code: str = "en", count: int = 10) -> list:
       # Map language code to language name
       language_map = {
           "en": "English", "es": "Spanish", "fr": "French",
           "de": "German", "it": "Italian", "pt": "Portuguese",
           "ru": "Russian", "zh": "Chinese", "ja": "Japanese",
           "ko": "Korean", "ar": "Arabic", "hi": "Hindi"
       }
       language_name = language_map.get(language_code, "English")

       # Update Groq prompt to include language
       prompt = f"""Generate 10 weird, surprising true-or-false claims about the world.
       All content must be in {language_name}.
       Make them interesting and fun. Mix true and false claims (about 50/50).
       Format: JSON array with {{"claim": str, "answer": bool, "explanation": str}}

       Important: The claim, explanation, and all text must be written in {language_name}."""
   ```

2. **`trivia_command()`** - Get user's language preference:
   ```python
   async def trivia_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
       user_id = update.effective_user.id

       # Get user's language preference
       language_code = user_preferences.get(user_id, "en")  # Default to English

       # Show language in start message
       language_map = {...}
       language_name = language_map.get(language_code, "English")

       await update.message.reply_text(f"🎮 Starting Trivia Game ({language_name})!...")

       # Generate questions in user's language
       questions = await generate_trivia_questions(language_code=language_code)
   ```

3. **Feedback Messages** - Make them language-aware:
   - Create translation dictionary for UI strings
   - Or generate them in-context with each question
   - Keep simple: "✅" / "❌" are universal, explanations already in target language

4. **Remove Caching** (if any exists):
   - Ensure no global question pool
   - Each call to `generate_trivia_questions()` should be fresh
   - Current implementation likely already does this

**What to Avoid:**
- Don't translate button callback data (keep `trivia_true_0` format)
- Don't cache questions between sessions
- Don't break existing translation features
- Don't require users to set language (default to English)
</implementation>

<output>
Modify this file:

**./main.py** - Update trivia functions:
1. Add `language_code` parameter to `generate_trivia_questions()`
2. Add language mapping dictionary (code → name)
3. Update Groq prompt to specify target language
4. Modify `trivia_command()` to:
   - Get user's language preference
   - Pass language to question generator
   - Show language in start message
5. Optionally translate UI feedback messages
6. Verify no question caching exists (remove if found)

Example updated flow:
```
User (with Spanish selected): /trivia

Bot: 🎮 ¡Comenzando Juego de Trivia (Español)!
     Generando 10 preguntas...

Bot: 🎮 ¡Juego Iniciado!
     Pregunta 1/10
     La miel nunca se echa a perder y puede durar miles de años

     [✓ Verdadero] [✗ Falso]

User: *taps Verdadero*

Bot: ✅ ¡Correcto!
     Los arqueólogos han encontrado miel de 3000 años en tumbas
     egipcias que todavía era comestible.

     Puntuación: 1/1
```
</output>

<verification>
Before declaring complete, verify:

1. **Language Integration:**
   - Questions generate in user's selected language
   - Explanations are in target language
   - Feedback messages work (keep simple with ✅/❌)
   - No English leaking into non-English games

2. **Fresh Questions:**
   - Each `/trivia` generates new questions
   - No caching between sessions
   - Questions are different each time (test by playing 2-3 games)
   - Temperature parameter ensures variety

3. **Default Language:**
   - Users without language preference get English
   - No errors if language preference not set
   - Gracefully handles all 12 supported languages

4. **Existing Functionality:**
   - All original trivia features still work
   - Score tracking accurate
   - Button callbacks work correctly
   - Multiple users can play simultaneously
   - Translation feature unaffected

5. **Testing:**
   - Play game in English (default)
   - Set language to Spanish with `/setlang spanish`
   - Play game in Spanish
   - Verify questions and explanations are in Spanish
   - Play again, verify different questions
   - Test with multiple languages (French, German, etc.)
</verification>

<success_criteria>
Improvements are complete when:
- Trivia questions appear in user's selected language (from /setlang)
- Explanations and feedback are in target language
- Each trivia session generates completely new questions
- No question repetition across sessions (or very rare)
- Default to English if no language preference set
- All existing trivia functionality remains intact
- Users can play unlimited games with fresh content
- Works correctly for all 12 supported languages

**Deliverable:** A more personalized and replayable trivia experience that respects user language preferences.
</success_criteria>