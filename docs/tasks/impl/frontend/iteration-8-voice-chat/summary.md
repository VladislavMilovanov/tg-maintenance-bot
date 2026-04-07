# Итерация 08: Голосовой режим чата — итоги

## Что реализовано

### Web — голосовой ввод (Web Speech API)

**`frontend/src/components/chat/voice-input-button.tsx`** — новый компонент:
- Использует браузерный `window.SpeechRecognition` / `window.webkitSpeechRecognition`
- Язык распознавания: `ru-RU`
- Режим: `continuous = false`, `interimResults = false` (финальный транскрипт по завершении фразы)
- Состояния: запись активна (кнопка Stop с `animate-pulse`, `variant="destructive"`) / неактивна (кнопка Mic)
- Graceful degradation: если браузер не поддерживает API — кнопка отображается disabled с подсказкой, компонент не падает
- SSR-безопасность: проверка `typeof window === "undefined"` в `lazy initial state`

**`frontend/src/types/speech-recognition.d.ts`** — TypeScript-декларации:
- Полные типы для `SpeechRecognition`, `SpeechRecognitionEvent`, `SpeechRecognitionErrorEvent`, `SpeechRecognitionResult` и пр.
- Расширение `Window` через `interface Window { SpeechRecognition, webkitSpeechRecognition }`
- Позволяет использовать Web Speech API без `@types/dom-speech-recognition`

**`frontend/src/components/chat/chat-input.tsx`** — обновление:
- Добавлен импорт `VoiceInputButton`
- Кнопка голосового ввода размещена между полем ввода и кнопкой отправки
- `onTranscript` вставляет транскрипт в поле ввода (с пробелом, если поле непустое)
- После вставки фокус возвращается на поле ввода

### Telegram bot — голосовые сообщения (Whisper STT)

**`src/maintenance_bot/handlers/chat.py`** — обновление:
- Добавлен обработчик `handle_voice_message` с фильтром `@router.message(F.voice)`
- Функция `transcribe_voice(voice_bytes, settings)`:
  - Скачивает голосовой файл `.ogg` из Telegram через `bot.get_file` + `bot.download_file`
  - Использует `SpooledTemporaryFile` для экономии памяти
  - Отправляет bytes в `openai.AsyncOpenAI.audio.transcriptions.create` (модель `whisper-1`, язык `ru`)
- Транскрипт передаётся в `backend_client.create_assistant_message` — тот же путь, что и текст
- Graceful degradation: если `OPENAI_API_KEY` не задан — информационное сообщение пользователю, бот продолжает работу
- Все исключения перехватываются с понятным сообщением пользователю

**`src/maintenance_bot/config.py`** — обновление:
- Новые поля `Settings`: `OPENAI_API_KEY: str | None`, `OPENAI_BASE_URL: str`, `WHISPER_MODEL: str`
- По умолчанию `OPENAI_BASE_URL = "https://openrouter.ai/api/v1"`, `WHISPER_MODEL = "whisper-1"`

### Документация

**`docs/integrations.md`** — обновление:
- Добавлен раздел «Голосовой ввод (Voice Chat)» с таблицей каналов (Web Speech API vs Whisper)
- Описана конфигурация `.env` для Telegram-бота
- Описано поведение при отсутствии `OPENAI_API_KEY`

## Файлы, созданные / изменённые

| Файл | Действие |
|---|---|
| `frontend/src/components/chat/voice-input-button.tsx` | создан |
| `frontend/src/types/speech-recognition.d.ts` | создан |
| `frontend/src/components/chat/chat-input.tsx` | изменён (интеграция VoiceInputButton) |
| `src/maintenance_bot/handlers/chat.py` | изменён (голосовой обработчик + transcribe_voice) |
| `src/maintenance_bot/config.py` | изменён (OPENAI_API_KEY, OPENAI_BASE_URL, WHISPER_MODEL) |
| `docs/integrations.md` | изменён (раздел Voice Chat) |

## Результаты верификации

### Frontend build
```
✓ Compiled successfully in 3.6s
✓ Finished TypeScript in 3.2s
✓ Generating static pages (8/8)
```
**Статус: PASSED**

### Frontend lint (ESLint)
```
> eslint
(нет ошибок)
```
**Статус: PASSED**

### TypeScript check (tsc --noEmit)
```
(нет ошибок)
```
**Статус: PASSED**

### Backend tests
```
60 passed in 0.78s
```
**Статус: PASSED**

### Bot tests
```
5 passed in 2.46s
```
**Статус: PASSED**

## Definition of Done

- [x] Кнопка голосового ввода присутствует в компонентах чата
- [x] Голосовой ввод корректно транскрибируется и отправляется как текстовый запрос
- [x] Telegram-бот принимает голосовые сообщения и возвращает ответ
- [x] `docs/integrations.md` обновлён с описанием голосового режима
- [x] Все проверки (build, lint, tsc, tests) пройдены без ошибок
