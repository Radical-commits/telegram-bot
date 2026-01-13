#!/usr/bin/env python3
"""
Quick test script to diagnose Groq API issues
"""
import os
import asyncio
from dotenv import load_dotenv
from groq import AsyncGroq

async def test_groq():
    # Load environment variables
    load_dotenv()

    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key or groq_api_key == "your_groq_api_key_here":
        print("❌ ERROR: GROQ_API_KEY not set properly in .env file")
        print("Please set a valid Groq API key in your .env file")
        return

    print(f"✓ API key found (first 10 chars): {groq_api_key[:10]}...")

    # Initialize Groq client
    try:
        client = AsyncGroq(api_key=groq_api_key)
        print("✓ Groq client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Groq client: {e}")
        return

    # Test 1: Simple translation
    print("\n--- Test 1: Translation ---")
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a translator. Translate the following text to Spanish. Only provide the translation, no explanations."
                },
                {
                    "role": "user",
                    "content": "Hello, how are you?"
                }
            ],
            temperature=0.3,
            max_tokens=1024
        )
        translation = response.choices[0].message.content.strip()
        print(f"✓ Translation successful: {translation}")
    except Exception as e:
        print(f"❌ Translation failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test 2: List available models (optional)
    print("\n--- Test 2: Check API connectivity ---")
    try:
        # Try a minimal request
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )
        print(f"✓ API connectivity OK")
    except Exception as e:
        print(f"❌ API connectivity issue: {type(e).__name__}: {e}")
        return

    print("\n✅ All tests passed! Groq API is working correctly.")
    print("\nIf the bot still fails, the issue might be:")
    print("  1. Telegram bot token invalid")
    print("  2. Network/firewall blocking Telegram")
    print("  3. Different issue in the bot code")

if __name__ == "__main__":
    asyncio.run(test_groq())
