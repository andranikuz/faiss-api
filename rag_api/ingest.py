import json, os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from .models import Message
from .config import DATA_DIR, INDEX_DIR
from typing import List

# Создаем единственный экземпляр эмбеддингов для переиспользования
embeddings = OpenAIEmbeddings()

def save_messages(chat_id: str, messages: List[Message]):
    from .config import ensure_directories
    ensure_directories()
    
    path = os.path.join(DATA_DIR, f"messages_{chat_id}.jsonl")
    
    with open(path, "w", encoding="utf-8") as f:
        for msg in messages:
            f.write(json.dumps(msg.dict(), ensure_ascii=False) + "\n")

def ingest_chat(chat_id: str):
    from .config import ensure_directories
    ensure_directories()
    
    path = os.path.join(DATA_DIR, f"messages_{chat_id}.jsonl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No chat file: {path}")
    docs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = json.loads(line)
            # Include alias and user_id in page_content for better search
            user_id = m.get("user_id", m.get("username", "unknown"))
            content = f"{m.get('alias', m.get('username', 'Unknown'))} ({user_id}): {m['text']}"
            # Add user_id to metadata if not present
            if "user_id" not in m:
                m["user_id"] = user_id
            docs.append(Document(page_content=content, metadata=m))
    
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(os.path.join(INDEX_DIR, chat_id))
