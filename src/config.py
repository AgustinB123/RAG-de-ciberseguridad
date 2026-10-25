import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCES_DIR = BASE_DIR / "sources"
CHROMA_DIR = BASE_DIR / "chroma_db"

LLM_MODEL = "qwen2.5:14b"
EMBEDDING_MODEL = "nomic-embed-text"

# Configuración del fragmentado
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200