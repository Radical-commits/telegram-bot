"""
Telegram Translation Bot - Phase 4: Production Ready
A bot that provides real-time text translation using Groq's Llama models.
Supports voice message transcription using Whisper large-v3.
Supports multiple languages with user preference storage.
Production-ready with retry logic, rate limiting, and graceful shutdown.
"""

import asyncio
import json
import logging
import os
import re
import signal
import sys
import tempfile
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Callable, Dict, Optional, List, Any

from aiohttp import web
from dotenv import load_dotenv
from groq import AsyncGroq, RateLimitError, APIError, APIConnectionError, APITimeoutError
import httpx
import ssl
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CallbackQueryHandler,
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

# In-memory storage for trivia game state
# Format: {user_id: {questions: list, current_index: int, score: int, active: bool}}
trivia_games: Dict[int, Dict[str, Any]] = {}

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
        f"Привет, {user.first_name}!\n\n"
        "Я бот-переводчик на основе Groq AI. Я могу переводить текстовые сообщения "
        "и расшифровывать голосовые сообщения на любой выбранный вами язык.\n\n"
        "Доступные команды:\n"
        "/start - Показать это приветственное сообщение\n"
        "/setlang <язык> - Установить предпочитаемый язык перевода\n"
        "/mylang - Показать текущий выбранный язык\n"
        "/trivia - Сыграть в увлекательную игру Правда/Ложь\n"
        "/help - Показать подробную справку по всем командам\n\n"
        "Чтобы начать:\n"
        "1. Введите /setlang, чтобы выбрать язык с помощью кнопок 🔘\n"
        "2. Отправьте мне текстовое или голосовое сообщение, и я переведу его!\n"
        "3. Хотите развлечься? Попробуйте /trivia для игры!\n\n"
        "Совет: Вы также можете ввести /setlang spanish, чтобы установить язык напрямую."
    )

    await update.message.reply_text(welcome_message)


async def setlang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /setlang command - set user's preferred language."""
    user_id = update.effective_user.id

    # Check if language argument was provided
    if not context.args:
        # Show inline keyboard with language options
        keyboard = []

        # Create buttons in rows of 2
        languages_sorted = sorted(SUPPORTED_LANGUAGES.items())
        for i in range(0, len(languages_sorted), 2):
            row = []
            for lang_name, lang_code in languages_sorted[i:i+2]:
                # Use flag emojis for popular languages
                flag_emojis = {
                    "english": "🇬🇧", "spanish": "🇪🇸", "french": "🇫🇷",
                    "german": "🇩🇪", "italian": "🇮🇹", "portuguese": "🇵🇹",
                    "russian": "🇷🇺", "chinese": "🇨🇳", "japanese": "🇯🇵",
                    "korean": "🇰🇷", "arabic": "🇸🇦", "hindi": "🇮🇳"
                }
                flag = flag_emojis.get(lang_name, "🌐")
                button_text = f"{flag} {lang_name.capitalize()}"
                row.append(InlineKeyboardButton(button_text, callback_data=f"lang_{lang_code}"))
            keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🌍 *Выберите предпочитаемый язык:*\n\n"
            "Выберите из кнопок ниже, или используйте:\n"
            "`/setlang <язык>`\n\n"
            "Пример: `/setlang spanish`",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    language = context.args[0]

    # Handle help request
    if language.lower() == "help":
        supported_list = "\n".join(f"- {lang}" for lang in sorted(SUPPORTED_LANGUAGES.keys()))
        await update.message.reply_text(
            f"Поддерживаемые языки:\n\n{supported_list}\n\n"
            "Использование: /setlang <язык>\n"
            "Пример: /setlang french"
        )
        return

    # Validate language
    is_valid, result = validate_language(language)

    if is_valid:
        language_code = result
        user_preferences[user_id] = language_code
        logger.info(f"User {user_id} set language to {language_code}")

        await update.message.reply_text(
            f"Ваш предпочитаемый язык установлен на {language.capitalize()} ({language_code}).\n\n"
            "Теперь отправьте мне любое текстовое сообщение, и я переведу его на выбранный язык!"
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
            f"Ваш текущий выбранный язык: {language_name.capitalize()} ({language_code})\n\n"
            "Используйте /setlang <язык> для изменения."
        )
    else:
        logger.info(f"User {user_id} checked language but none is set")

        # Show inline keyboard for language selection
        keyboard = []
        languages_sorted = sorted(SUPPORTED_LANGUAGES.items())
        for i in range(0, len(languages_sorted), 2):
            row = []
            for lang_name, lang_code in languages_sorted[i:i+2]:
                flag_emojis = {
                    "english": "🇬🇧", "spanish": "🇪🇸", "french": "🇫🇷",
                    "german": "🇩🇪", "italian": "🇮🇹", "portuguese": "🇵🇹",
                    "russian": "🇷🇺", "chinese": "🇨🇳", "japanese": "🇯🇵",
                    "korean": "🇰🇷", "arabic": "🇸🇦", "hindi": "🇮🇳"
                }
                flag = flag_emojis.get(lang_name, "🌐")
                button_text = f"{flag} {lang_name.capitalize()}"
                row.append(InlineKeyboardButton(button_text, callback_data=f"lang_{lang_code}"))
            keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Вы еще не установили предпочитаемый язык.\n\n"
            "🌍 *Выберите ваш язык:*",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


async def button_callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route button callbacks to appropriate handlers."""
    query = update.callback_query
    callback_data = query.data

    # Route to appropriate handler based on callback data prefix
    if callback_data.startswith("lang_"):
        await language_button_callback(update, context)
    elif callback_data.startswith("trivia_"):
        await trivia_button_callback(update, context)
    else:
        await query.answer()
        logger.warning(f"Unknown callback data: {callback_data}")


async def language_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button presses for language selection."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    user_id = update.effective_user.id
    callback_data = query.data

    # Extract language code from callback data (format: lang_en, lang_es, etc.)
    if callback_data.startswith("lang_"):
        language_code = callback_data[5:]  # Remove "lang_" prefix

        # Find the language name
        language_name = next(
            (name for name, code in SUPPORTED_LANGUAGES.items() if code == language_code),
            "Unknown"
        )

        # Save user preference
        user_preferences[user_id] = language_code
        logger.info(f"User {user_id} set language to {language_code} via button")

        # Update the message to show confirmation
        await query.edit_message_text(
            f"✅ *Язык установлен на {language_name.capitalize()} ({language_code})*\n\n"
            "Теперь отправьте мне любое текстовое сообщение, и я переведу его!\n\n"
            "Используйте /setlang для изменения языка в любое время.",
            parse_mode="Markdown"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command - show detailed help."""
    user_id = update.effective_user.id

    logger.info(f"User {user_id} requested help")

    help_text = (
        "Бот-переводчик - Команды и использование\n\n"

        "/start\n"
        "Показать приветственное сообщение и основную информацию.\n\n"

        "/setlang [язык]\n"
        "Установить предпочитаемый язык перевода.\n"
        "• Просто введите /setlang, чтобы увидеть кнопки выбора языка 🔘\n"
        "• Или используйте: /setlang spanish\n"
        "• Используйте /setlang help, чтобы увидеть все поддерживаемые языки.\n\n"

        "/mylang\n"
        "Показать ваш текущий выбранный язык.\n"
        "Показывает 'не установлен', если вы еще не выбрали язык.\n\n"

        "/trivia\n"
        "Сыграть в увлекательную игру Правда/Ложь!\n"
        "• Ответьте на 10 странных и интересных фактов\n"
        "• Вопросы появляются на выбранном вами языке\n"
        "• Используйте кнопки для выбора Правда или Ложь\n"
        "• Получайте мгновенную обратную связь с объяснениями\n"
        "• Посмотрите свой финальный счет в конце\n"
        "• Играйте сколько угодно раз с новыми вопросами\n"
        "• Каждая игра генерирует совершенно новые вопросы\n\n"

        "/help\n"
        "Показать это подробное справочное сообщение.\n\n"

        "Как работает перевод:\n"
        "1. Установите предпочитаемый язык с помощью /setlang\n"
        "2. Отправьте любое текстовое или голосовое сообщение\n"
        "3. Я переведу его на ваш язык с помощью Groq AI\n\n"

        "Для голосовых сообщений:\n"
        "- Отправьте голосовое сообщение на любом языке\n"
        "- Бот расшифрует его с помощью Whisper large-v3\n"
        "- Затем переведет на ваш предпочитаемый язык\n"
        "- Если язык не установлен, вы увидите только расшифровку\n\n"

        "Бот показывает как ваш оригинальный текст/расшифровку, так и перевод, "
        "чтобы вы могли их сравнить.\n\n"

        "Работает на Groq AI:\n"
        "- Перевод: модель Llama 3.3 70B\n"
        "- Расшифровка: модель Whisper large-v3\n"
        "- Вопросы викторины: модель Llama 3.3 70B с веб-верификацией"
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
            "Пожалуйста, сначала установите предпочитаемый язык перевода!\n\n"
            "Используйте /setlang <язык> для установки.\n"
            "Пример: /setlang spanish\n\n"
            "Используйте /setlang help для просмотра всех поддерживаемых языков."
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
            f"Исходный текст:\n{message_text}\n\n"
            f"Перевод на {target_language_name}:\n{translated_text}"
        )
        logger.info(f"Sent translation to user {user_id}")
    else:
        # Translation failed - show error and original text
        error_message = result
        response = (
            f"Исходный текст:\n{message_text}\n\n"
            f"Ошибка перевода: {error_message}"
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
            "Голосовое сообщение слишком короткое. Пожалуйста, отправьте более длинное сообщение."
        )
        return

    # Check file size (Telegram max is 20MB, but we'll be more conservative)
    max_size = 20 * 1024 * 1024  # 20MB
    if voice.file_size > max_size:
        await update.message.reply_text(
            f"Голосовое сообщение слишком большое ({voice.file_size / (1024*1024):.1f}МБ).\n"
            f"Максимальный поддерживаемый размер: {max_size / (1024*1024):.0f}МБ."
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
            response = f"Ошибка расшифровки: {error_message}"
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
                    f"Расшифровка:\n{transcribed_text}\n\n"
                    f"Перевод на {target_language_name}:\n{translated_text}"
                )
                logger.info(f"Sent transcription and translation to user {user_id}")
            else:
                # Translation failed, show transcription only
                error_message = translate_result
                response = (
                    f"Расшифровка:\n{transcribed_text}\n\n"
                    f"Ошибка перевода: {error_message}"
                )
                logger.warning(f"Translation failed for user {user_id}: {error_message}")
        else:
            # No language preference - show transcription only
            response = f"Расшифровка:\n{transcribed_text}\n\n" \
                      f"Чтобы получать переводы, установите язык с помощью /setlang <язык>"
            logger.info(f"Sent transcription only to user {user_id} (no language preference)")

        await update.message.reply_text(response)

    except asyncio.TimeoutError:
        logger.error(f"Voice file download timeout for user {user_id}")
        await update.message.reply_text(
            f"Загрузка голосового файла заняла слишком много времени (>{FILE_DOWNLOAD_TIMEOUT}с). Пожалуйста, попробуйте файл меньшего размера."
        )

    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"Voice message handling failed for user {user_id} ({error_type}): {str(e)}")
        await update.message.reply_text(
            f"Не удалось обработать голосовое сообщение: {error_type}. Пожалуйста, попробуйте снова."
        )

    finally:
        # Clean up temporary file
        if temp_file and Path(temp_file).exists():
            try:
                Path(temp_file).unlink()
                logger.debug(f"Deleted temporary file")
            except Exception as e:
                logger.error(f"Failed to delete temporary file: {e}")


# ==============================================================================
# Trivia Game Functions
# ==============================================================================

@async_retry(max_retries=MAX_RETRIES)
async def verify_claim_with_search(claim: str, expected_answer: bool) -> tuple[bool, str]:
    """
    Verify a trivia claim using web search.

    Args:
        claim: The claim to verify
        expected_answer: The expected answer (True or False)

    Returns:
        Tuple of (is_verified: bool, search_summary: str)
        - On verification success: (True, brief_explanation)
        - On verification failure: (False, reason)
    """
    try:
        # Use httpx to search for verification
        # We'll use DuckDuckGo Instant Answer API (no API key needed)
        search_query = f"{claim} fact check"

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try DuckDuckGo Instant Answer API
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": search_query,
                    "format": "json",
                    "no_html": 1,
                    "skip_disambig": 1
                }
            )

            if response.status_code == 200:
                data = response.json()
                # Check if we got relevant results
                abstract = data.get("AbstractText", "")

                if abstract and len(abstract) > 20:
                    # We got some information, consider it verified
                    # Extract a brief summary (first sentence)
                    first_sentence = abstract.split('.')[0] + '.'
                    logger.info(f"Claim verified via search: {claim[:50]}")
                    return True, first_sentence[:200]

        # If search didn't return useful results, assume we can't verify
        logger.warning(f"Could not verify claim via search: {claim[:50]}")
        return False, "Could not find reliable verification"

    except Exception as e:
        logger.error(f"Search verification failed: {type(e).__name__}: {e}")
        return False, f"Search failed: {type(e).__name__}"


@async_retry(max_retries=MAX_RETRIES)
async def generate_trivia_questions(language_code: str = "en", count: int = 10) -> tuple[bool, Any]:
    """
    Generate trivia questions using Groq API in the specified language.

    Args:
        language_code: Language code (e.g., "en", "es", "fr")
        count: Number of questions to generate

    Returns:
        Tuple of (success: bool, result: list or error_message)
        - On success: (True, list_of_question_dicts)
        - On failure: (False, error_message)
    """
    if not groq_client:
        logger.error("Groq client is not initialized")
        return False, "Trivia service is not available. Please contact the administrator."

    # Get the language name for the prompt
    language_name = LANGUAGE_NAMES.get(language_code, "English")

    try:
        logger.info(f"Generating {count} trivia questions in {language_name}...")

        prompt = f"""Generate exactly {count} weird, surprising, and interesting true-or-false claims about the world.
Make them fun and engaging! Mix true and false claims (roughly 50/50 split).
Topics can include: animals, science, history, geography, technology, human body, space, food, etc.

IMPORTANT: All content must be in {language_name}. The claim, explanation, and ALL text must be written in {language_name}.

Requirements:
- Each claim should be clear and specific
- Avoid controversial or offensive topics
- Make them surprising or counterintuitive
- Include a brief (1-2 sentence) explanation for each
- Write everything in {language_name}

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "claim": "The exact claim text here (in {language_name})",
    "answer": true,
    "explanation": "Brief explanation why this is true or false (in {language_name})"
  }}
]

Return ONLY the JSON array, no other text. Remember: ALL TEXT must be in {language_name}."""

        chat_completion = await asyncio.wait_for(
            groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a trivia question generator. You create interesting true/false questions in {language_name}. You ONLY respond with valid JSON arrays. All text content must be in {language_name}."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.8,  # Higher temperature for more creative and varied questions
                max_tokens=2048,
            ),
            timeout=30
        )

        response_text = chat_completion.choices[0].message.content.strip()
        logger.debug(f"Groq response: {response_text[:200]}")

        # Extract JSON from response (in case there's extra text)
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
        else:
            json_text = response_text

        # Parse JSON
        questions = json.loads(json_text)

        # Validate structure
        if not isinstance(questions, list) or len(questions) == 0:
            logger.error("Invalid questions format: not a list or empty")
            return False, "Generated questions have invalid format"

        # Validate each question
        validated_questions = []
        for q in questions:
            if isinstance(q, dict) and "claim" in q and "answer" in q and "explanation" in q:
                validated_questions.append(q)

        if len(validated_questions) < count:
            logger.warning(f"Only {len(validated_questions)} valid questions out of {count}")

        logger.info(f"Successfully generated {len(validated_questions)} trivia questions in {language_name}")
        return True, validated_questions

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse trivia questions JSON: {e}")
        logger.error(f"Response was: {response_text[:500]}")
        return False, "Failed to parse generated questions"

    except asyncio.TimeoutError:
        logger.error("Trivia generation timeout")
        return False, "Question generation took too long. Please try again."

    except RateLimitError as e:
        logger.warning(f"Trivia generation rate limit: {e}")
        return False, "Trivia service is busy. Please wait a moment and try again."

    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"Trivia generation failed ({error_type}): {str(e)}")
        return False, f"Failed to generate questions: {error_type}"


async def send_trivia_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """
    Send the current trivia question to the user.

    Args:
        update: Telegram update object
        context: Telegram context
        user_id: User ID
    """
    game_state = trivia_games.get(user_id)

    if not game_state or not game_state.get("active"):
        logger.warning(f"No active game for user {user_id}")
        return

    questions = game_state["questions"]
    current_index = game_state["current_index"]
    score = game_state["score"]

    if current_index >= len(questions):
        # Game over
        await end_trivia_game(update, context, user_id)
        return

    question = questions[current_index]
    question_number = current_index + 1
    total_questions = len(questions)

    # Create inline keyboard with True/False buttons
    keyboard = [
        [
            InlineKeyboardButton("✓ Правда", callback_data=f"trivia_true_{current_index}"),
            InlineKeyboardButton("✗ Ложь", callback_data=f"trivia_false_{current_index}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    question_text = (
        f"*Question {question_number}/{total_questions}*\n\n"
        f"{question['claim']}\n\n"
        f"_Current score: {score}/{question_number - 1}_" if question_number > 1 else f"*Question {question_number}/{total_questions}*\n\n{question['claim']}"
    )

    # Send question
    if update.callback_query:
        await update.callback_query.message.reply_text(
            question_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            question_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


async def end_trivia_game(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """
    End the trivia game and show final score.

    Args:
        update: Telegram update object
        context: Telegram context
        user_id: User ID
    """
    game_state = trivia_games.get(user_id)

    if not game_state:
        return

    score = game_state["score"]
    total = len(game_state["questions"])

    # Generate encouraging message based on score
    percentage = (score / total) * 100

    if percentage == 100:
        message = "Идеальный результат! Вы мастер викторины!"
    elif percentage >= 80:
        message = "Отличная работа! Вы действительно знаете факты!"
    elif percentage >= 60:
        message = "Хорошая работа! Вы справились!"
    elif percentage >= 40:
        message = "Неплохо! Продолжайте учиться!"
    else:
        message = "Хорошая попытка! Сыграйте снова, чтобы улучшить свой результат!"

    final_text = (
        f"🎮 *Игра окончена!*\n\n"
        f"*Итоговый счет: {score} из {total}*\n"
        f"({percentage:.0f}%)\n\n"
        f"{message}\n\n"
        f"Хотите сыграть снова? Используйте /trivia для начала новой игры с другими вопросами!"
    )

    # Clean up game state
    trivia_games.pop(user_id, None)
    logger.info(f"Trivia game ended for user {user_id}. Score: {score}/{total}")

    # Send final message
    if update.callback_query:
        await update.callback_query.message.reply_text(
            final_text,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            final_text,
            parse_mode="Markdown"
        )


async def trivia_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /trivia command - start a new trivia game."""
    user_id = update.effective_user.id

    logger.info(f"User {user_id} started trivia game")

    # Get user's language preference (default to English)
    language_code = user_preferences.get(user_id, "en")
    language_name = LANGUAGE_NAMES.get(language_code, "English")

    # Check if user already has an active game
    if user_id in trivia_games and trivia_games[user_id].get("active"):
        await update.message.reply_text(
            "У вас уже есть активная игра в викторину!\n\n"
            "Сначала завершите текущую игру, или используйте /trivia снова, чтобы начать новую игру "
            "(это отменит текущую игру)."
        )
        # Clean up old game
        trivia_games.pop(user_id, None)

    # Send "generating questions" message with language info
    generating_msg = await update.message.reply_text(
        f"🎮 *Запуск игры в викторину ({language_name})!*\n\n"
        "Генерируем для вас 10 странных и интересных вопросов...\n"
        "_Это может занять немного времени..._",
        parse_mode="Markdown"
    )

    # Generate questions in user's language
    success, result = await generate_trivia_questions(language_code=language_code, count=10)

    if not success:
        error_message = result
        await generating_msg.edit_text(
            f"❌ Не удалось начать игру в викторину:\n{error_message}\n\n"
            "Пожалуйста, попробуйте снова с помощью /trivia"
        )
        return

    questions = result

    # Make sure we have at least 10 questions
    if len(questions) < 10:
        await generating_msg.edit_text(
            f"❌ Не удалось сгенерировать достаточно вопросов (получено только {len(questions)}).\n\n"
            "Пожалуйста, попробуйте снова с помощью /trivia"
        )
        return

    # Initialize game state
    trivia_games[user_id] = {
        "questions": questions[:10],  # Use exactly 10 questions
        "current_index": 0,
        "score": 0,
        "active": True,
        "language_code": language_code  # Store language for potential future use
    }

    logger.info(f"Trivia game initialized for user {user_id} with {len(questions[:10])} questions in {language_name}")

    # Delete generating message
    await generating_msg.delete()

    # Send welcome message
    await update.message.reply_text(
        f"🎮 *Игра в викторину началась ({language_name})!*\n\n"
        "Ответьте на 10 вопросов Правда/Ложь.\n"
        "Вы получите мгновенную обратную связь после каждого ответа.\n\n"
        "Давайте начнем!",
        parse_mode="Markdown"
    )

    # Send first question
    await send_trivia_question(update, context, user_id)


async def trivia_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle True/False button presses in trivia game."""
    query = update.callback_query
    await query.answer()  # Acknowledge button press

    user_id = update.effective_user.id
    callback_data = query.data

    # Check if this is a trivia callback
    if not callback_data.startswith("trivia_"):
        return

    # Check if user has an active game
    if user_id not in trivia_games or not trivia_games[user_id].get("active"):
        await query.edit_message_text(
            "❌ Эта игра истекла или уже была завершена.\n\n"
            "Используйте /trivia, чтобы начать новую игру!"
        )
        return

    game_state = trivia_games[user_id]

    # Parse callback data: trivia_true_0 or trivia_false_0
    parts = callback_data.split("_")
    user_answer = parts[1] == "true"  # true or false
    question_index = int(parts[2])

    # Verify this is the current question (prevent double-answering)
    if question_index != game_state["current_index"]:
        await query.edit_message_text(
            "❌ На этот вопрос уже был дан ответ.\n\n"
            "Пожалуйста, подождите следующий вопрос..."
        )
        return

    questions = game_state["questions"]
    current_question = questions[question_index]
    correct_answer = current_question["answer"]
    explanation = current_question["explanation"]

    # Check if answer is correct
    is_correct = (user_answer == correct_answer)

    if is_correct:
        game_state["score"] += 1
        result_emoji = "✅"
        result_text = "Правильно!"
    else:
        result_emoji = "❌"
        answer_text = "Правда" if correct_answer else "Ложь"
        result_text = f"Неправильно! Правильный ответ: {answer_text}."

    # Update current index
    game_state["current_index"] += 1

    score = game_state["score"]
    question_number = question_index + 1
    total_questions = len(questions)

    # Build response message
    response_text = (
        f"{result_emoji} *{result_text}*\n\n"
        f"_{explanation}_\n\n"
        f"Счет: {score}/{question_number}"
    )

    # Update the message with result
    await query.edit_message_text(
        response_text,
        parse_mode="Markdown"
    )

    logger.info(f"User {user_id} answered question {question_number}: {'correct' if is_correct else 'wrong'}")

    # Send next question after a brief pause
    await asyncio.sleep(1.5)

    if game_state["current_index"] < total_questions:
        # More questions to go
        await send_trivia_question(update, context, user_id)
    else:
        # Game over
        await end_trivia_game(update, context, user_id)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot."""
    logger.error(f"Update {update} caused error {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Извините, произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова."
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


# ==============================================================================
# Health Check Server (keeps Render.com free tier awake)
# ==============================================================================

# Track bot start time for uptime reporting
bot_start_time = datetime.now()

async def health_check(request):
    """Health check endpoint for monitoring and keeping Render awake."""
    uptime = datetime.now() - bot_start_time
    uptime_seconds = int(uptime.total_seconds())

    return web.json_response({
        "status": "ok",
        "bot": "telegram-translation-bot",
        "uptime_seconds": uptime_seconds,
        "uptime": str(uptime).split('.')[0],  # Format: HH:MM:SS
        "timestamp": datetime.now().isoformat(),
        "message": "Bot is running"
    })

async def root_handler(request):
    """Root endpoint with bot information."""
    return web.Response(text=(
        "🤖 Telegram Translation Bot\n"
        "Status: Running\n"
        "\n"
        "Endpoints:\n"
        "  GET /health - Health check (JSON)\n"
        "  GET / - This page\n"
    ))

async def start_health_server(port: int = 8080):
    """Start the health check HTTP server."""
    app = web.Application()
    app.router.add_get('/', root_handler)
    app.router.add_get('/health', health_check)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    logger.info(f"Health check server started on port {port}")
    print(f"Health check server: http://0.0.0.0:{port}/health")


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
        # Check if SSL verification should be disabled (for testing in corporate networks)
        disable_ssl = os.getenv("DISABLE_SSL_VERIFY", "false").lower() == "true"

        if disable_ssl:
            logger.warning("⚠️  SSL verification is DISABLED - only use for testing!")
            # Create custom httpx client with SSL verification disabled
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            http_client = httpx.AsyncClient(verify=ssl_context)
            groq_client = AsyncGroq(api_key=groq_api_key, http_client=http_client)
            logger.info("Groq client initialized (SSL verification disabled)")
        else:
            groq_client = AsyncGroq(api_key=groq_api_key)
            logger.info("Groq client initialized successfully")

        # Create the Application
        logger.info("Starting Telegram Translation Bot (Phase 4 - Production Ready)...")

        # Get port for health check server (Render provides PORT env var)
        port = int(os.getenv("PORT", "8080"))

        # Create application with post_init callback for health server
        async def post_init_callback(app):
            """Start health check server after bot initialization."""
            await start_health_server(port)

        application = Application.builder().token(token).post_init(post_init_callback).build()
        app_instance = application

        # Register command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("setlang", setlang_command))
        application.add_handler(CommandHandler("mylang", mylang_command))
        application.add_handler(CommandHandler("trivia", trivia_command))
        application.add_handler(CommandHandler("help", help_command))

        # Register callback handler for inline keyboard buttons (routes to specific handlers)
        application.add_handler(CallbackQueryHandler(button_callback_router))

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
        print(f"  Health Check Port: {port}")
        print("="*60)
        print("\nBot is running successfully!")
        print("Send text or voice messages to translate.")
        print(f"Health check endpoint: http://0.0.0.0:{port}/health")
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
