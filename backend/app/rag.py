import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import numpy as np

DOCS_DIR = Path(__file__).parent / "data" / "docs"

@dataclass
class Chunk:
    doc: str
    text: str
    vec: np.ndarray

def _chunk_text(text: str, chunk_size: int = 600, overlap: int = 120) -> List[str]:
    text = " ".join(text.split())
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i+chunk_size])
        i += max(1, chunk_size - overlap)
    return chunks

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-10
    return float(np.dot(a, b) / denom)

class MiniRAG:
    def __init__(self, embed_fn):
        self.embed_fn = embed_fn
        self.chunks: List[Chunk] = []

    def build(self) -> None:
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        files = sorted([p for p in DOCS_DIR.glob("*.txt")])
        if not files:
            return

        for p in files:
            content = p.read_text(encoding="utf-8")
            for c in _chunk_text(content):
                vec = self.embed_fn(c)
                self.chunks.append(Chunk(doc=p.name, text=c, vec=vec))

    def retrieve(self, query: str, k: int = 2) -> List[Tuple[str, str]]:
        if not self.chunks:
            return []
        qv = self.embed_fn(query)
        scored = [(_cosine(qv, ch.vec), ch) for ch in self.chunks]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [(ch.doc, ch.text) for _, ch in scored[:k]]