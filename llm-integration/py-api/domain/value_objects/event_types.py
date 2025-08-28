from enum import Enum

class EventType(str, Enum):
    MESSAGE_TEXT = "message_text"
    FUNCTION_CALL = "function_call"
    FUNCTION_CALL_OUTPUT = "function_call_output"
    RAG_QUERY = "rag_query"
    RAG_RETRIEVAL = "rag_retrieval"
    RAG_SUMMARY = "rag_summary"
    SUMMARY = "summary"
    SANITIZER_REPORT = "sanitizer_report"
    ERROR = "error"

    @classmethod
    def for_llm_input(cls):
        """Event types safe to include in LLM prompts by default."""
        return {
            cls.MESSAGE_TEXT,
            cls.FUNCTION_CALL_OUTPUT,
            cls.RAG_SUMMARY,
            cls.SUMMARY,
        }
