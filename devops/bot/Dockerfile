FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

WORKDIR /app

RUN python -m venv "$VIRTUAL_ENV"

COPY pyproject.toml ./
COPY src ./src
COPY backend/src ./backend/src

RUN pip install --upgrade pip && pip install .

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

WORKDIR /app

RUN useradd --create-home --home-dir /home/appuser --shell /usr/sbin/nologin appuser

COPY --from=builder /opt/venv /opt/venv

USER appuser

CMD ["python", "-m", "maintenance_bot"]

