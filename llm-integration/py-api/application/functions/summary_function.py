from typing import Dict, Any
from pathlib import Path
import json
from infrastructure.config import settings
from infrastructure.llm.function import LLMFunction, Param

DATA_PATH = Path(settings.BOOK_DATA_PATH)

def _load_books() -> Dict[str, str]:
    if DATA_PATH.exists():
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        return {item["title"]: item["summary"] for item in data}
    return {}

BOOKS = _load_books()

def _normalize_title(t: str) -> str:
    return " ".join(t.strip().split())

def get_summary_by_title(*, title: str, lang: str = "en") -> str:
    key = _normalize_title(title)
    return {
        "summary": BOOKS.get(key, f"Summary not found for: {title}")
    }

def get_summary_tool() -> LLMFunction:
    return LLMFunction(
        name="get_summary_by_title",
        description="Return the full summary of a book for an exact title.",
        handler=get_summary_by_title,
        params=[
            Param("title", str, "Exact book title", required=True),
            Param("lang",  str, "Language code (e.g. 'en', 'ro')", required=False, default="en"),
        ],
    )
