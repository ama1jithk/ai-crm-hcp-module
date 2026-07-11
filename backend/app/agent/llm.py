from langchain_groq import ChatGroq
from app.config import settings


def get_llm(temperature: float = 0.2):
    """
    Primary model: gemma2-9b-it (fast, cheap, used for structured extraction/summarization).
    A larger model (llama-3.3-70b-versatile) can be swapped in via GROQ_FALLBACK_MODEL
    for tasks that need deeper reasoning (e.g. next-best-action suggestions).
    """
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=temperature,
    )


def get_fallback_llm(temperature: float = 0.3):
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_FALLBACK_MODEL,
        temperature=temperature,
    )
