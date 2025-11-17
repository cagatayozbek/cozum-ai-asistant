"""
Multi-Tool Agent Architecture
Çözüm Koleji Veli Asistanı - Simplified LangChain Agent
"""

import os
from dotenv import load_dotenv
import traceback

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

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
    
    def __init__(self, llm: ChatGoogleGenerativeAI, checkpointer: InMemorySaver = None):
        self.llm = llm
        self.checkpointer = checkpointer or InMemorySaver()
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
        
        # Aktif kademeleri belirle (dinamik)
        active_levels = ', '.join(self.levels).title() if self.levels else "Tüm kademeler"
        
        # System prompt - agent'e talimatlar
        system_prompt = f"""Siz, Çözüm Eğitim Kurumları'nın veli asistanısınız.

AKTİF KADEMELER: {active_levels}

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
5) ÖNEMLİ: Kademe değiştiğinde veya yeni bilgi istendiğinde MUTLAKA aracı tekrar çağırın

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
        """Eğitim kademelerini ayarla ve agent'i yeniden oluştur."""
        old_levels = self.levels
        self.levels = levels
        
        # ✨ Agent'i yeniden oluştur (system prompt'ta kademe bilgisi var)
        if old_levels != levels:
            self.agent = self._create_agent()
        
        # Eğer kademe değiştiyse, conversation history'ye not ekle
        if old_levels != levels and old_levels is not None:
            self.conversation_history.append({
                "role": "assistant",
                "content": f"✅ Kademe güncellendi: {', '.join(levels)}. Bundan sonraki sorularınız için sadece bu kademe(ler)den bilgi getireceğim."
            })
    
    def clear_history(self):
        """Sohbet geçmişini temizle."""
        self.conversation_history = []
        self.thread_id = f"thread_{os.urandom(8).hex()}"
    
    def chat(self, user_query: str) -> str:
        """Kullanıcı mesajını gönder ve yanıt al.
        
        MEMORY OPTIMIZATION: Sliding window approach
        - Sadece son 10 mesajı LLM'e gönderir (5 user + 5 assistant)
        - Tüm geçmiş self.conversation_history'de saklanır (UI için)
        - Token kullanımı sabit kalır (~2000 token max)
        """
        try:
            # 🎯 SLIDING WINDOW: Sadece son 10 mesajı al (son 5 soru-cevap çifti)
            recent_history = self.conversation_history[-10:] if len(self.conversation_history) > 10 else self.conversation_history
            
            # 1️⃣ Dinamik kademe bilgisi için SystemMessage oluştur
            active_levels = ', '.join(self.levels).title() if self.levels else "Tüm kademeler"
            system_message = SystemMessage(
                content=f"🎯 AKTİF KADEMELER: {active_levels}\n\n"
                        f"Kullanıcının seçtiği kademe(ler) bunlardır. Araçlar otomatik olarak bu kademelerde arama yapar."
            )
            
            # 🐛 DEBUG: Show sliding window size
            print(f"\n💬 [CHAT] Soru soruldu")
            print(f"   Toplam geçmiş: {len(self.conversation_history)} mesaj")
            print(f"   LLM'e gönderilen: {len(recent_history)} mesaj (sliding window)")
            print(f"   Aktif kademeler: {self.levels}")
            
            # 2️⃣ Son N mesajı LangChain message formatına çevir
            messages = [system_message]  # Başa SystemMessage ekle
            
            for msg in recent_history:
                if isinstance(msg, dict):
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg.get("role") == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            
            # 3️⃣ Yeni kullanıcı mesajını ekle
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


# Test
if __name__ == "__main__":
    """Test: Kademe değişikliği senaryosu"""
    print("🤖 Kademe Değişikliği Testi\n")
    
    llm = initialize_chat_model()
    session = ChatSession(llm)
    
    # 1. Ortaokul
    print("1️⃣ ORTAOKUL seçildi")
    session.set_levels(["ortaokul"])
    response1 = session.chat("İngilizce ders saatleri nelerdir")
    print(f"Yanıt: {response1[:150]}...\n")
    
    # 2. Lise'ye değiştir
    print("2️⃣ LİSE'ye değiştirildi")
    session.set_levels(["lise"])
    response2 = session.chat("İngilizce ders saatleri nelerdir")
    print(f"Yanıt: {response2[:150]}...")
    
    # Kontrol
    if "ortaokul" in response2.lower() and "lise" in response2.lower():
        print("\n❌ SORUN VAR: HEM ortaokul HEM lise bilgisi var!")
    elif "lise" in response2.lower():
        print("\n✅ SORUN YOK: Sadece lise bilgisi var!")
    else:
        print("\n⚠️ BEKLENMEDIK: Ne ortaokul ne de lise bilgisi yok?")
