import sqlite3
from pathlib import Path
from typing import Any, Dict, List

DB_PATH = Path(__file__).parent / "app.db"

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            task TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_message(session_id: str, role: str, content: str) -> None:
    conn = get_conn()
    conn.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content),
    )
    conn.commit()
    conn.close()

def get_last_messages(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit),
    ).fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

def create_todo(session_id: str, task: str) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO todos (session_id, task) VALUES (?, ?)",
        (session_id, task),
    )
    conn.commit()
    todo_id = cur.lastrowid
    conn.close()
    return {"id": todo_id, "task": task, "done": False}

def list_todos(session_id: str) -> List[Dict[str, Any]]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, task, done FROM todos WHERE session_id = ? ORDER BY id DESC",
        (session_id,),
    ).fetchall()
    conn.close()
    return [{"id": r["id"], "task": r["task"], "done": bool(r["done"])} for r in rows]