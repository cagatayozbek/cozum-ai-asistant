import os
from typing import Annotated, TypedDict, Literal
from dotenv import load_dotenv
from operator import add

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from retriever import get_retrieved_documents, SUPPORTED_LEVELS

import traceback
import re
# --- CONFIGURATION ---
CHAT_MODEL = "gemini-2.5-flash"

# --- STATE SCHEMA (TypedDict for LangGraph) ---
class ChatState(TypedDict):
    """State for the chat graph."""
    levels: list[str] | None
    messages: Annotated[list[BaseMessage], add]  # add operator appends messages
    context: str

def initialize_chat_model() -> ChatGoogleGenerativeAI:
    """API anahtarını yükler ve sohbet modelini başlatır."""
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY ortam değişkeni bulunamadı. .env dosyasını kontrol edin.")
    
    return ChatGoogleGenerativeAI(
        model=CHAT_MODEL,
        google_api_key=google_api_key,
        temperature=0.4,  # Tutarlı ama doğal yanıtlar için (0.0=deterministik, 1.0=yaratıcı)
    )

def get_level_display_name(level: str) -> str:
    """Seviye kodunu kullanıcı dostu isme çevirir."""
    mapping = {
        "anaokulu": "Anaokulu",
        "ilkokul": "İlkokul (1-4. Sınıf)",
        "ortaokul": "Ortaokul (5-8. Sınıf)",
        "lise": "Lise (9-12. Sınıf)"
    }
    return mapping.get(level, level)

# --- TYPE DEFINITIONS ---
QueryType = Literal["casual", "followup", "question"]

# --- GRAPH NODES ---
def classify_query_with_llm(llm: ChatGoogleGenerativeAI, user_msg: str, recent_messages: list[BaseMessage]) -> QueryType:
    """LLM ile soru tipini sınıflandır - 3 kategori: casual, followup, question."""
    
    # Build context from last 3 messages (exclude current one)
    # TAM MESAJI AL - Kesme yok! Uzun AI yanıtları için kritik
    context_parts = []
    for msg in recent_messages[-3:]:
        msg_type = "User" if isinstance(msg, HumanMessage) else "AI"
        context_parts.append(f"{msg_type}: {msg.content}")
    
    conversation_history = "\n".join(context_parts) if context_parts else "İlk mesaj - followup olamaz"
    
    classification_prompt = f"""Classify this message into ONE category:
- casual: Selamlaşma, teşekkür, veda, kimlik sorusu (merhaba, teşekkürler, hoşçakal, sen kimsin)
- followup: Önceki yanıta bağımlı takip sorusu (tek başına anlamsız)
- question: Okul hakkında bağımsız yeni soru (retrieval gerekli)

RECENT CONTEXT:
{conversation_history}

CURRENT MESSAGE: "{user_msg}"

KEY TEST: "Bu mesaj önceki yanıt olmadan anlamlı mı?"
→ Selamlaşma/teşekkür/veda = casual
→ Kısa/belirsiz + önceki yanıta bağlı = followup
→ Spesifik okul sorusu = question

EXAMPLES:
"Merhaba" / "Teşekkürler" / "Sen kimsin?" → casual
"Kaç saat?" (after program discussion) → followup
"Ücret ne kadar?" (after service discussion) → followup
"manevi eğitim var mı" → question
"İngilizce eğitimi nasıl?" → question

Return ONLY the category name:"""
    
    response = llm.invoke([HumanMessage(content=classification_prompt)])
    classification = response.content.strip().lower()
    
    # Validate and fallback
    valid_classes: list[QueryType] = ["casual", "followup", "question"]
    if classification not in valid_classes:
        classification = "question"  # Güvenli taraf: retrieval yap
    
    return classification

def router_node(state: ChatState, llm: ChatGoogleGenerativeAI) -> Command[Literal["retrieve", "llm"]]:
    """Route to retrieval or direct LLM - Command pattern ile state update + routing."""
    messages = state.get("messages", [])
    
    if not messages:
        return Command(update={"context": ""}, goto="llm")
    
    # Get last user message (current query)
    last_user_msg = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_msg = msg.content
            break
    
    if not last_user_msg:
        return Command(update={"context": ""}, goto="llm")
    
    # Pass recent message history to classifier (exclude current message for context)
    recent_messages = messages[:-1] if len(messages) > 1 else []
    query_type = classify_query_with_llm(llm, last_user_msg, recent_messages)
    
    # Casual conversation (selamlaşma, teşekkür, veda, kimlik) - direkt LLM'e git
    if query_type == "casual":
        return Command(update={"context": ""}, goto="llm")
    
    # Takip sorusu - mevcut context'i koru, direkt LLM'e git
    if query_type == "followup":
        return Command(goto="llm")  # Keep existing context
    
    # Yeni soru - retrieval gerekli
    return Command(update={"context": "NEEDS_RETRIEVAL"}, goto="retrieve")

def retrieve_node(state: ChatState) -> dict:
    """Retrieve relevant documents based on last user message."""
    # Check if retrieval is needed (router marks it)
    if state.get("context") != "NEEDS_RETRIEVAL":
        return {}  # Skip retrieval, keep existing context
    
    if not state.get("messages"):
        return {"context": ""}
    
    # Get last user message
    last_user_msg = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            last_user_msg = msg.content
            break
    
    if not last_user_msg or not state.get("levels"):
        return {"context": ""}
    
    # Retrieve documents
    retrieved_docs = get_retrieved_documents(
        last_user_msg,
        k=4,
        levels=state.get("levels", []),
        force_recreate=False,
        silent=True
    )
    
    # Format context
    if not retrieved_docs:
        context = "Bilgi bulunamadı."
    else:
        context_parts = []
        for i, (doc, score) in enumerate(retrieved_docs, 1):
            level = doc.metadata.get('level', 'N/A').upper()
            title = doc.metadata.get('title', 'Başlık yok')
            content = doc.metadata.get('original_content', doc.page_content)
            context_parts.append(f"[{level}] {title}\n{content}")
        context = "\n\n---\n\n".join(context_parts)
    
    # Return context to be used by LLM (store in state for next node)
    # Don't add to messages, just pass it through state
    return {"context": context}

def llm_node(state: ChatState, llm: ChatGoogleGenerativeAI) -> dict:
    """Generate response using LLM with context and full conversation history."""
    if not state.get("messages"):
        return {}
    
    # Get context from state (set by retrieve_node)
    context = state.get("context", "")
    
    # Build system prompt
    level_info = ", ".join([get_level_display_name(l) for l in state.get("levels", [])]) if state.get("levels") else "Henüz seçilmedi"
    
    system_prompt = f"""Siz Çözüm Eğitim Kurumları'nın veli asistanısınız.
Seçili kademeler: {level_info}

KILAVUZ:
1) Yalnızca BAĞLAM'daki bilgileri kullanın; asla uydurma yapmayın.
2) Resmi fakat samimi bir üslupla "siz" diye hitap edin.
3) Yanıta kısa bir özetle başlayın; ardından çoğu durumda ayrıntılı ve kapsamlı açıklama verin — gerekirse birkaç paragraf, maddeleme ve örneklerle destekleyin. Sadece selamlaşma/teşekkür gibi durumlarda çok kısa olun.
4) Takip sorularında önceki konuşma geçmişini kullanın ve sadece sorulan spesifik bilgiyi verin; yine de gerekiyorsa bağlamı genişletecek ek açıklamalar ekleyin.
5) BAĞLAM'da ilgili bilgi yoksa: "Üzgünüm, bu konuda size yardımcı olamıyorum." deyin ve veliyi okula yönlendirin.
6) Ücretlerle ilgili soru geldiğinde fiyat vermeyin; "Ücret bilgisi için lütfen okulla iletişime geçin." şeklinde yönlendirin.
7) Gereksiz tekrar ve dolgu cümlelerinden kaçının; ancak bilgi aktarımı için gerekli açıklamaları atlamayın.

ÖRNEKLER:
Veli: "İngilizce eğitimi nasıl?"
Asistan: "İlkokul (1-4): Cambridge programı — Haftalık: 12 saat Main Course, 2 saat Think&Talk. Dil Duşu yöntemiyle erken yaşta desteklenir.
Detaylar:
• Ders yapısı: ... 
• Değerlendirme: ...
• Öneriler: ...

Veli: "Okul hakkında bilgi istiyorum"
Asistan: "Okulumuz modern bir eğitim anlayışıyla öğrenci gelişimine odaklanır. Hangi konuda detay istersiniz? • Eğitim programları • İngilizce • Sosyal aktiviteler • Ücretler • Servis"

Veli: "Merhaba"
Asistan: "Merhaba! Ben Çözüm Eğitim Kurumları'nın veli asistanıyım. Size nasıl yardımcı olabilirim?"

BAĞLAM: {context if context else "Genel sohbet; okula özgü bilgi gerekmiyor."}"""
    
    # Pass FULL conversation history + system prompt
    # This allows LLM to see previous messages for follow-up questions
    messages = [
        SystemMessage(content=system_prompt),
        *state["messages"]  # Include ALL previous messages (HumanMessage and AIMessage)
    ]
    
    # Invoke LLM with complete conversation history
    response = llm.invoke(messages)
    
    return {"messages": [AIMessage(content=response.content)]}

class ChatSession:
    """LangGraph-based chat session manager."""
    
    def __init__(self, llm: ChatGoogleGenerativeAI, checkpointer: MemorySaver):
        self.llm = llm
        self.checkpointer = checkpointer
        self.graph = self._build_graph()
        self.thread_id = "default"  # Can be changed for multi-user scenarios
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        # Create graph
        workflow = StateGraph(ChatState)
        
        # Add nodes - pass llm to router for classification
        workflow.add_node("router", lambda state: router_node(state, self.llm))
        workflow.add_node("retrieve", retrieve_node)
        workflow.add_node("llm", lambda state: llm_node(state, self.llm))
        
        # Add edges - Command pattern handles routing automatically
        workflow.add_edge(START, "router")
        workflow.add_edge("retrieve", "llm")  # Retrieve sonrası LLM'e git
        workflow.add_edge("llm", END)
        
        # Compile with checkpointer
        return workflow.compile(checkpointer=self.checkpointer)
    
    def get_config(self):
        """Get configuration with thread_id."""
        return {"configurable": {"thread_id": self.thread_id}}
    
    def get_state(self) -> dict:
        """Get current state as dict."""
        state = self.graph.get_state(self.get_config())
        if state and state.values:
            # Ensure all keys have defaults
            values = state.values
            return {
                "levels": values.get("levels"),
                "messages": values.get("messages", []),
                "context": values.get("context", "")
            }
        return {"levels": None, "messages": [], "context": ""}
    
    def clear_history(self):
        """Clear conversation history by resetting thread."""
        self.thread_id = f"thread_{os.urandom(8).hex()}"
    
    def set_levels(self, levels: list[str]):
        """Set education levels in state."""
        # Simply update state with new levels
        self.graph.update_state(self.get_config(), {"levels": levels})
    
    def chat(self, user_query: str) -> str:
        """Send user message and get response."""
        try:
            # Simply invoke with the new message - let the graph handle state
            # The 'add' operator will automatically append to existing messages
            result = self.graph.invoke(
                {"messages": [HumanMessage(content=user_query)]},
                self.get_config()
            )
            
            # Extract last AI message from result
            if result and "messages" in result:
                for msg in reversed(result["messages"]):
                    if isinstance(msg, AIMessage):
                        response = msg.content
                        
                        # Check for level change tags
                        
                        tag_pattern = r'#KADEME_EKLE:(\w+)#'
                        matches = re.findall(tag_pattern, response)
                        
                        if matches:
                            # Extract and add new levels
                            current_state = self.get_state()
                            current_levels = current_state.get("levels", [])
                            
                            for level_to_add in matches:
                                level_to_add = level_to_add.lower()
                                if level_to_add in SUPPORTED_LEVELS and level_to_add not in current_levels:
                                    current_levels.append(level_to_add)
                            
                            # Update state with new levels
                            if current_levels != current_state.get("levels", []):
                                self.graph.update_state(self.get_config(), {"levels": current_levels})
                            
                            # Remove tags from response
                            response = re.sub(tag_pattern, '', response).strip()
                        
                        return response
            
            return "Üzgünüm, bir yanıt üretemedim. Lütfen sorunuzu farklı şekilde sormayı deneyin."
        except Exception as e:
            # Log error but don't expose details to user
            
            traceback.print_exc()
            return "Üzgünüm, teknik bir sorun oluştu. Lütfen tekrar deneyin."

# CLI için main() fonksiyonu kaldırıldı
# Production'da Streamlit (app.py) kullanılıyor
