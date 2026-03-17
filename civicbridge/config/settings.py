import os
from pathlib import Path

APP_NAME = "CivicBridge"
APP_TAGLINE = "Multilingual Public Service Navigator"

SUPPORTED_LANGUAGES = {
    "English": "en",
    "Malay": "ms",
    "Indonesian": "id",
}

DEFAULT_LLM_MODEL = "gpt-4o-mini"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

RETRIEVAL_K = 4

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DOCUMENT_PATH = BASE_DIR / "docs" / "sample_document.pdf"
