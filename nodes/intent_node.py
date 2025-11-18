"""
Intent Detection Node
Kullanıcı sorgusunun intent'ini tespit eder
"""

from state_schema import ChatState
from intent_detector import detect_intent
from langchain_google_genai import ChatGoogleGenerativeAI


def intent_detection_node(state: ChatState, llm: ChatGoogleGenerativeAI) -> ChatState:
    """
    Intent detection node - kullanıcı sorgusunu classify eder.
    
    Args:
        state: Current conversation state
        llm: LangChain LLM instance
    
    Returns:
        Updated state with intent information
    """
    query = state["user_query"]
    
    # Intent detection
    detection = detect_intent(llm, query)
    
    # Update state
    state["intent"] = detection.intent
    state["intent_confidence"] = detection.confidence
    state["intent_reasoning"] = detection.reasoning
    
    print(f"\n🎯 [INTENT NODE] Intent: {detection.intent} (confidence: {detection.confidence:.2f})")
    print(f"   Reasoning: {detection.reasoning}")
    
    return state
