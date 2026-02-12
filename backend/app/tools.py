import ast
import operator as op
from typing import Any, Dict, List

from .db import create_todo, list_todos
from .rag import MiniRAG

_ALLOWED = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

def _eval(node):
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numbers allowed")
    if isinstance(node, ast.BinOp):
        return _ALLOWED[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _ALLOWED[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")

def calculate(expression: str) -> Dict[str, Any]:
    tree = ast.parse(expression, mode="eval")
    return {"expression": expression, "result": _eval(tree.body)}

def get_weather(city: str) -> Dict[str, Any]:
    return {"city": city, "note": "Weather tool stub (swap to real API later).", "temp_c": None}

def make_tools(session_id: str, rag: MiniRAG):
    def _create_todo(task: str):
        return create_todo(session_id, task)

    def _list_todos():
        return {"todos": list_todos(session_id)}

    def _search_docs(query: str):
        hits = rag.retrieve(query, k=2)
        return {"query": query, "hits": [{"doc": d, "text": t} for d, t in hits]}

    tool_funcs = {
        "calculate": lambda expression: calculate(expression),
        "create_todo": lambda task: _create_todo(task),
        "list_todos": lambda: _list_todos(),
        "search_docs": lambda query: _search_docs(query),
        "get_weather": lambda city: get_weather(city),
    }

    tool_schemas: List[Dict[str, Any]] = [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Evaluate a math expression like '12*3+4'.",
                "parameters": {
                    "type": "object",
                    "properties": {"expression": {"type": "string"}},
                    "required": ["expression"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_todo",
                "description": "Create a todo task for the user.",
                "parameters": {
                    "type": "object",
                    "properties": {"task": {"type": "string"}},
                    "required": ["task"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_todos",
                "description": "List todos for the user.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_docs",
                "description": "Search local docs (RAG) and return top relevant chunks.",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather for a city (stub today).",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            },
        },
    ]

    return tool_schemas, tool_funcs