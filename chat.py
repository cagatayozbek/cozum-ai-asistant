"""
Refactored Chat Session - LangGraph Multi-Node Architecture
Production-ready, modular, testable chatbot system
"""

import os
from dotenv import load_dotenv
import traceback

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import InMemorySaver

from workflow import create_workflow
from state_schema import create_initial_state, ChatState
from retriever import SUPPORTED_LEVELS

# --- CONFIGURATION ---
def initialize_chat_model() -> ChatGoogleGenerativeAI:
    """API anahtarını yükler ve sohbet modelini başlatır."""
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY ortam değişkeni bulunamadı. .env dosyasını kontrol edin.")
    
    # Model selection: env var or fallback to default
    model_name = os.getenv("GEMINI_MODEL")
    
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=google_api_key,
        temperature=0.4,  # Tutarlı ama doğal yanıtlar için
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


class ChatSession:
    """
    Refactored Chat Session - LangGraph Multi-Node Architecture
    
    ✨ YENİ ÖZELLİKLER:
    - Intent-based deterministik routing
    - Modüler prompt sistemi (role, style, context, output ayrı)
    - LangGraph native memory management (checkpointer)
    - Her node izole ve test edilebilir
    - Sliding window memory (LangGraph manages)
    - Production-ready error handling
    
    ❌ ESKİ SİSTEM (KALDIRILDI):
    - create_agent (tool-based agent)
    - self.conversation_history (manual memory)
    - Double SystemMessage (çift prompt sorunu)
    - Tool dispatch belirsizliği
    """
    
    def __init__(self, llm: ChatGoogleGenerativeAI, checkpointer: InMemorySaver = None, compress_context: bool = False):
        self.llm = llm
        self.checkpointer = checkpointer or InMemorySaver()
        self.levels = None  # Seçili eğitim kademeleri
        self.thread_id = "default"
        self.compress_context = compress_context  # Context compression control (A/B test için - DEFAULT: OFF)
        
        # LangGraph workflow oluştur
        self.workflow = create_workflow(self.llm, self.checkpointer)
    
    def set_levels(self, levels: list[str]):
        """
        Eğitim kademelerini ayarla.
        
        Args:
            levels: Seçili kademe listesi (örn: ["anaokulu", "lise"])
        """
        self.levels = levels
        print(f"\n✅ Kademe güncellendi: {', '.join(levels)}")
    
    def clear_history(self):
        """Sohbet geçmişini temizle - yeni thread ID oluştur."""
        self.thread_id = f"thread_{os.urandom(8).hex()}"
        print(f"\n🗑️  Sohbet geçmişi temizlendi (yeni thread: {self.thread_id})")
    
    def chat(self, user_query: str) -> str:
        """
        Kullanıcı mesajını işle ve yanıt döndür.
        
        LangGraph Workflow:
        1. Intent Detection → Query classify edilir
        2. Router → Intent'e göre doğru node'a yönlendirilir
        3. Retrieve/News/Price/Direct → Context hazırlanır
        4. Answer → Final LLM yanıtı oluşturulur
        
        Memory:
        - LangGraph checkpointer otomatik manage eder
        - Sliding window (last 10 messages) answer_node içinde
        - Thread-based conversation persistence
        
        Args:
            user_query: Kullanıcının sorusu
        
        Returns:
            Final answer string
        """
        try:
            # Active levels
            active_levels = self.levels if self.levels else list(SUPPORTED_LEVELS)
            
            # Get conversation history from checkpointer
            config = {"configurable": {"thread_id": self.thread_id}}
            
            # Get existing messages from checkpointer (if any)
            try:
                snapshot = self.workflow.get_state(config)
                existing_messages = snapshot.values.get("messages", []) if snapshot else []
            except:
                existing_messages = []
            
            # Add new user message
            messages = existing_messages + [HumanMessage(content=user_query)]
            
            # Create initial state
            initial_state = create_initial_state(
                user_query=user_query,
                active_levels=active_levels,
                messages=messages,
                compress_context=self.compress_context  # A/B test için
            )
            
            print(f"\n" + "="*80)
            print(f"💬 [CHAT SESSION] Yeni soru işleniyor")
            print(f"   Thread ID: {self.thread_id}")
            print(f"   Aktif kademeler: {active_levels}")
            print(f"   Mesaj geçmişi: {len(messages)} mesaj")
            print(f"   🗜️  Context Compression: {'ON' if self.compress_context else 'OFF'}")
            print("="*80)
            
            # Invoke workflow
            result = self.workflow.invoke(initial_state, config)
            
            # Extract final answer
            final_answer = result.get("final_answer", "Üzgünüm, bir yanıt üretemedim.")
            
            print(f"\n✅ [CHAT SESSION] Yanıt hazır ({len(final_answer)} karakter)")
            print("="*80 + "\n")
            
            return final_answer
            
        except Exception as e:
            print(f"\n❌ [CHAT SESSION] Hata oluştu:")
            traceback.print_exc()
            return "Üzgünüm, teknik bir sorun oluştu. Lütfen tekrar deneyin."


# Test
if __name__ == "__main__":
    """
    Test senaryoları:
    1. Greeting
    2. Education (FAISS retrieval)
    3. Price (contact info)
    4. Unknown (fallback)
    """
    print("🤖 Refactored Chat Session Test\n")
    
    llm = initialize_chat_model()
    session = ChatSession(llm)
    
    # Test 1: Greeting
    print("\n" + "🟢 TEST 1: GREETING".center(80, "="))
    session.set_levels(["anaokulu"])
    response1 = session.chat("Merhaba")
    print(f"\n📝 Yanıt:\n{response1}\n")
    
    # Test 2: Education
    print("\n" + "🟢 TEST 2: EDUCATION (FAISS)".center(80, "="))
    response2 = session.chat("Anaokulunda İngilizce eğitimi nasıl?")
    print(f"\n📝 Yanıt:\n{response2}\n")
    
    # Test 3: Price
    print("\n" + "🟢 TEST 3: PRICE".center(80, "="))
    response3 = session.chat("Ücretler ne kadar?")
    print(f"\n📝 Yanıt:\n{response3}\n")
    
    # Test 4: Unknown
    print("\n" + "🟢 TEST 4: UNKNOWN".center(80, "="))
    response4 = session.chat("Hava durumu nasıl?")
    print(f"\n📝 Yanıt:\n{response4}\n")
    
    # Test 5: Level change
    print("\n" + "🟢 TEST 5: LEVEL CHANGE".center(80, "="))
    session.set_levels(["lise"])
    response5 = session.chat("İngilizce eğitimi nasıl?")
    print(f"\n📝 Yanıt:\n{response5}\n")
    
    print("\n" + "✅ TÜM TESTLER TAMAMLANDI".center(80, "=") + "\n")
