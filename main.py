from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from youtube_rag import build_rag_chain

app = FastAPI(title="YouTube RAG API", version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG chain
rag_chain = None
current_video_url = None


class YouTubeRequest(BaseModel):
    youtube_url: str


class QuestionRequest(BaseModel):
    question: str


class Response(BaseModel):
    status: str
    message: str


class AnswerResponse(BaseModel):
    answer: str
    success: bool


@app.get("/")
def root():
    return {
        "status": "YouTube RAG API Running",
        "version": "1.0",
        "endpoints": {
            "ingest": "/youtube/ingest",
            "ask": "/youtube/ask",
            "clear": "/youtube/clear"
        }
    }


@app.post("/youtube/ingest", response_model=Response)
def ingest(req: YouTubeRequest):
    """Process a YouTube video and build RAG chain"""
    global rag_chain, current_video_url
    
    try:
        print(f"📥 Processing YouTube URL: {req.youtube_url}")
        rag_chain = build_rag_chain(req.youtube_url)
        current_video_url = req.youtube_url
        
        return {
            "status": "success",
            "message": f"Video processed successfully. You can now ask questions!"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid URL: {str(e)}")
    
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Transcript error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.post("/youtube/ask", response_model=AnswerResponse)
def ask(req: QuestionRequest):
    """Ask a question about the processed video"""
    global rag_chain
    
    if rag_chain is None:
        raise HTTPException(
            status_code=400,
            detail="No video processed yet. Please use /youtube/ingest first."
        )
    
    try:
        print(f"❓ Question: {req.question}")
        answer = rag_chain.invoke(req.question)
        
        return {
            "answer": answer,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.delete("/youtube/clear")
def clear():
    """Clear the current RAG chain"""
    global rag_chain, current_video_url
    
    rag_chain = None
    current_video_url = None
    
    return {
        "status": "success",
        "message": "RAG chain cleared"
    }


@app.get("/youtube/status")
def status():
    """Check if a video is currently loaded"""
    return {
        "video_loaded": rag_chain is not None,
        "current_video": current_video_url if current_video_url else "None"
    }


if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)