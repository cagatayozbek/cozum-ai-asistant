"""
LangGraph Workflow - Multi-Node Architecture
Intent-based routing ile deterministik conversation flow
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

from state_schema import ChatState
from nodes.intent_node import intent_detection_node
from nodes.router_node import router_node
from nodes.retrieve_node import retrieve_node
from nodes.compression_node import context_compression_node
from nodes.answer_node import (
    answer_node, 
    direct_answer_node, 
    search_news_node, 
    price_info_node
)


def create_workflow(llm: ChatGoogleGenerativeAI, checkpointer: InMemorySaver = None):
    """
    LangGraph workflow oluşturur.
    
    Flow:
    START → intent_detection → router 
             ↓
    ┌────────┼────────┬─────────┐
    ↓        ↓        ↓         ↓
    retrieve  news   price    direct
    ↓        ↓        ↓         ↓
    compress (70% token reduction)
    ↓        ↓        ↓         ↓
    └────────┴────────┴─────────┘
             ↓
           answer → END
    
    Args:
        llm: ChatGoogleGenerativeAI instance
        checkpointer: InMemorySaver for conversation persistence
    
    Returns:
        Compiled StateGraph
    """
    # Create StateGraph
    workflow = StateGraph(ChatState)
    
    # Add nodes
    workflow.add_node("intent_detection", lambda state: intent_detection_node(state, llm))
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("search_news", search_news_node)
    workflow.add_node("price_info", price_info_node)
    workflow.add_node("compression", context_compression_node)  # 🆕 Context compression
    workflow.add_node("direct_answer", lambda state: direct_answer_node(state, llm))
    workflow.add_node("answer", lambda state: answer_node(state, llm))
    
    # Set entry point
    workflow.set_entry_point("intent_detection")
    
    # Add conditional routing after intent detection
    workflow.add_conditional_edges(
        "intent_detection",
        router_node,
        {
            "retrieve": "retrieve",
            "search_news": "search_news",
            "price_info": "price_info",
            "direct_answer": "direct_answer"
        }
    )
    
    # All nodes go to compression first (except direct_answer)
    workflow.add_edge("retrieve", "compression")
    workflow.add_edge("search_news", "compression")
    workflow.add_edge("price_info", "compression")
    
    # Compression goes to answer
    workflow.add_edge("compression", "answer")
    
    # Direct answer bypasses compression
    workflow.add_edge("direct_answer", END)  # Direct answer goes to END
    
    # Answer node goes to END
    workflow.add_edge("answer", END)
    
    # Compile
    app = workflow.compile(checkpointer=checkpointer)
    
    return app


# Visualization helper
def generate_mermaid_diagram() -> str:
    """LangGraph workflow'unun Mermaid diagram'ını oluşturur."""
    return """
```mermaid
graph TD
    START([START]) --> intent[Intent Detection]
    intent --> router{Router}
    
    router -->|education| retrieve[Retrieve Node<br/>FAISS Search]
    router -->|event| news[Search News Node<br/>Web Scraper]
    router -->|price| price[Price Info Node<br/>Contact Info]
    router -->|greeting/unknown| direct[Direct Answer Node<br/>No Context]
    
    retrieve --> compress[Compression Node<br/>70% Token Reduction]
    news --> compress
    price --> compress
    
    compress --> answer[Answer Node<br/>LLM Response]
    
    direct --> END([END])
    answer --> END
    
    style intent fill:#e1f5ff
    style router fill:#fff4e1
    style retrieve fill:#e8f5e9
    style news fill:#fff3e0
    style price fill:#fce4ec
    style compress fill:#fff9c4
    style direct fill:#f3e5f5
    style answer fill:#e0f2f1
```
"""


if __name__ == "__main__":
    """Workflow diagram'ını yazdır."""
    print(generate_mermaid_diagram())
