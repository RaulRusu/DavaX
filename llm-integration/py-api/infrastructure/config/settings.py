import os
from dotenv import load_dotenv

load_dotenv(".env") 

# --- Application ---
APP_ENV = os.getenv("APP_ENV", "dev")
APP_NAME = os.getenv("APP_NAME", "chat-service")
BOOK_DATA_PATH = os.getenv("BOOK_DATA_PATH", "resources/books_with_tags.json")
ROUTER_SYSTEM_PROMPT_PATH = os.getenv("ROUTER_SYSTEM_PROMPT_PATH", "resources/router_system_prompt.txt")

# --- LLM / OpenAI ---
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Tool loop ---
TOOL_MAX_STEPS = int(os.getenv("TOOL_MAX_STEPS", "3"))

# --- Chroma ---
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "resources/chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "book_summaries")
MANIFEST_PATH_STRING = os.getenv("MANIFEST_PATH", f"resources/{CHROMA_COLLECTION}_manifest.json")
# --- RAG ---
RAG_RETRIEVER = os.getenv("RAG_RETRIEVER", "hybrid")
RAG_TOP_K_VECTOR = int(os.getenv("RAG_TOP_K_VECTOR", "12"))
RAG_TOP_K_LEXICAL = int(os.getenv("RAG_TOP_K_LEXICAL", "12"))
RAG_TOP_K_LLM_CONTEXT = int(os.getenv("RAG_TOP_K_LLM_CONTEXT", "4"))
RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small")

# --- Prompt policy ---
SYSTEM_MESSAGE = os.getenv(
    "SYSTEM_MESSAGE",
    "You are a helpful assistant who recommends books."
)
