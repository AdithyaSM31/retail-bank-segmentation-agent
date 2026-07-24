"""
FastAPI Backend — Provides API endpoints for the banking analytics agent.
Handles chat, file uploads, and downloads.
"""
import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agent.orchestrator import create_agent, run_agent_query
from config import OUTPUT_DIR

app = FastAPI(
    title="Customer Segmentation Agent API",
    description="AI-powered banking analytics agent for customer segmentation and personalization",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create agent on startup
agent = None
# Store conversation history per session
sessions: dict[str, list] = {}


@app.on_event("startup")
async def startup():
    global agent
    agent = create_agent()


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    charts: list[str] = []
    session_id: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a user query through the banking analytics agent."""
    global agent
    if agent is None:
        agent = create_agent()

    # Get or create session history
    history = sessions.get(request.session_id, [])

    try:
        result = run_agent_query(agent, request.message, history)

        # Update session history
        history.append({"role": "user", "content": request.message})
        history.append({"role": "assistant", "content": result["response"]})
        sessions[request.session_id] = history

        return ChatResponse(
            response=result["response"],
            charts=result["charts"],
            session_id=request.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download an exported file from the outputs directory."""
    filepath = OUTPUT_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
    return FileResponse(path=str(filepath), filename=filename)


@app.get("/health")
async def health():
    return {"status": "healthy", "agent_loaded": agent is not None}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
