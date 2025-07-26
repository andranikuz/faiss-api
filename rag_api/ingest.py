import json, os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from .models import Message
from typing import List

# Создаем единственный экземпляр эмбеддингов для переиспользования
embeddings = OpenAIEmbeddings()

def save_messages(chat_id: str, messages: List[Message]):
    os.makedirs("data", exist_ok=True)
    path = f"data/messages_{chat_id}.jsonl"
    
    with open(path, "w", encoding="utf-8") as f:
        for msg in messages:
            f.write(json.dumps(msg.dict(), ensure_ascii=False) + "\n")

def ingest_chat(chat_id: str):
    path = f"data/messages_{chat_id}.jsonl"
    if not os.path.exists(path):
        raise FileNotFoundError(f"No chat file: {path}")
    docs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = json.loads(line)
            content = m["text"]
            docs.append(Document(page_content=content, metadata=m))
    
    os.makedirs("index", exist_ok=True)
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(f"index/{chat_id}")
