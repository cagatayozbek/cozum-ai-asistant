"""
Multi-Tool Agent Architecture
Çözüm Koleji Veli Asistanı - Simplified LangChain Agent
"""

import os
from dotenv import load_dotenv
import traceback

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from tools import AVAILABLE_TOOLS
from retriever import SUPPORTED_LEVELS

# --- CONFIGURATION ---
CHAT_MODEL = "gemini-2.5-flash"


def initialize_chat_model() -> ChatGoogleGenerativeAI:
    """API anahtarını yükler ve sohbet modelini başlatır."""
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY ortam değişkeni bulunamadı. .env dosyasını kontrol edin.")
    
    return ChatGoogleGenerativeAI(
        model=CHAT_MODEL,
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
    """LangChain Agent tabanlı sohbet oturumu yöneticisi."""
    
    def __init__(self, llm: ChatGoogleGenerativeAI, checkpointer: MemorySaver = None):
        self.llm = llm
        self.checkpointer = checkpointer or MemorySaver()
        self.levels = None  # Seçili eğitim kademeleri
        self.conversation_history = []  # Sohbet geçmişi
        self.thread_id = "default"
        
        # Agent'i oluştur
        self.agent = self._create_agent()
    
    def _create_agent(self):
        """LangChain v1 agent oluştur - create_agent API ile."""
        
        # System prompt - agent'e talimatlar
        system_prompt = """Siz Çözüm Eğitim Kurumları'nın veli asistanısınız.

GÖREV:
Velilerin okul hakkındaki sorularını yanıtlayın. İhtiyaç duyduğunuzda araçlarınızı kullanın.

ARAÇLARINIZ:
1. retrieve_education_info: Eğitim programları, dersler, spor aktiviteleri hakkında bilgi
2. search_school_news: Güncel haberler, etkinlikler, duyurular (henüz aktif değil)

KURALLAR:
1) Eğitim programı soruları → retrieve_education_info aracını kullanın
2) Etkinlik/haber soruları → search_school_news aracını kullanın  
3) Selamlaşma/teşekkür → Hiçbir araç kullanmayın, doğrudan yanıt verin
4) Takip soruları → Sohbet geçmişini kullanın, gerekirse araçları tekrar çağırın

ÜSLUP:
- Resmi fakat samimi "siz" ile hitap edin
- Kısa özetle başlayın, sonra detaylı açıklama
- Selamlaşmalarda çok kısa olun
- Bilgi yoksa: "Üzgünüm, bu konuda size yardımcı olamıyorum."
- Ücret sorularında: "Ücret bilgisi için lütfen okulla iletişime geçin."

ÖRNEKLER:
Veli: "Merhaba"
Siz: "Merhaba! Ben Çözüm Eğitim Kurumları'nın veli asistanıyım. Size nasıl yardımcı olabilirim?"

Veli: "İngilizce eğitimi nasıl?"
Siz: [retrieve_education_info aracını kullan] → Detaylı yanıt ver

Veli: "Bu hafta etkinlik var mı?"
Siz: [search_school_news aracını kullan] → Yanıt ver"""

        # LangChain v1 create_agent API
        agent = create_agent(
            model=self.llm,
            tools=AVAILABLE_TOOLS,
            system_prompt=system_prompt,
            checkpointer=self.checkpointer,
        )
        
        return agent
    
    def set_levels(self, levels: list[str]):
        """Eğitim kademelerini ayarla."""
        self.levels = levels
    
    def clear_history(self):
        """Sohbet geçmişini temizle."""
        self.conversation_history = []
        self.thread_id = f"thread_{os.urandom(8).hex()}"
    
    def chat(self, user_query: str) -> str:
        """Kullanıcı mesajını gönder ve yanıt al."""
        try:
            # Conversation history'yi hazırla
            messages = []
            for msg in self.conversation_history:
                if isinstance(msg, dict):
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg.get("role") == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            
            # Yeni kullanıcı mesajını ekle
            messages.append(HumanMessage(content=user_query))
            
            # Agent'i çağır (LangChain v1 API)
            response = self.agent.invoke(
                {"messages": messages},
                config={"configurable": {"thread_id": self.thread_id}}
            )
            
            # Yanıtı çıkar (son mesaj AI yanıtı olmalı)
            output = ""
            if "messages" in response:
                for msg in reversed(response["messages"]):
                    if isinstance(msg, AIMessage):
                        # LangChain v1 content_blocks formatını handle et
                        if isinstance(msg.content, str):
                            output = msg.content
                        elif isinstance(msg.content, list):
                            # content_blocks formatı - sadece text kısmını al
                            for block in msg.content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    output = block.get("text", "")
                                    break
                        break
            
            if not output:
                output = "Üzgünüm, bir yanıt üretemedim."
            
            # Conversation history'ye ekle
            self.conversation_history.append({"role": "user", "content": user_query})
            self.conversation_history.append({"role": "assistant", "content": output})
            
            return output
            
        except Exception as e:
            traceback.print_exc()
            return "Üzgünüm, teknik bir sorun oluştu. Lütfen tekrar deneyin."


# Visualization için (opsiyonel)
if __name__ == "__main__":
    """Test agent locally"""
    print("🤖 Multi-Tool Agent Test\n")
    
    llm = initialize_chat_model()
    session = ChatSession(llm)
    session.set_levels(["lise"])
    
    # Test queries
    queries = [
        "Merhaba",
        "Lise İngilizce programı nasıl?",
        "Kaç saat İngilizce var?",
    ]
    
    for query in queries:
        print(f"\n👤 Kullanıcı: {query}")
        response = session.chat(query)
        print(f"🤖 Asistan: {response}")
        print("-" * 80)
