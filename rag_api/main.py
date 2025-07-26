from fastapi import FastAPI, HTTPException, Depends
from dotenv import load_dotenv
from .models import SearchRequest, SearchResponse, AnalyzeRequest, AnalyzeResponse, IngestRequest, IngestResponse
from .search import search
from .analyze import analyze_messages
from .ingest import ingest_chat, save_messages
from .auth import verify_token
from .config import INDEX_DIR
import os

load_dotenv()
app = FastAPI()

@app.post("/search", response_model=SearchResponse)
def search_messages(req: SearchRequest, token: str = Depends(verify_token)):
    try:
        if not os.path.exists(os.path.join(INDEX_DIR, req.chat_id)):
            raise HTTPException(status_code=404, detail=f"Index for chat_id {req.chat_id} not found")
        results = search(req.chat_id, req.query, req.k, req.after_timestamp, req.enhance_query)
        return SearchResponse(results=results)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest, token: str = Depends(verify_token)):
    try:
        # Validate max_messages
        if req.max_messages > 1000:
            raise HTTPException(status_code=400, detail="max_messages cannot exceed 1000")
        if req.max_messages < 1:
            raise HTTPException(status_code=400, detail="max_messages must be at least 1")
            
        if not os.path.exists(os.path.join(INDEX_DIR, req.chat_id)):
            raise HTTPException(status_code=404, detail=f"Index for chat_id {req.chat_id} not found")
            
        summary, messages_used, source_messages = analyze_messages(
            req.chat_id, 
            req.query, 
            req.user_id,
            req.max_messages,
            req.k,
            req.after_timestamp,
            req.enhance_query
        )
        
        return AnalyzeResponse(
            summary=summary, 
            messages_used=messages_used,
            source_messages=source_messages
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest_messages", response_model=IngestResponse)
def ingest_messages(req: IngestRequest, token: str = Depends(verify_token)):
    try:
        if not req.messages:
            raise HTTPException(status_code=400, detail="Messages field cannot be empty")
        
        result = save_messages(req.chat_id, req.messages)
        
        # Only reindex if new messages were added
        if result["added_count"] > 0:
            ingest_chat(req.chat_id)
        
        return IngestResponse(
            status="ok",
            message_count=len(req.messages),
            added_count=result["added_count"],
            skipped_count=result["skipped_count"],
            chat_id=req.chat_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
