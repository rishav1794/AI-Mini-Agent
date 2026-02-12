# AI Mini Agent

## Screenshots
<img width="444" height="693" alt="Screenshot 2026-02-12 at 11 55 31 AM" src="https://github.com/user-attachments/assets/f616be5c-93a6-432b-9c46-0b3fecb8813d" />

<img width="430" height="683" alt="Screenshot 2026-02-12 at 11 58 33 AM" src="https://github.com/user-attachments/assets/c1856788-b4f0-454e-be34-42b3f6b28860" />

<img width="863" height="678" alt="Screenshot 2026-02-12 at 11 59 41 AM" src="https://github.com/user-attachments/assets/cb85a813-e197-4b23-b091-a910bb2ab9c9" />

A minimal full-stack AI agent demonstrating:

- Tool calling
- Short-term memory
- Retrieval-Augmented Generation (RAG)
- Modular backend architecture
- React-based chat interface

This is not a generic chatbot.  
It is a structured agent workflow.

---

## Why This Project Exists

Most “AI demos” are just prompt wrappers.

This project models how a real AI agent should behave:

- Maintain state
- Decide when to use tools
- Retrieve relevant knowledge
- Separate reasoning from execution
- Keep architecture modular and extensible

The focus is system design, not UI polish.

---

## Core Capabilities

### 1. Tool Calling

The agent can invoke structured backend tools:

- `calculate(expression)`
- `create_todo(task)`
- `list_todos()`
- `search_docs(query)`

The model decides when to call a tool.

If a tool is triggered:
1. Backend executes it.
2. Result is injected back into the model.
3. Final response is generated.

This introduces determinism into a probabilistic system.

LLMs generate language.  
Tools generate capability.

---

### 2. Short-Term Memory

Each session stores recent messages in SQLite.

Only the last N messages are injected into the prompt to:

- Maintain conversational context
- Avoid token bloat
- Improve response relevance

Memory is scoped per session.

In production, this would likely evolve into:
- Summarized history
- Semantic indexing
- User-scoped identity mapping

Memory is context management, not just storage.

### 3. Retrieval-Augmented Generation (RAG)

The backend includes a small local knowledge base:

Workflow:

1. Load documents
2. Chunk content
3. Embed chunks
4. Embed user query
5. Retrieve top-k similar chunks
6. Inject retrieved context into system prompt

This allows the agent to answer based on project-specific knowledge instead of relying only on model pretraining.

RAG is a relevance filter for prompt construction.

---

## Architecture

### Backend (FastAPI)

- backend/
- app/
- agent.py # agent reasoning loop
- tools.py # structured tool implementations
- rag.py # retrieval logic
- db.py # memory persistence
- main.py # API layer


Responsibilities:

- Construct system prompt
- Retrieve memory
- Inject RAG context
- Execute tools
- Return final response

SQLite is used for lightweight persistence.

The backend is intentionally modular:
- Reasoning logic separated from tools
- Tools separated from retrieval
- Retrieval separated from memory

---

### Frontend (React + TypeScript)

- frontend/
- src/
- Chat.tsx
- main.tsx


Features:

- Session-based chat UI
- API integration with FastAPI backend
- Minimal interface focused on agent behavior

No unnecessary UI complexity.

---

## Agent Execution Flow

High-level lifecycle:

1. User sends message.
2. Backend loads session memory.
3. RAG retrieves relevant context (if applicable).
4. System prompt is constructed.
5. Model may trigger tool call.
6. Backend executes tool.
7. Final response returned to user.

This enforces separation between reasoning and action.

---

## Tech Stack

Backend:
- Python
- FastAPI
- OpenAI SDK
- SQLite

Frontend:
- React
- TypeScript
- Vite
- pnpm

---

## Run Locally

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
## Create .env
 - OPENAI_API_KEY=your_key_here
 - OPENAI_MODEL=gpt-4o-mini

## Run
```bash
uvicorn app.main:app --reload --port 8000
```
## Frontend
```bash
cd frontend
pnpm install
pnpm dev
```
