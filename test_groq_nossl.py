#!/usr/bin/env python3
"""
Test Groq API with SSL verification disabled (TESTING ONLY)
WARNING: This bypasses SSL security checks. Only use for local testing.
"""
import os
import asyncio
import ssl
import httpx
from dotenv import load_dotenv
from groq import AsyncGroq

async def test_groq_no_ssl():
    load_dotenv()

    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key or groq_api_key == "your_groq_api_key_here":
        print("❌ ERROR: GROQ_API_KEY not set properly")
        return

    print(f"✓ API key found (first 10 chars): {groq_api_key[:10]}...")

    # Create custom httpx client with SSL verification disabled
    # WARNING: Only for testing in environments with SSL interception
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    http_client = httpx.AsyncClient(verify=ssl_context)

    try:
        client = AsyncGroq(api_key=groq_api_key, http_client=http_client)
        print("✓ Groq client initialized (SSL verification disabled)")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return

    # Test translation
    print("\n--- Testing Translation ---")
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Translate to Spanish. Only provide the translation."},
                {"role": "user", "content": "Hello, how are you?"}
            ],
            temperature=0.3,
            max_tokens=100
        )
        translation = response.choices[0].message.content.strip()
        print(f"✓ Translation successful: {translation}")
        print("\n✅ Groq API works! The issue is SSL certificate verification.")
        print("\nTo fix this in the bot, you have two options:")
        print("1. Fix SSL certificates (recommended for production)")
        print("2. Disable SSL verification for testing (NOT recommended for production)")
    except Exception as e:
        print(f"❌ Still failed: {type(e).__name__}: {e}")
    finally:
        await http_client.aclose()

if __name__ == "__main__":
    asyncio.run(test_groq_no_ssl())
