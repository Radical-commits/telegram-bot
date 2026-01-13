"""
Telegram Translation Bot - Phase 4: Production Ready
A bot that provides real-time text translation using Groq's Llama models.
Supports voice message transcription using Whisper large-v3.
Supports multiple languages with user preference storage.
Production-ready with retry logic, rate limiting, and graceful shutdown.
"""

import asyncio
import logging
import os
import signal
import sys
import tempfile
import time
from functools import wraps
from pathlib import Path
from typing import Callable, Dict, Optional

from dotenv import load_dotenv
from groq import AsyncGroq, RateLimitError, APIError, APIConnectionError, APITimeoutError
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Load environment variables from .env file
load_dotenv()

# Configure logging for production
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s] %(message)s",
    level=getattr(logging, log_level, logging.INFO)
)
logger = logging.getLogger(__name__)

# Log startup without sensitive data
logger.info(f"Starting bot with log level: {log_level}")

# Supported languages (will be used for validation)
SUPPORTED_LANGUAGES = {
    "english": "en",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "portuguese": "pt",
    "russian": "ru",
    "chinese": "zh",
    "japanese": "ja",
    "korean": "ko",
    "arabic": "ar",
    "hindi": "hi",
}

# Language code to full name mapping for Groq translation prompts
LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
}

# In-memory storage for user language preferences
# Format: {user_id: language_code}
user_preferences: Dict[int, str] = {}

# Groq client (initialized in main)
groq_client: Optional[AsyncGroq] = None

# Timeout configuration (in seconds)
TRANSLATION_TIMEOUT = 30  # 30 seconds for text translation
TRANSCRIPTION_TIMEOUT = 60  # 60 seconds for voice transcription
FILE_DOWNLOAD_TIMEOUT = 30  # 30 seconds for file download

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]  # Exponential backoff: 1s, 2s, 4s


def async_retry(max_retries: int = MAX_RETRIES, delays: list = None) -> Callable:
    """
    Decorator to retry async functions with exponential backoff.
    Only retries on transient errors (5xx, network, timeout).
    Does not retry on client errors (4xx) or rate limits (429).

    Args:
        max_retries: Maximum number of retry attempts
        delays: List of delays between retries (exponential backoff)
    """
    if delays is None:
        delays = RETRY_DELAYS

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)

                except RateLimitError as e:
                    # Don't retry rate limits - inform user immediately
                    logger.warning(f"Rate limit hit in {func.__name__}: {e}")
                    raise

                except (APIConnectionError, APITimeoutError) as e:
                    # Transient errors - retry with backoff
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = delays[attempt] if attempt < len(delays) else delays[-1]
                        logger.warning(
                            f"Transient error in {func.__name__} (attempt {attempt + 1}/{max_retries}): {type(e).__name__}. "
                            f"Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"Max retries reached in {func.__name__}: {type(e).__name__}")

                except APIError as e:
                    # Check if it's a 5xx server error (retriable) or 4xx client error (not retriable)
                    error_str = str(e).lower()
                    if "500" in error_str or "502" in error_str or "503" in error_str or "504" in error_str:
                        # Server error - retry
                        last_exception = e
                        if attempt < max_retries - 1:
                            delay = delays[attempt] if attempt < len(delays) else delays[-1]
                            logger.warning(
                                f"Server error in {func.__name__} (attempt {attempt + 1}/{max_retries}): {e}. "
                                f"Retrying in {delay}s..."
                            )
                            await asyncio.sleep(delay)
                        else:
                            logger.error(f"Max retries reached in {func.__name__}: {e}")
                    else:
                        # Client error (4xx) - don't retry
                        logger.error(f"Client error in {func.__name__} (not retrying): {e}")
                        raise

                except Exception as e:
                    # Unknown error - log and don't retry
                    logger.error(f"Unexpected error in {func.__name__}: {type(e).__name__}: {e}")
                    raise

            # All retries exhausted
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def validate_language(language: str) -> tuple[bool, str]:
    """
    Validate if the provided language is supported.

    Args:
        language: Language name to validate (case-insensitive)

    Returns:
        Tuple of (is_valid, language_code_or_error_message)
    """
    language_lower = language.lower()

    if language_lower in SUPPORTED_LANGUAGES:
        return True, SUPPORTED_LANGUAGES[language_lower]

    # Provide helpful error message with supported languages
    supported_list = ", ".join(sorted(SUPPORTED_LANGUAGES.keys()))
    error_msg = f"Language '{language}' is not supported.\n\nSupported languages:\n{supported_list}"
    return False, error_msg


@async_retry(max_retries=MAX_RETRIES)
async def transcribe_audio(file_path: str) -> tuple[bool, str]:
    """
    Transcribe audio file using Groq Whisper large-v3 model.
    Includes automatic retry with exponential backoff for transient errors.

    Args:
        file_path: Path to the audio file

    Returns:
        Tuple of (success: bool, result: str)
        - On success: (True, transcribed_text)
        - On failure: (False, error_message)
    """
    if not groq_client:
        logger.error("Groq client is not initialized")
        return False, "Transcription service is not available. Please contact the administrator."

    try:
        logger.info(f"Transcribing audio file: {file_path}")

        # Open the audio file and send to Whisper API with timeout
        with open(file_path, "rb") as audio_file:
            transcription = await asyncio.wait_for(
                groq_client.audio.transcriptions.create(
                    file=(Path(file_path).name, audio_file.read()),
                    model="whisper-large-v3",
                    response_format="text",
                    temperature=0.0,  # Deterministic transcription
                ),
                timeout=TRANSCRIPTION_TIMEOUT
            )

        # The response is the transcribed text directly
        transcribed_text = transcription.strip()

        if not transcribed_text:
            logger.warning("Transcription returned empty text")
            return False, "Audio file appears to be empty or contains no speech."

        logger.info(f"Transcription successful: {transcribed_text[:50]}...")
        return True, transcribed_text

    except asyncio.TimeoutError:
        logger.error(f"Transcription timeout after {TRANSCRIPTION_TIMEOUT}s")
        return False, f"Transcription took too long (>{TRANSCRIPTION_TIMEOUT}s). Please try a shorter voice message."

    except RateLimitError as e:
        logger.warning(f"Transcription rate limit: {e}")
        return False, "Transcription service is busy. Please wait a moment and try again."

    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"Transcription failed ({error_type}): {str(e)}")

        # Provide user-friendly error messages
        if "api_key" in str(e).lower() or "authentication" in str(e).lower():
            return False, "Transcription service authentication failed. Please contact the administrator."
        elif "format" in str(e).lower() or "codec" in str(e).lower():
            return False, "Audio format is not supported. Please try a different voice message."
        else:
            return False, f"Transcription failed: {error_type}. Please try again later."


@async_retry(max_retries=MAX_RETRIES)
async def translate_text(text: str, target_language_code: str) -> tuple[bool, str]:
    """
    Translate text to the target language using Groq API.
    Includes automatic retry with exponential backoff for transient errors.

    Args:
        text: The text to translate
        target_language_code: Target language code (e.g., 'es', 'fr')

    Returns:
        Tuple of (success: bool, result: str)
        - On success: (True, translated_text)
        - On failure: (False, error_message)
    """
    if not groq_client:
        logger.error("Groq client is not initialized")
        return False, "Translation service is not available. Please contact the administrator."

    target_language_name = LANGUAGE_NAMES.get(target_language_code, target_language_code)

    try:
        logger.info(f"Translating text to {target_language_name}: {text[:50]}...")

        # Create chat completion request to Groq with timeout
        chat_completion = await asyncio.wait_for(
            groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a translator. Translate the following text to {target_language_name}. "
                                   f"Only provide the translation, no explanations or additional text."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3,  # Lower temperature for more consistent translations
                max_tokens=1024,
            ),
            timeout=TRANSLATION_TIMEOUT
        )

        translated_text = chat_completion.choices[0].message.content.strip()
        logger.info(f"Translation successful: {translated_text[:50]}...")
        return True, translated_text

    except asyncio.TimeoutError:
        logger.error(f"Translation timeout after {TRANSLATION_TIMEOUT}s")
        return False, f"Translation took too long (>{TRANSLATION_TIMEOUT}s). Please try again with shorter text."

    except RateLimitError as e:
        logger.warning(f"Translation rate limit: {e}")
        return False, "Translation service is busy. Please wait a moment and try again."

    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"Translation failed ({error_type}): {str(e)}")

        # Provide user-friendly error messages
        if "api_key" in str(e).lower() or "authentication" in str(e).lower():
            return False, "Translation service authentication failed. Please contact the administrator."
        else:
            return False, f"Translation failed: {error_type}. Please try again later."


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command - welcome message."""
    user = update.effective_user
    user_id = user.id

    # Log user activity without sensitive data
    logger.info(f"User {user_id} started the bot")

    welcome_message = (
        f"Hello {user.first_name}!\n\n"
        "I'm a translation bot powered by Groq AI. I can translate your text messages "
        "and transcribe voice messages to any language you prefer.\n\n"
        "Available commands:\n"
        "/start - Show this welcome message\n"
        "/setlang <language> - Set your preferred translation language\n"
        "/mylang - Show your current language preference\n"
        "/help - Show detailed help for all commands\n\n"
        "To get started:\n"
        "1. Set your language with /setlang (e.g., /setlang spanish)\n"
        "2. Send me text or voice messages and I'll translate them!\n\n"
        "Use /setlang help to see all supported languages."
    )

    await update.message.reply_text(welcome_message)


async def setlang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /setlang command - set user's preferred language."""
    user_id = update.effective_user.id

    # Check if language argument was provided
    if not context.args:
        await update.message.reply_text(
            "Please specify a language.\n\n"
            "Usage: /setlang <language>\n"
            "Example: /setlang spanish\n\n"
            "Use /setlang help to see all supported languages."
        )
        return

    language = context.args[0]

    # Handle help request
    if language.lower() == "help":
        supported_list = "\n".join(f"- {lang}" for lang in sorted(SUPPORTED_LANGUAGES.keys()))
        await update.message.reply_text(
            f"Supported languages:\n\n{supported_list}\n\n"
            "Usage: /setlang <language>\n"
            "Example: /setlang french"
        )
        return

    # Validate language
    is_valid, result = validate_language(language)

    if is_valid:
        language_code = result
        user_preferences[user_id] = language_code
        logger.info(f"User {user_id} set language to {language_code}")

        await update.message.reply_text(
            f"Your preferred language has been set to {language.capitalize()} ({language_code}).\n\n"
            "Now send me any text message and I'll translate it to your preferred language!"
        )
    else:
        error_message = result
        logger.info(f"User {user_id} attempted invalid language")
        await update.message.reply_text(error_message)


async def mylang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /mylang command - show user's current language preference."""
    user_id = update.effective_user.id

    if user_id in user_preferences:
        language_code = user_preferences[user_id]
        # Find the language name from the code
        language_name = next(
            (name for name, code in SUPPORTED_LANGUAGES.items() if code == language_code),
            "Unknown"
        )

        logger.info(f"User {user_id} checked their language: {language_code}")
        await update.message.reply_text(
            f"Your current language preference: {language_name.capitalize()} ({language_code})\n\n"
            "Use /setlang <language> to change it."
        )
    else:
        logger.info(f"User {user_id} checked language but none is set")
        await update.message.reply_text(
            "You haven't set a language preference yet.\n\n"
            "Use /setlang <language> to set your preferred language.\n"
            "Example: /setlang english\n\n"
            "Use /setlang help to see all supported languages."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command - show detailed help."""
    user_id = update.effective_user.id

    logger.info(f"User {user_id} requested help")

    help_text = (
        "Translation Bot - Commands & Usage\n\n"

        "/start\n"
        "Show welcome message and basic information.\n\n"

        "/setlang <language>\n"
        "Set your preferred translation language.\n"
        "Example: /setlang spanish\n"
        "Use /setlang help to see all supported languages.\n\n"

        "/mylang\n"
        "Display your current language preference.\n"
        "Shows 'not set' if you haven't chosen a language yet.\n\n"

        "/help\n"
        "Show this detailed help message.\n\n"

        "How Translation Works:\n"
        "1. Set your preferred language with /setlang\n"
        "2. Send any text message or voice message\n"
        "3. I'll translate it to your language using Groq AI\n\n"

        "For voice messages:\n"
        "- Send a voice message in any language\n"
        "- The bot will transcribe it using Whisper large-v3\n"
        "- Then translate it to your preferred language\n"
        "- If no language is set, you'll see transcription only\n\n"

        "The bot shows both your original text/transcription and the translation "
        "so you can compare them.\n\n"

        "Powered by Groq AI:\n"
        "- Translation: Llama 3.3 70B model\n"
        "- Transcription: Whisper large-v3 model"
    )

    await update.message.reply_text(help_text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages (non-commands) - translate them."""
    user_id = update.effective_user.id
    message_text = update.message.text

    # Log activity without message content for privacy
    logger.info(f"User {user_id} sent text message for translation")

    # Check if user has set a language preference
    if user_id not in user_preferences:
        logger.info(f"User {user_id} has no language preference set")
        await update.message.reply_text(
            "Please set your preferred translation language first!\n\n"
            "Use /setlang <language> to set it.\n"
            "Example: /setlang spanish\n\n"
            "Use /setlang help to see all supported languages."
        )
        return

    # Get user's preferred language
    target_language_code = user_preferences[user_id]
    target_language_name = LANGUAGE_NAMES.get(target_language_code, target_language_code)

    # Translate the message
    success, result = await translate_text(message_text, target_language_code)

    if success:
        # Format response with original and translation
        translated_text = result
        response = (
            f"Original text:\n{message_text}\n\n"
            f"Translation to {target_language_name}:\n{translated_text}"
        )
        logger.info(f"Sent translation to user {user_id}")
    else:
        # Translation failed - show error and original text
        error_message = result
        response = (
            f"Original text:\n{message_text}\n\n"
            f"Translation failed: {error_message}"
        )
        logger.warning(f"Translation failed for user {user_id}: {error_message}")

    await update.message.reply_text(response)


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages - transcribe and optionally translate them."""
    user_id = update.effective_user.id
    voice = update.message.voice

    # Log activity without sensitive data
    logger.info(f"User {user_id} sent voice message (duration: {voice.duration}s, size: {voice.file_size} bytes)")

    # Check voice message duration
    if voice.duration < 1:
        await update.message.reply_text(
            "Voice message is too short. Please send a longer message."
        )
        return

    # Check file size (Telegram max is 20MB, but we'll be more conservative)
    max_size = 20 * 1024 * 1024  # 20MB
    if voice.file_size > max_size:
        await update.message.reply_text(
            f"Voice message is too large ({voice.file_size / (1024*1024):.1f}MB).\n"
            f"Maximum supported size is {max_size / (1024*1024):.0f}MB."
        )
        return

    # Show typing indicator while processing
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Use temporary file for voice message
    temp_file = None
    try:
        # Download voice file to temporary location with timeout
        logger.info(f"Downloading voice file for user {user_id}...")
        file = await voice.get_file()

        # Create temporary file with .ogg extension (Telegram voice format)
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp:
            temp_file = temp.name
            await asyncio.wait_for(
                file.download_to_drive(temp_file),
                timeout=FILE_DOWNLOAD_TIMEOUT
            )

        logger.info(f"Voice file downloaded successfully")

        # Send typing indicator again (transcription might take time)
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Transcribe the audio
        transcribe_success, transcribe_result = await transcribe_audio(temp_file)

        if not transcribe_success:
            # Transcription failed
            error_message = transcribe_result
            response = f"Transcription failed: {error_message}"
            logger.warning(f"Transcription failed for user {user_id}: {error_message}")
            await update.message.reply_text(response)
            return

        transcribed_text = transcribe_result
        logger.info(f"Transcription successful for user {user_id}")

        # Check if user has a language preference for translation
        if user_id in user_preferences:
            target_language_code = user_preferences[user_id]
            target_language_name = LANGUAGE_NAMES.get(target_language_code, target_language_code)

            # Send typing indicator again (translation in progress)
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

            # Translate the transcribed text
            translate_success, translate_result = await translate_text(transcribed_text, target_language_code)

            if translate_success:
                translated_text = translate_result
                response = (
                    f"Transcription:\n{transcribed_text}\n\n"
                    f"Translation to {target_language_name}:\n{translated_text}"
                )
                logger.info(f"Sent transcription and translation to user {user_id}")
            else:
                # Translation failed, show transcription only
                error_message = translate_result
                response = (
                    f"Transcription:\n{transcribed_text}\n\n"
                    f"Translation failed: {error_message}"
                )
                logger.warning(f"Translation failed for user {user_id}: {error_message}")
        else:
            # No language preference - show transcription only
            response = f"Transcription:\n{transcribed_text}\n\n" \
                      f"To get translations, set your language with /setlang <language>"
            logger.info(f"Sent transcription only to user {user_id} (no language preference)")

        await update.message.reply_text(response)

    except asyncio.TimeoutError:
        logger.error(f"Voice file download timeout for user {user_id}")
        await update.message.reply_text(
            f"Voice file download took too long (>{FILE_DOWNLOAD_TIMEOUT}s). Please try a smaller file."
        )

    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"Voice message handling failed for user {user_id} ({error_type}): {str(e)}")
        await update.message.reply_text(
            f"Failed to process voice message: {error_type}. Please try again."
        )

    finally:
        # Clean up temporary file
        if temp_file and Path(temp_file).exists():
            try:
                Path(temp_file).unlink()
                logger.debug(f"Deleted temporary file")
            except Exception as e:
                logger.error(f"Failed to delete temporary file: {e}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot."""
    logger.error(f"Update {update} caused error {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Sorry, an error occurred while processing your request. Please try again."
        )


# Global reference to application for shutdown handler
app_instance = None


def shutdown_handler(signum, frame):
    """
    Handle shutdown signals (SIGINT, SIGTERM) gracefully.
    Allows in-flight requests to complete before shutdown.
    """
    logger.warning(f"Received shutdown signal: {signum}")
    print("\n\nShutting down gracefully...")
    print("Waiting for in-flight requests to complete...")

    if app_instance:
        try:
            # Stop the bot gracefully
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(app_instance.stop())
                loop.create_task(app_instance.shutdown())
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    logger.info("Bot shutdown complete")
    print("Shutdown complete. Goodbye!")
    sys.exit(0)


def main() -> None:
    """Start the bot with production configuration."""
    global groq_client, app_instance

    # Get bot token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set!")
        print("\nError: TELEGRAM_BOT_TOKEN environment variable is not set.")
        print("Please create a .env file with your bot token:")
        print("TELEGRAM_BOT_TOKEN=your_token_here\n")
        return

    if not groq_api_key:
        logger.error("GROQ_API_KEY environment variable is not set!")
        print("\nError: GROQ_API_KEY environment variable is not set.")
        print("Please add your Groq API key to the .env file:")
        print("GROQ_API_KEY=your_groq_api_key_here")
        print("\nGet your API key from: https://console.groq.com/\n")
        return

    # Register shutdown handlers for graceful shutdown
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        # Initialize Groq client
        groq_client = AsyncGroq(api_key=groq_api_key)
        logger.info("Groq client initialized successfully")

        # Create the Application
        logger.info("Starting Telegram Translation Bot (Phase 4 - Production Ready)...")
        application = Application.builder().token(token).build()
        app_instance = application

        # Register command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("setlang", setlang_command))
        application.add_handler(CommandHandler("mylang", mylang_command))
        application.add_handler(CommandHandler("help", help_command))

        # Register message handlers
        # Voice messages are handled first (before text handler)
        application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
        # Text messages (non-command)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Register error handler
        application.add_error_handler(error_handler)

        # Start the bot
        logger.info("Bot is running in production mode. Press Ctrl+C to stop.")
        print("\n" + "="*60)
        print("  Telegram Translation Bot - Production Ready")
        print("="*60)
        print(f"  Log Level: {log_level}")
        print(f"  Translation Timeout: {TRANSLATION_TIMEOUT}s")
        print(f"  Transcription Timeout: {TRANSCRIPTION_TIMEOUT}s")
        print(f"  Max Retries: {MAX_RETRIES}")
        print("="*60)
        print("\nBot is running successfully!")
        print("Send text or voice messages to translate.")
        print("Press Ctrl+C to stop gracefully.\n")

        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        print("\n\nShutting down...")

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"\nError starting bot: {e}")
        print("Please check your TELEGRAM_BOT_TOKEN and try again.\n")


if __name__ == "__main__":
    main()
