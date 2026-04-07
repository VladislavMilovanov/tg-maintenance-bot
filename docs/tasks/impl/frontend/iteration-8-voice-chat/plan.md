# Итерация 08: Голосовой режим чата — план

## Цель

Добавить голосовой ввод в чат двух каналов — web-клиента и Telegram-бота — и задокументировать новую интеграцию в `docs/integrations.md`.

## Состав работ

### Web — голосовой ввод (Web Speech API)

- Реализовать компонент `voice-input-button.tsx` с использованием браузерного `window.SpeechRecognition` / `window.webkitSpeechRecognition`
- Добавить TypeScript-декларации для Web Speech API (`src/types/speech-recognition.d.ts`)
- Интегрировать кнопку голосового ввода в `chat-input.tsx` рядом с полем ввода
- Транскрибированный текст вставляется в поле ввода — далее стандартный путь через `POST /api/v1/assistant/messages`
- Graceful degradation: кнопка отображается в неактивном состоянии, если браузер не поддерживает Web Speech API

### Telegram bot — голосовые сообщения (Whisper STT)

- Добавить обработчик `handle_voice_message` в `src/maintenance_bot/handlers/chat.py` с фильтром `F.voice`
- Функция `transcribe_voice`: скачивает `.ogg`-файл из Telegram, отправляет в OpenAI Whisper API (`whisper-1`) для транскрипции (язык `ru`)
- Транскрипт передаётся в `backend_client.create_assistant_message` — тот же путь, что и текст
- Новые параметры конфигурации в `config.py`: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `WHISPER_MODEL`
- Graceful degradation: если `OPENAI_API_KEY` не задан, бот отвечает информационным сообщением и продолжает работу

### Документация

- Обновить `docs/integrations.md`: добавить раздел «Голосовой ввод (Voice Chat)» с таблицей каналов и описанием конфигурации

## Технические решения

| Аспект | Решение |
|---|---|
| Web STT | Браузерный Web Speech API — нулевые затраты, не требует backend-вызова |
| Telegram STT | OpenAI Whisper API через OpenRouter (или прямой OpenAI) — поддерживает `.ogg` |
| Общий путь к ассистенту | Транскрибированный текст идёт через `POST /api/v1/assistant/messages` — изменений backend не требуется |
| Отказоустойчивость | Оба канала имеют fallback без паники и без прерывания остальной функциональности |

## Артефакты

- `frontend/src/components/chat/voice-input-button.tsx`
- `frontend/src/types/speech-recognition.d.ts`
- `frontend/src/components/chat/chat-input.tsx` (обновление)
- `src/maintenance_bot/handlers/chat.py` (обновление)
- `src/maintenance_bot/config.py` (обновление)
- `docs/integrations.md` (обновление)
