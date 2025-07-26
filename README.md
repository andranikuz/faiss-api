# FAISS API

RAG API для семантического поиска в сообщениях чата.

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

# Deploy
fly deploy

# Create volume for persistent storage (первый раз)
fly volumes create faiss_data --size 1 --region ams
```

### 2. Docker Image для других проектов

```bash
# Build image
docker build -t faiss-api:latest .

# Run locally
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  -e API_TOKEN="your-token" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/index:/app/index \
  faiss-api:latest

# Or use docker-compose
cp docker-compose.example.yml docker-compose.yml
# Edit .env file with your keys
docker-compose up -d
```

## API Endpoints

Все эндпоинты требуют авторизацию: `Authorization: Bearer YOUR_API_TOKEN`

- `POST /search` - Поиск сообщений
- `POST /analyze` - Поиск + анализ через GPT
- `POST /ingest_messages` - Загрузка новых сообщений