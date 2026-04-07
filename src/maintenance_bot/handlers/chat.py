"""Обработчик текстовых и голосовых сообщений."""

import io
import logging
import tempfile

from aiogram import Bot, F, Router
from aiogram.types import Message

from maintenance_bot.backend_client import BackendApiError, BackendClient
from maintenance_bot.config import Settings

logger = logging.getLogger(__name__)

router = Router(name="chat")

USER_FACING_BACKEND_ERROR = "Сервис временно недоступен. Попробуйте позже."
USER_FACING_VOICE_ERROR = "Не удалось распознать голосовое сообщение. Попробуйте ещё раз или напишите текстом."
USER_FACING_NO_VOICE_KEY = (
    "Голосовые сообщения недоступны: не настроен API-ключ для распознавания речи."
)


async def transcribe_voice(voice_bytes: bytes, settings: Settings) -> str:
    """Transcribe OGG voice bytes to text using Whisper API."""
    try:
        import openai  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError("openai package is not installed") from exc

    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not configured")

    client = openai.AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )

    audio_file = io.BytesIO(voice_bytes)
    audio_file.name = "voice.ogg"

    transcription = await client.audio.transcriptions.create(
        model=settings.WHISPER_MODEL,
        file=audio_file,
        language="ru",
    )
    return transcription.text.strip()


@router.message(F.voice)
async def handle_voice_message(
    message: Message,
    bot: Bot,
    backend_client: BackendClient,
    settings: Settings,
) -> None:
    """Обработка голосового сообщения: транскрибация + ответ ассистента."""
    if not message.from_user or not message.voice:
        return

    if not settings.OPENAI_API_KEY:
        await message.answer(USER_FACING_NO_VOICE_KEY)
        return

    user_id = message.from_user.id
    logger.info(
        "Голосовое сообщение от user_id=%s, duration=%ds",
        user_id,
        message.voice.duration,
    )

    # Download voice file from Telegram
    try:
        file_info = await bot.get_file(message.voice.file_id)
        with tempfile.SpooledTemporaryFile(max_size=10 * 1024 * 1024) as tmp:
            await bot.download_file(file_info.file_path, destination=tmp)  # type: ignore[arg-type]
            tmp.seek(0)
            voice_bytes = tmp.read()
    except Exception:
        logger.exception("Failed to download voice file for user_id=%s", user_id)
        await message.answer(USER_FACING_VOICE_ERROR)
        return

    # Transcribe
    try:
        text = await transcribe_voice(voice_bytes, settings)
    except Exception:
        logger.exception("Whisper transcription failed for user_id=%s", user_id)
        await message.answer(USER_FACING_VOICE_ERROR)
        return

    if not text:
        await message.answer("Не удалось разобрать речь. Попробуйте говорить чётче.")
        return

    logger.info("Транскрипция для user_id=%s: %r", user_id, text[:80])

    # Send to assistant backend (same flow as text)
    try:
        response = await backend_client.create_assistant_message(
            user_id=user_id,
            text=text,
            display_name=message.from_user.full_name or message.from_user.username,
        )
        await message.answer(response.answer)
    except BackendApiError as exc:
        logger.warning(
            "Backend error for user_id=%s status_code=%s: %s",
            user_id,
            exc.status_code,
            exc.message,
        )
        await message.answer(USER_FACING_BACKEND_ERROR)
    except Exception:
        logger.exception(
            "Unexpected error while processing voice for user_id=%s", user_id
        )
        await message.answer(USER_FACING_BACKEND_ERROR)


@router.message()
async def handle_message(
    message: Message,
    backend_client: BackendClient,
) -> None:
    """Обработка текстового сообщения от пользователя."""
    if not message.text or not message.from_user:
        return

    user_id = message.from_user.id
    text = message.text.strip()

    if not text:
        return

    logger.info("Сообщение от user_id=%s, длина=%d", user_id, len(text))

    try:
        response = await backend_client.create_assistant_message(
            user_id=user_id,
            text=text,
            display_name=message.from_user.full_name or message.from_user.username,
        )
        await message.answer(response.answer)
    except BackendApiError as exc:
        logger.warning(
            "Backend error for user_id=%s status_code=%s: %s",
            user_id,
            exc.status_code,
            exc.message,
        )
        await message.answer(USER_FACING_BACKEND_ERROR)
    except Exception:
        logger.exception(
            "Unexpected error while processing message for user_id=%s", user_id
        )
        await message.answer(USER_FACING_BACKEND_ERROR)
