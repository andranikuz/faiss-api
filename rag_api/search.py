import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from .models import SearchResult
from .config import INDEX_DIR

# Создаем единственный экземпляр эмбеддингов для переиспользования
embeddings = OpenAIEmbeddings()

def search(chat_id: str, query: str, k: int = 5) -> list[SearchResult]:
    db = FAISS.load_local(
	    os.path.join(INDEX_DIR, chat_id),
	    embeddings,
	    allow_dangerous_deserialization=True
	)
    results = db.similarity_search(query, k=k)
    search_results = []
    for doc in results:
        result = SearchResult(
            id=doc.metadata["id"],
            username=doc.metadata["username"],
            alias=doc.metadata.get("alias", ""),
            text=doc.metadata["text"],
            timestamp=doc.metadata["timestamp"]
        )
        # Add user_id to result if available
        if "user_id" in doc.metadata:
            result.user_id = doc.metadata["user_id"]
        search_results.append(result)
    return search_results
