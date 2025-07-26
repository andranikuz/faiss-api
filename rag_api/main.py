from fastapi import FastAPI, HTTPException, Depends
from dotenv import load_dotenv
from .models import SearchRequest, SearchResponse, AnalyzeRequest, AnalyzeResponse, IngestRequest, IngestResponse
from .search import search
from .analyze import analyze_messages
from .ingest import ingest_chat, save_messages
from .auth import verify_token
import os

load_dotenv()
app = FastAPI()

@app.post("/search", response_model=SearchResponse)
def search_messages(req: SearchRequest, token: str = Depends(verify_token)):
    try:
        if not os.path.exists(f"index/{req.chat_id}"):
            raise HTTPException(status_code=404, detail=f"Index for chat_id {req.chat_id} not found")
        results = search(req.chat_id, req.query, req.k)
        return SearchResponse(results=results)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest, token: str = Depends(verify_token)):
    try:
        if not os.path.exists(f"index/{req.chat_id}"):
            raise HTTPException(status_code=404, detail=f"Index for chat_id {req.chat_id} not found")
        gpt_answer, messages = analyze_messages(req.chat_id, req.query, req.k)
        return AnalyzeResponse(gpt_answer=gpt_answer, messages=messages)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest_messages", response_model=IngestResponse)
def ingest_messages(req: IngestRequest, token: str = Depends(verify_token)):
    try:
        if not req.messages:
            raise HTTPException(status_code=400, detail="Messages field cannot be empty")
        
        save_messages(req.chat_id, req.messages)
        ingest_chat(req.chat_id)
        
        return IngestResponse(
            status="ok",
            message_count=len(req.messages),
            chat_id=req.chat_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
