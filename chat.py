import os
from typing import Annotated, TypedDict, Literal
from enum import Enum
from dotenv import load_dotenv
from operator import add

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.documents import Document
from pydantic import BaseModel, ConfigDict, Field

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from retriever import get_retrieved_documents, SUPPORTED_LEVELS

import traceback

# --- CONFIGURATION ---
CHAT_MODEL = "gemini-2.5-flash"

# --- ENUMS ---
class RetrievalStatus(str, Enum):
    """Status for document retrieval."""
    NOT_NEEDED = "not_needed"
    PENDING = "pending"
    COMPLETED = "completed"

# --- STATE SCHEMA (TypedDict for LangGraph) ---
class ChatState(TypedDict):
    """State for the chat graph."""
    levels: list[str] | None
    messages: Annotated[list[BaseMessage], add]  # add operator appends messages
    retrieved_docs: list[tuple[Document, float]]  # RAG dokümanları (formatlanmamış)
    retrieval_status: RetrievalStatus

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


class QueryClassification(BaseModel):
    """Structured response schema for query classification."""
    model_config = ConfigDict(extra="forbid")

    category: QueryType


class LevelDetection(BaseModel):
    """Structured response for detecting education level mentions in user query."""
    model_config = ConfigDict(extra="forbid")

    detected_levels: list[str] = Field(
        default_factory=list,
        description="List of education levels mentioned (anaokulu, ilkokul, ortaokul, lise)"
    )
    should_add_to_context: bool = Field(
        default=False,
        description="Whether these levels should be added to user's context"
    )


# --- HELPER FUNCTIONS ---
def get_last_user_message(messages: list[BaseMessage]) -> str | None:
    """Sohbet geçmişinden son kullanıcı mesajını çıkar."""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    return None


def format_retrieved_context(retrieved_docs: list[tuple[Document, float]]) -> str:
    """Alınan dokümanları LLM için bağlam string'ine dönüştür."""
    if not retrieved_docs:
        return "Bilgi bulunamadı."
    
    context_parts = []
    for doc, score in retrieved_docs:
        level = doc.metadata.get('level', 'N/A').upper()
        title = doc.metadata.get('title', 'Başlık yok')
        content = doc.metadata.get('original_content', doc.page_content)
        context_parts.append(f"[{level}] {title}\n{content}")
    
    return "\n\n---\n\n".join(context_parts)


def detect_level_mentions(llm: ChatGoogleGenerativeAI, user_query: str) -> LevelDetection:
    """Kullanıcı sorgusunda kademe bahsini tespit et - yapılandırılmış LLM çıktısı kullanarak."""
    detection_prompt = f"""Kullanıcının bu sorgusunda hangi eğitim kademelerinden bahsettiğini analiz et ve bunların bağlama eklenip eklenmeyeceğine karar ver.

Kullanıcı Sorgusu: "{user_query}"

Eğitim Kademeleri:
- anaokulu 
- ilkokul (1-4. sınıf)
- ortaokul (5-8. sınıf)
- lise (9-12. sınıf)

Kurallar:
1. Sadece kullanıcı açıkça bir kademe hakkında bilgi istiyorsa tespit et
2. YENİ bir kademe soruyorlarsa should_add_to_context=true yap
3. Sadece karşılaştırma yapıyorlarsa veya zaten o kademeyi konuşuyorsanız ekleme

Örnekler:
"Lise programı nasıl?" → detected_levels: ["lise"], should_add_to_context: true
"İngilizce kaç saat?" → detected_levels: [], should_add_to_context: false
"Lise ve ortaokul karşılaştır" → detected_levels: ["lise", "ortaokul"], should_add_to_context: true

Tespit edilen kademeleri JSON nesnesi olarak döndür."""
    
    structured_detector = llm.with_structured_output(LevelDetection, method="json_schema")
    
    try:
        result = structured_detector.invoke([HumanMessage(content=detection_prompt)])
        if isinstance(result, LevelDetection):
            return result
        elif isinstance(result, dict):
            return LevelDetection(**result)
        else:
            return LevelDetection()
    except Exception:
        # Fallback to empty detection on error
        return LevelDetection()

# --- GRAPH NODES ---
def classify_query_with_llm(llm: ChatGoogleGenerativeAI, user_msg: str, recent_messages: list[BaseMessage]) -> QueryType:
    """LLM ile soru tipini sınıflandır - 3 kategori: casual, followup, question."""
    
    # Son 3 mesajdan bağlam oluştur (mevcut mesaj hariç)
    # TAM MESAJI AL - Kesme yok! Uzun AI yanıtları için kritik
    context_parts = []
    for msg in recent_messages[-3:]:
        msg_type = "Kullanıcı" if isinstance(msg, HumanMessage) else "Asistan"
        context_parts.append(f"{msg_type}: {msg.content}")
    
    conversation_history = "\n".join(context_parts) if context_parts else "İlk mesaj - takip sorusu olamaz"
    
    classification_prompt = f"""Bu mesajı TEK bir kategoriye sınıflandır:
- casual: Selamlaşma, teşekkür, veda, kimlik sorusu (merhaba, teşekkürler, hoşçakal, sen kimsin)
- followup: Önceki yanıta bağımlı takip sorusu (tek başına anlamsız)
- question: Okul hakkında bağımsız yeni soru (veri tabanı araması gerekli)

ÖNCEKİ BAĞLAM:
{conversation_history}

ŞU ANKİ MESAJ: "{user_msg}"

ANA TEST: "Bu mesaj önceki yanıt olmadan anlamlı mı?"
→ Selamlaşma/teşekkür/veda = casual
→ Kısa/belirsiz + önceki yanıta bağlı = followup
→ Spesifik okul sorusu = question

ÖRNEKLER:
"Merhaba" / "Teşekkürler" / "Sen kimsin?" → casual
"Kaç saat?" (program tartışmasından sonra) → followup
"Ücret ne kadar?" (hizmet tartışmasından sonra) → followup
"manevi eğitim var mı" → question
"İngilizce eğitimi nasıl?" → question

SADECE kategori adını döndür:"""
    
    structured_classifier = llm.with_structured_output(QueryClassification, method="json_schema")
    response = structured_classifier.invoke([HumanMessage(content=classification_prompt)])
    if isinstance(response, QueryClassification):
        classification = response.category
    elif isinstance(response, dict):
        classification = str(response.get("category", ""))
    else:
        classification = str(response)
    classification = classification.strip().lower()
    
    # Validate and fallback
    valid_classes: list[QueryType] = ["casual", "followup", "question"]
    if classification not in valid_classes:
        classification = "question"  # Güvenli taraf: retrieval yap
    
    return classification

def router_node(state: ChatState, llm: ChatGoogleGenerativeAI) -> dict:
    """Soru sınıflandırmasına göre retrieval'a veya direkt LLM'e yönlendir."""
    messages = state.get("messages", [])
    
    if not messages:
        return {
            "retrieval_status": RetrievalStatus.NOT_NEEDED
        }
    
    # Yardımcı fonksiyon ile son kullanıcı mesajını al
    last_user_msg = get_last_user_message(messages)
    if not last_user_msg:
        return {
            "retrieval_status": RetrievalStatus.NOT_NEEDED
        }
    
    # Sınıflandırıcıya son mesaj geçmişini gönder (mevcut mesaj hariç)
    recent_messages = messages[:-1] if len(messages) > 1 else []
    query_type = classify_query_with_llm(llm, last_user_msg, recent_messages)
    
    # Sıradan sohbet veya takip sorusu - retrieval atla
    if query_type in ["casual", "followup"]:
        return {
            "retrieval_status": RetrievalStatus.NOT_NEEDED
        }
    
    # Yeni soru - retrieval gerekli
    return {
        "retrieval_status": RetrievalStatus.PENDING
    }


def decide_next_node(state: ChatState) -> Literal["retrieve", "llm"]:
    """Retrieval durumuna göre sonraki node'u belirle."""
    if state.get("retrieval_status") == RetrievalStatus.PENDING:
        return "retrieve"
    return "llm"

def retrieve_node(state: ChatState) -> dict:
    """Son kullanıcı mesajına göre ilgili dokümanları getir ve state'e kaydet."""
    messages = state.get("messages", [])
    if not messages:
        return {
            "retrieved_docs": [],
            "retrieval_status": RetrievalStatus.COMPLETED
        }
    
    # Yardımcı fonksiyon ile son kullanıcı mesajını al
    last_user_msg = get_last_user_message(messages)
    if not last_user_msg or not state.get("levels"):
        return {
            "retrieved_docs": [],
            "retrieval_status": RetrievalStatus.COMPLETED
        }
    
    # Dokümanları getir (formatlamadan kaydet - LLM node'da formatlanacak)
    retrieved_docs = get_retrieved_documents(
        last_user_msg,
        k=4,
        levels=state.get("levels", []),
        force_recreate=False,
        silent=True
    )
    
    # numpy.float32 → Python float (MemorySaver serialization için)
    serializable_docs = [
        (doc, float(score)) for doc, score in retrieved_docs
    ]
    
    return {
        "retrieved_docs": serializable_docs,
        "retrieval_status": RetrievalStatus.COMPLETED
    }

def llm_node(state: ChatState, llm: ChatGoogleGenerativeAI) -> dict:
    """LLM'i çağır - sistem promptu dinamik oluştur, messages state'inden gelir."""
    if not state.get("messages"):
        return {}
    
    # State'ten dokümanları al (varsa)
    retrieved_docs = state.get("retrieved_docs", [])
    
    # Dokümanları LLM için formatla (sadece burada, state'te tutma)
    if retrieved_docs:
        context = format_retrieved_context(retrieved_docs)
    else:
        context = ""
    
    # Sistem promptunu oluştur - her çağrıda dinamik (ama messages'a ekleme!)
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
    
    # ÖNEMLI: SystemMessage sadece invoke'a gönder, state'e ekleme!
    # MemorySaver sadece HumanMessage ve AIMessage'ları saklamalı
    messages_for_llm = [
        SystemMessage(content=system_prompt),
        *state["messages"]  # State'ten gelen conversation history
    ]
    
    # LLM'i çağır
    response = llm.invoke(messages_for_llm)
    
    # SADECE AI yanıtını state'e ekle (SystemMessage DEĞİL!)
    return {"messages": [AIMessage(content=response.content)]}

class ChatSession:
    """LangGraph tabanlı sohbet oturumu yöneticisi."""
    
    def __init__(self, llm: ChatGoogleGenerativeAI, checkpointer: MemorySaver):
        self.llm = llm
        self.checkpointer = checkpointer
        self.graph = self._build_graph()
        self.thread_id = "default"  # Çok kullanıcılı senaryolar için değiştirilebilir
    
    def _build_graph(self) -> StateGraph:
        """LangGraph iş akışını oluştur."""
        # Graph oluştur
        workflow = StateGraph(ChatState)
        
        # Node'ları ekle
        workflow.add_node("router", lambda state: router_node(state, self.llm))
        workflow.add_node("retrieve", retrieve_node)
        workflow.add_node("llm", lambda state: llm_node(state, self.llm))
        
        # Edge'leri ekle
        workflow.add_edge(START, "router")
        
        # Conditional edge: router'dan sonra retrieval gerekli mi?
        workflow.add_conditional_edges(
            "router",
            decide_next_node,  # Karar fonksiyonu
            {
                "retrieve": "retrieve",  # PENDING ise retrieval'a git
                "llm": "llm"  # NOT_NEEDED ise direkt LLM'e git
            }
        )
        
        workflow.add_edge("retrieve", "llm")  # Retrieve sonrası LLM'e git
        workflow.add_edge("llm", END)
        
        # Checkpointer ile derle
        return workflow.compile(checkpointer=self.checkpointer)
    
    def get_config(self):
        """thread_id ile konfigürasyon al."""
        return {"configurable": {"thread_id": self.thread_id}}
    
    def get_state(self) -> dict:
        """Mevcut state'i dict olarak al."""
        state = self.graph.get_state(self.get_config())
        if state and state.values:
            # Tüm key'lerin varsayılanlarını garanti et
            values = state.values
            return {
                "levels": values.get("levels"),
                "messages": values.get("messages", []),
                "retrieved_docs": values.get("retrieved_docs", [])
            }
        return {"levels": None, "messages": [], "retrieved_docs": []}

    def draw_graph_mermaid(self) -> str:
        """Graph yapısını Mermaid diyagram olarak döndür."""
        return self.graph.get_graph().draw_mermaid()

    def draw_graph_png(self, output_path: str) -> None:
        """Graph'ı verilen yola PNG dosyası olarak çiz."""
        self.graph.get_graph().draw_png(output_path)
    
    def clear_history(self):
        """Thread'i sıfırlayarak sohbet geçmişini temizle."""
        self.thread_id = f"thread_{os.urandom(8).hex()}"
    
    def set_levels(self, levels: list[str]):
        """State'te eğitim kademelerini ayarla."""
        # Basitçe state'i yeni kademelerle güncelle
        self.graph.update_state(self.get_config(), {"levels": levels})
    
    def chat(self, user_query: str) -> str:
        """Kullanıcı mesajını gönder ve yanıt al."""
        try:
            # İşlemeden önce kademe bahsini tespit et
            level_detection = detect_level_mentions(self.llm, user_query)
            
            # Gerekirse tespit edilen kademeleri bağlama ekle
            if level_detection.should_add_to_context and level_detection.detected_levels:
                current_state = self.get_state()
                current_levels = list(current_state.get("levels") or [])
                
                levels_added = []
                for level in level_detection.detected_levels:
                    level = level.lower()
                    if level in SUPPORTED_LEVELS and level not in current_levels:
                        current_levels.append(level)
                        levels_added.append(level)
                
                # State'i yeni kademelerle güncelle
                if levels_added:
                    self.graph.update_state(self.get_config(), {"levels": current_levels})
            
            # Mesajı graph üzerinden işle
            result = self.graph.invoke(
                {"messages": [HumanMessage(content=user_query)]},
                self.get_config()
            )
            
            # Sonuçtan son AI mesajını çıkar
            if result and "messages" in result:
                for msg in reversed(result["messages"]):
                    if isinstance(msg, AIMessage):
                        return msg.content
            
            return "Üzgünüm, bir yanıt üretemedim. Lütfen sorunuzu farklı şekilde sormayı deneyin."
        
        except Exception as e:
            traceback.print_exc()
            return "Üzgünüm, teknik bir sorun oluştu. Lütfen tekrar deneyin."

# CLI için main() fonksiyonu kaldırıldı
# Production'da Streamlit (app.py) kullanılıyor

# --- GRAPH VISUALIZATION ---
if __name__ == "__main__":
    """Graph yapısını görselleştir - development amaçlı"""
    print("🎨 LangGraph yapısı oluşturuluyor...")
    
    # LLM ve checkpointer oluştur
    llm = initialize_chat_model()
    checkpointer = MemorySaver()
    
    # ChatSession oluştur
    session = ChatSession(llm, checkpointer)
    
    # PNG olarak kaydet
    output_path = "langgraph_visualization.png"
    try:
        session.draw_graph_png(output_path)
        print(f"✅ Graph başarıyla kaydedildi: {output_path}")
    except Exception as e:
        print(f"❌ PNG oluşturulamadı: {e}")
        print("💡 Not: 'pygraphviz' veya 'graphviz' kurulu olmalı")
        print("   macOS: brew install graphviz && pip install pygraphviz")
    
    # Mermaid diyagramı da yazdır
    print("\n📊 Mermaid Diyagram:")
    print("=" * 70)
    print(session.draw_graph_mermaid())
    print("=" * 70)
