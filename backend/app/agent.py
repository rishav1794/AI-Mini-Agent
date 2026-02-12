import json
import os
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from .db import get_last_messages, save_message
from .rag import MiniRAG
from .tools import make_tools

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
RAG_EMBEDDINGS = os.getenv("RAG_EMBEDDINGS", "true").lower() == "true"

client = OpenAI()

def _embed_text(text: str):
    import numpy as np
    if not RAG_EMBEDDINGS:
        h = abs(hash(text)) % 10_000
        rng = np.random.default_rng(h)
        return rng.random(128).astype("float32")

    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(resp.data[0].embedding, dtype="float32")

def build_rag() -> MiniRAG:
    rag = MiniRAG(embed_fn=_embed_text)
    rag.build()
    return rag

SYSTEM_PROMPT = """You are Invictus Mini Agent.
You can chat normally, but you also have tools.
Rules:
- Use tools when it helps: math -> calculate, tasks -> create_todo/list_todos, knowledge from local docs -> search_docs.
- If user asks about content that might exist in docs, call search_docs.
- Be concise and correct.
"""

def run_agent(session_id: str, user_text: str, rag: MiniRAG) -> str:
    save_message(session_id, "user", user_text)

    memory = get_last_messages(session_id, limit=10)
    rag_hits = rag.retrieve(user_text, k=2)
    rag_block = ""
    if rag_hits:
        rag_block = "\n\n".join([f"[{doc}] {txt}" for doc, txt in rag_hits])

    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if rag_block:
        messages.append({"role": "system", "content": f"Relevant local context:\n{rag_block}"})
    messages.extend(memory)

    tool_schemas, tool_funcs = make_tools(session_id=session_id, rag=rag)

    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tool_schemas,
        tool_choice="auto",
    )

    msg = resp.choices[0].message

    if msg.tool_calls:
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
        })

        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")
            fn = tool_funcs.get(name)
            if not fn:
                tool_result = {"error": f"Unknown tool: {name}"}
            else:
                try:
                    tool_result = fn(**args)
                except Exception as e:
                    tool_result = {"error": str(e), "tool": name}

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": name,
                "content": json.dumps(tool_result),
            })

        resp2 = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
        final_text = resp2.choices[0].message.content or ""
    else:
        final_text = msg.content or ""

    save_message(session_id, "assistant", final_text)
    return final_text