from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .db import init_db
from .agent import run_agent, build_rag

app = FastAPI(title="Invictus Mini Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    response: str

rag = None

@app.on_event("startup")
def on_startup():
    global rag
    init_db()
    rag = build_rag()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    global rag
    text = run_agent(session_id=req.session_id, user_text=req.message, rag=rag)
    return ChatResponse(session_id=req.session_id, response=text)