"""Logging configuration for backend service."""

import json
import logging
import sys
from typing import Any


def configure_logging(level_name: str) -> None:
    """Configure root logging once for local backend runs."""

    logging.basicConfig(
        level=getattr(logging, level_name.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
        force=True,
    )


def extract_chat_id(request_body: bytes) -> str | None:
    """Extract Telegram chat_id-like value from supported request payloads."""

    if not request_body:
        return None

    try:
        payload = json.loads(request_body)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    for container_name in ("user", "author"):
        container = payload.get(container_name)
        if not isinstance(container, dict):
            continue
        external_id = container.get("external_id")
        chat_id = _parse_telegram_external_id(external_id)
        if chat_id is not None:
            return chat_id
    return None


def build_request_log_message(
    *,
    method: str,
    path: str,
    status_code: int,
    request_body: bytes,
    response_size: int,
) -> str:
    """Build a privacy-safe request log line without user message contents."""

    chat_id = extract_chat_id(request_body)
    parts = [
        "Handled request",
        f"method={method}",
        f"path={path}",
        f"status_code={status_code}",
    ]
    if chat_id is not None:
        parts.append(f"chat_id={chat_id}")
    parts.append(f"request_bytes={len(request_body)}")
    parts.append(f"response_bytes={response_size}")
    return " ".join(parts)


def _parse_telegram_external_id(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    prefix = "telegram:"
    if not value.startswith(prefix):
        return None
    chat_id = value[len(prefix) :].strip()
    return chat_id or None
