"""
State Schema - LangGraph State Tanımı
Tüm workflow boyunca kullanılan state yapısı
"""

from typing import TypedDict, List, Optional, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class ChatState(TypedDict):
    """
    LangGraph workflow state.
    
    LangGraph multi-node mimarisinde tüm node'lar arasında paylaşılan state.
    Her node bu state'i okuyabilir ve güncelleyebilir.
    """
    # Conversation messages (LangGraph manages this with add_messages)
    messages: Annotated[List[BaseMessage], add_messages]
    
    # User query
    user_query: str
    
    # Intent detection result
    intent: Optional[str]  # "greeting", "education", "event", "price", "unknown"
    intent_confidence: Optional[float]
    intent_reasoning: Optional[str]
    
    # Active education levels
    active_levels: List[str]  # ["anaokulu", "ilkokul", "ortaokul", "lise"]
    
    # Retrieved context from FAISS/tools
    retrieved_context: Optional[str]
    
    # Final answer
    final_answer: Optional[str]
    
    # Error handling
    error: Optional[str]


def create_initial_state(
    user_query: str,
    active_levels: List[str],
    messages: List[BaseMessage]
) -> ChatState:
    """
    Yeni conversation için initial state oluşturur.
    
    Args:
        user_query: Kullanıcının sorusu
        active_levels: Seçili eğitim kademeleri
        messages: Conversation history (LangChain messages)
    
    Returns:
        ChatState: Initial state
    """
    return ChatState(
        messages=messages,
        user_query=user_query,
        intent=None,
        intent_confidence=None,
        intent_reasoning=None,
        active_levels=active_levels,
        retrieved_context=None,
        final_answer=None,
        error=None
    )
