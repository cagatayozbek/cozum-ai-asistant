"""
Router Node
Intent'e göre hangi node'a gidileceğine karar verir
"""

from state_schema import ChatState
from typing import Literal


RouteDestination = Literal["retrieve", "search_news", "direct_answer", "price_info"]


def router_node(state: ChatState) -> RouteDestination:
    """
    Router node - intent'e göre routing kararı verir.
    
    Args:
        state: Current conversation state
    
    Returns:
        Destination node name
    """
    intent = state.get("intent", "unknown")
    
    # Routing logic
    if intent == "education":
        destination = "retrieve"
    elif intent == "event":
        destination = "search_news"
    elif intent == "price":
        destination = "price_info"
    else:  # greeting, unknown
        destination = "direct_answer"
    
    print(f"\n🔀 [ROUTER NODE] Intent: {intent} → Routing to: {destination}")
    
    return destination
