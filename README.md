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

```bash
# Build image
docker build -t faiss-api:latest .

# Run locally
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  -e API_TOKEN="your-token" \
  -e STORAGE_DIR="/app/storage" \
  -v $(pwd)/storage:/app/storage \
  faiss-api:latest

# Or use docker-compose
cp docker-compose.example.yml docker-compose.yml
# Edit .env file with your keys
docker-compose up -d
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
- `POST /ingest_messages` - Загрузка новых сообщений

## Environment Variables

- `OPENAI_API_KEY` - API ключ OpenAI
- `API_TOKEN` - Токен для авторизации запросов
- `STORAGE_DIR` - Путь к директории хранения (по умолчанию `/app/storage`)