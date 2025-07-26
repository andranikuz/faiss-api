# FAISS API

RAG API для семантического поиска в сообщениях чата.

## Архитектура хранения

Все данные хранятся в едином каталоге `storage` с структурой:
```
storage/
├── data/          # JSONL файлы с сообщениями
│   ├── messages_123.jsonl
│   └── messages_456.jsonl
└── index/         # FAISS индексы
    ├── 123/
    └── 456/
```

## Deployment

### 1. Deploy to Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login to Fly
fly auth login

# Create app (первый раз)
fly apps create faiss-api

# Set secrets
fly secrets set OPENAI_API_KEY="your-openai-key"
fly secrets set API_TOKEN="your-secret-token"

# Create volume for persistent storage (первый раз)
fly volumes create faiss_storage --size 1 --region ams

# Deploy
fly deploy
```

### 2. Docker Image для других проектов

#### Использование готового образа:
```bash
# Pull from Docker Hub
docker pull andranikuz/faiss-api:latest

# Run locally
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  -e API_TOKEN="your-token" \
  -e STORAGE_DIR="/app/storage" \
  -v $(pwd)/storage:/app/storage \
  andranikuz/faiss-api:latest

# Or use docker-compose
cp docker-compose.example.yml docker-compose.yml
# Edit .env file with your keys
docker-compose up -d
```

#### Сборка собственного образа:
```bash
# Build and push to Docker Hub
make login    # Login to Docker Hub
make push     # Build and push latest
make release  # Build and push with version tag

# Other commands
make build    # Build locally only
make run      # Run locally for testing
make buildx   # Build for multiple platforms
make help     # Show all commands
```

### Использование в docker-compose

```yaml
services:
  faiss-api:
    image: faiss-api:latest
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - API_TOKEN=${API_TOKEN}
      - STORAGE_DIR=/app/storage
    volumes:
      - ./storage:/app/storage  # Единый volume для данных и индексов
    ports:
      - "8000:8000"
```

## API Endpoints

Все эндпоинты требуют авторизацию: `Authorization: Bearer YOUR_API_TOKEN`

- `POST /search` - Поиск сообщений
- `POST /analyze` - Поиск + анализ через GPT
- `POST /ingest_messages` - Добавление новых сообщений (избегает дубликатов)

### Структура сообщения

Поддерживаются следующие поля для отслеживания структуры Telegram-чатов:

```json
{
  "id": 1,
  "username": "andranikuz", 
  "alias": "Андраник",
  "text": "Я думаю, что мы делаем классный бот",
  "timestamp": "2024-07-25T18:32:00Z",
  "user_id": "u123",
  "message_id": 456,
  "message_thread_id": 22,
  "reply_to_message_id": 455,
  "chat_id": "chat_123"
}
```

**Поля сообщения:**
- `timestamp` - время создания (ISO8601 UTC). Если не указано - используется текущее время
- `message_id` - ID сообщения от Telegram API
- `message_thread_id` - ID треда в супергруппе
- `reply_to_message_id` - ID сообщения, на которое дан ответ
- `chat_id` - ID чата/супергруппы/канала

**Форматы timestamp:**
- ISO8601: `"2024-07-25T18:32:00Z"` (рекомендуется)
- Unix timestamp: `1721911200`
- Если не указан - автоматически устанавливается текущее время UTC

### Фильтрация по времени

Можно фильтровать сообщения по времени с помощью параметра `after_timestamp`:

**Поиск сообщений после определенной даты:**
```json
POST /search
{
  "chat_id": "123",
  "query": "обсуждение проекта",
  "k": 10,
  "after_timestamp": "2024-07-25T00:00:00Z"
}
```

**Анализ только недавних сообщений:**
```json
POST /analyze
{
  "chat_id": "123", 
  "query": "Как изменилось настроение пользователей?",
  "user_id": "u123",
  "max_messages": 50,
  "after_timestamp": 1721865600
}
```

**Поддерживаемые форматы для after_timestamp:**
- ISO8601: `"2024-07-25T00:00:00Z"`
- Unix timestamp: `1721865600`

## Environment Variables

- `OPENAI_API_KEY` - API ключ OpenAI
- `API_TOKEN` - Токен для авторизации запросов
- `STORAGE_DIR` - Путь к директории хранения (по умолчанию `/app/storage`)