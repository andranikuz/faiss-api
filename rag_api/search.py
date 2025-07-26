from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from .models import SearchResult

# Создаем единственный экземпляр эмбеддингов для переиспользования
embeddings = OpenAIEmbeddings()

def search(chat_id: str, query: str, k: int = 5) -> list[SearchResult]:
    db = FAISS.load_local(
	    f"index/{chat_id}",
	    embeddings,
	    allow_dangerous_deserialization=True
	)
    results = db.similarity_search(query, k=k)
    return [
    SearchResult(
	        id=doc.metadata["id"],
	        username=doc.metadata["username"],
	        alias=doc.metadata.get("alias", ""),
	        text=doc.metadata["text"],
	        timestamp=doc.metadata["timestamp"]
	    )
	    for doc in results
	]
