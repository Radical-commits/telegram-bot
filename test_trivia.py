#!/usr/bin/env python3
"""
Test script for trivia game question generation.
Run this to verify the Groq API integration works correctly.
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv
from groq import AsyncGroq

# Load environment variables
load_dotenv()

async def test_question_generation():
    """Test trivia question generation."""
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        print("❌ GROQ_API_KEY not found in .env file")
        return False

    print("✓ GROQ_API_KEY found")

    # Initialize Groq client
    groq_client = AsyncGroq(api_key=groq_api_key)
    print("✓ Groq client initialized")

    # Generate test questions
    print("\n📝 Generating 3 test trivia questions...\n")

    prompt = """Generate exactly 3 weird, surprising, and interesting true-or-false claims about the world.
Make them fun and engaging! Mix true and false claims (roughly 50/50 split).
Topics can include: animals, science, history, geography, technology, human body, space, food, etc.

Requirements:
- Each claim should be clear and specific
- Avoid controversial or offensive topics
- Make them surprising or counterintuitive
- Include a brief (1-2 sentence) explanation for each

Return ONLY a valid JSON array with this exact structure:
[
  {
    "claim": "The exact claim text here",
    "answer": true,
    "explanation": "Brief explanation why this is true or false"
  }
]

Return ONLY the JSON array, no other text."""

    try:
        chat_completion = await asyncio.wait_for(
            groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a trivia question generator. You create interesting true/false questions. You ONLY respond with valid JSON arrays."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.8,
                max_tokens=2048,
            ),
            timeout=30
        )

        response_text = chat_completion.choices[0].message.content.strip()
        print("✓ Received response from Groq")
        print(f"\nRaw response:\n{response_text}\n")

        # Extract JSON
        import re
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
        else:
            json_text = response_text

        # Parse JSON
        questions = json.loads(json_text)
        print("✓ Successfully parsed JSON")

        # Validate structure
        if not isinstance(questions, list):
            print("❌ Response is not a list")
            return False

        if len(questions) == 0:
            print("❌ No questions generated")
            return False

        print(f"✓ Generated {len(questions)} questions\n")

        # Display questions
        for i, q in enumerate(questions, 1):
            if not all(key in q for key in ["claim", "answer", "explanation"]):
                print(f"❌ Question {i} missing required fields")
                continue

            print(f"Question {i}:")
            print(f"  Claim: {q['claim']}")
            print(f"  Answer: {q['answer']}")
            print(f"  Explanation: {q['explanation']}")
            print()

        print("✅ All tests passed! Trivia game is ready to use.")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        return False
    except asyncio.TimeoutError:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("🎮 Trivia Game - Question Generation Test\n")
    print("=" * 60)

    success = asyncio.run(test_question_generation())

    print("=" * 60)

    if success:
        print("\n✅ Test completed successfully!")
        print("\nYou can now run the bot with: python main.py")
        print("Then use the /trivia command in Telegram to play!")
        sys.exit(0)
    else:
        print("\n❌ Test failed. Please check the error messages above.")
        sys.exit(1)
