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
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver

from retriever import get_retrieved_documents, SUPPORTED_LEVELS

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
        
        # Tools oluştur (closure ile self.levels erişimi)
        self.tools = self._create_tools()
        
        # Agent'i oluştur
        self.agent = self._create_agent()
    
    def _create_tools(self):
        """ChatSession'a özel tools oluştur - self.levels ile closure."""
        
        @tool
        def retrieve_education_info(query: str) -> str:
            """
            Eğitim programları, ders saatleri, İngilizce eğitimi, spor aktiviteleri hakkında bilgi alır.
            
            FAISS vector store'dan semantik arama yaparak okul eğitim dokümanlarından bilgi getirir.
            Kullanıcının seçtiği kademelerde otomatik olarak arama yapar.
            
            Args:
                query: Kullanıcının sorusu (örn: "Lise İngilizce programı nasıl?")
            
            Returns:
                Formatlanmış doküman içerikleri veya "Bilgi bulunamadı" mesajı
            
            Örnekler:
                - "Lise programı nedir?"
                - "İngilizce kaç saat?"
                - "Spor faaliyetleri neler?"
                - "Ders saatleri nasıl?"
            """
            # Kullanıcının seçtiği kademeleri kullan (yoksa tüm kademeler)
            levels = self.levels if self.levels else list(SUPPORTED_LEVELS)
            
            # Retrieve documents from FAISS
            retrieved_docs = get_retrieved_documents(
                query,
                k=4,
                levels=levels,
                force_recreate=False,
                silent=True  # Production mode - suppress debug output
            )
            
            # Format documents for LLM
            if not retrieved_docs:
                return "Bilgi bulunamadı. Bu konuda dokümanlarımızda bilgi yok."
            
            context_parts = []
            for doc, score in retrieved_docs:
                level = doc.metadata.get('level', 'N/A').upper()
                title = doc.metadata.get('title', 'Başlıksız')
                content = doc.page_content
                
                context_parts.append(
                    f"**[{level}] {title}**\n{content}\n"
                )
            
            return "\n---\n".join(context_parts)
        
        @tool
        def search_school_news(query: str) -> str:
            """
            Okul haberleri, etkinlikler ve duyurular hakkında bilgi alır.
            
            Okulun web sitesinden güncel haber ve etkinlikleri arar.
            ⚠️ Henüz aktif değil - placeholder implementasyon.
            
            Args:
                query: Aranacak haber/etkinlik konusu (örn: "Bu hafta etkinlik var mı?")
            
            Returns:
                Haber ve etkinlik bilgileri veya placeholder mesajı
            
            Örnekler:
                - "Bu hafta etkinlik var mı?"
                - "Son haberler neler?"
                - "Yaklaşan etkinlikler"
            """
            return "🚧 Haber ve etkinlik arama özelliği henüz aktif değil. Lütfen doğrudan okul iletişim kanallarını kullanın."
        
        return [retrieve_education_info, search_school_news]
    
    def _create_agent(self):
        """LangChain v1 agent oluştur - create_agent API ile."""
        
        # System prompt - agent'e talimatlar
        system_prompt = """Siz, Çözüm Eğitim Kurumları'nın veli asistanısınız.

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
            tools=self.tools,  # ChatSession'a özel tools (closure ile levels erişimi)
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
    """Test agent locally - kademe filtreleme testi"""
    print("🤖 Multi-Tool Agent Test - Kademe Filtreleme\n")
    
    llm = initialize_chat_model()
    
    # Test 1: Sadece lise seçili
    print("=" * 80)
    print("TEST 1: Sadece LİSE kademesi seçili")
    print("=" * 80)
    session1 = ChatSession(llm)
    session1.set_levels(["lise"])
    
    response = session1.chat("İngilizce programı nasıl?")
    print(f"\n👤 Soru: İngilizce programı nasıl?")
    print(f"🎯 Kademe: {session1.levels}")
    print(f"🤖 Yanıt: {response[:200]}...")
    
    # Test 2: Sadece anaokulu seçili
    print("\n" + "=" * 80)
    print("TEST 2: Sadece ANAOKULU kademesi seçili")
    print("=" * 80)
    session2 = ChatSession(llm)
    session2.set_levels(["anaokulu"])
    
    response = session2.chat("İngilizce programı nasıl?")
    print(f"\n👤 Soru: İngilizce programı nasıl?")
    print(f"🎯 Kademe: {session2.levels}")
    print(f"🤖 Yanıt: {response[:200]}...")
    
    # Test 3: Tüm kademeler
    print("\n" + "=" * 80)
    print("TEST 3: TÜM KADEMELER seçili")
    print("=" * 80)
    session3 = ChatSession(llm)
    session3.set_levels(["anaokulu", "ilkokul", "ortaokul", "lise"])
    
    response = session3.chat("İngilizce eğitimi hakkında bilgi ver")
    print(f"\n👤 Soru: İngilizce eğitimi hakkında bilgi ver")
    print(f"🎯 Kademe: {session3.levels}")
    print(f"🤖 Yanıt: {response[:300]}...")
    
    print("\n" + "=" * 80)
