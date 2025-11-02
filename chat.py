import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from operator import add

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from retriever import get_retrieved_documents, SUPPORTED_LEVELS

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
        
    )

def format_context(documents: list) -> str:
    """Alınan dokümanları LLM'e verilecek tek bir metin bloğu haline getirir."""
    if not documents:
        return "Bilgi bulunamadı."
    
    context = []
    for i, (doc, score) in enumerate(documents, 1):
        level = doc.metadata.get('level', 'N/A').upper()
        title = doc.metadata.get('title', 'Başlık yok')
        content = doc.metadata.get('original_content', doc.page_content)
        context.append(f"[{level}] {title}\n{content}")
    return "\n\n---\n\n".join(context)

def get_level_display_name(level: str) -> str:
    """Seviye kodunu kullanıcı dostu isme çevirir."""
    mapping = {
        "anaokulu": "Anaokulu",
        "ilkokul": "İlkokul (1-4. Sınıf)",
        "ortaokul": "Ortaokul (5-8. Sınıf)",
        "lise": "Lise (9-12. Sınıf)"
    }
    return mapping.get(level, level)

def welcome_and_get_levels() -> list:
    """Veliyi karşılar ve çocuklarının eğitim kademelerini öğrenir."""
    print("\n" + "="*70)
    print("🎓 Çözüm Eğitim Kurumları - AI Veli Asistanı")
    print("="*70)
    print("\nMerhaba! Ben Çözüm Koleji AI asistanıyım.")
    print("Size okulumuz hakkında bilgi vermek için buradayım. 😊\n")
    
    # Seviye seçimi
    print("Lütfen çocuğunuzun/çocuklarınızın eğitim kademesini seçin:")
    print("(Birden fazla çocuğunuz varsa, virgülle ayırarak girebilirsiniz)\n")
    
    for i, level in enumerate(SUPPORTED_LEVELS, 1):
        print(f"{i}. {get_level_display_name(level)}")
    print(f"{len(SUPPORTED_LEVELS) + 1}. Tüm kademeler")
    
    while True:
        choice = input("\nSeçiminiz (örn: 1,2 veya 1): ").strip()
        
        if not choice:
            print("❌ Lütfen bir seçim yapın.")
            continue
        
        # "Tüm kademeler" seçeneği
        if choice == str(len(SUPPORTED_LEVELS) + 1):
            return SUPPORTED_LEVELS
        
        # Birden fazla seçim
        try:
            choices = [int(c.strip()) for c in choice.split(',')]
            selected_levels = []
            
            for c in choices:
                if 1 <= c <= len(SUPPORTED_LEVELS):
                    selected_levels.append(SUPPORTED_LEVELS[c - 1])
                else:
                    print(f"❌ Geçersiz seçim: {c}")
                    break
            else:
                if selected_levels:
                    print("\n✅ Seçilen kademeler:")
                    for level in selected_levels:
                        print(f"   • {get_level_display_name(level)}")
                    print("\nArtık bu kademelere özel sorular sorabilirsiniz!")
                    return selected_levels
        except ValueError:
            print("❌ Lütfen geçerli sayılar girin (örn: 1,2 veya 3)")

def show_help():
    """Yardım mesajını gösterir."""
    print("\n" + "─"*70)
    print("📝 Komutlar:")
    print("─"*70)
    print("  /help veya /yardim    - Bu yardım mesajını gösterir")
    print("  /seviye veya /kademe  - Eğitim kademesini değiştirir")
    print("  /temizle veya /clear  - Sohbet geçmişini temizler")
    print("  /cikis veya /exit     - Programdan çıkar")
    print("─"*70)

# --- GRAPH NODES ---
def retrieve_node(state: ChatState) -> dict:
    """Retrieve relevant documents based on last user message."""
    if not state.get("messages"):
        return {"context": ""}  # Return default empty context
    
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
    """Generate response using LLM with context."""
    if not state.get("messages"):
        return {}
    
    # Get last user message
    user_msg = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_msg = msg.content
            break
    
    if not user_msg:
        return {}
    
    # Get context from state (set by retrieve_node)
    context = state.get("context", "Bilgi bulunamadı.")
    
    # Build system prompt
    level_info = ", ".join([get_level_display_name(l) for l in state.get("levels", [])]) if state.get("levels") else "Henüz seçilmedi"
    
    system_prompt = f"""Sen Çözüm Eğitim Kurumları için tasarlanmış yapay zeka destekli bir veli asistanısın.
Görevin: Velilere okul hakkında doğru, net ve samimi bilgi vermek.

KURALLAR:
1. Yanıtlarını SADECE sağlanan BAĞLAM'daki bilgilere dayandır
2. Yanıtlarında KESİNLİKLE uydurma yapma
3. Asla tahmin etme veya uydurma
4. Profesyonel ve samimi bir üslup kullan

6. Kullanıcıya hitap ederken: "siz", "sizlere", "istiyorsanız" gibi saygılı ifadeler
7. Yanıtları 2-5 cümle ile sınırla, özet ver


ŞU ANDA SEÇİLİ KADEMELER: {level_info}

GENEL SORULAR İÇİN REHBERLİK:
- Eğer soru ÇOK GENEL ise (örn: "okul hakkında bilgi", "okulunuzu anlatır mısınız"):
  → BAĞLAM'dan 1-2 ilginç bilgi ver (örn: eğitim anlayışı, özellikler)
  → MUTLAKA bu listeyi göster:
  
  "Size daha detaylı hangi konuda bilgi verebilirim?
  • Eğitim programları ve müfredat
  • İngilizce ve yabancı dil eğitimi  
  • Sosyal aktiviteler ve kulüpler
  • Ücretler ve kayıt işlemleri
  • Servis ve yemek hizmetleri"

KADEME YÖNETİMİ:
- Eğer kullanıcı seçili OLMAYAN bir kademe hakkında soru sorarsa:
  → Kibarca sor: "Şu an {level_info} için bilgi verebiliyorum. [İstenenKademe] hakkında da bilgi almak ister misiniz?"
- Kullanıcı EVET derse → "Harika! [İstenenKademe] bilgilerini de ekledim. Sorunuzu tekrar sorabilirsiniz." de
  VE `#KADEME_EKLE:[kademe_adi]#` tag'i ekle (kullanıcı görmez)

Özel Tag Formatı:
- #KADEME_EKLE:anaokulu# → Anaokulu ekle
- #KADEME_EKLE:lise# → Lise ekle
- Tag'i yanıtın EN SONUNA ekle, kullanıcı görmeyecek

BAĞLAM:
{context}

VELİNİN SORUSU: {user_msg}

YANITINIZ (samimi, kısa ve net):"""
    
    # Invoke LLM with single formatted message (Gemini prefers this)
    response = llm.invoke([HumanMessage(content=system_prompt)])
    
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
        
        # Add nodes
        workflow.add_node("retrieve", retrieve_node)
        workflow.add_node("llm", lambda state: llm_node(state, self.llm))
        
        # Add edges - simple flow for now
        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "llm")
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
        print("\n✅ Sohbet geçmişi temizlendi.")
    
    def set_levels(self, levels: list[str]):
        """Set education levels in state."""
        # Simply update state with new levels
        self.graph.update_state(self.get_config(), {"levels": levels})
        print(f"\n✅ Kademeler güncellendi: {', '.join([get_level_display_name(l) for l in levels])}")
    
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
                        import re
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
            print(f"\n⚠️ Hata: {e}")
            import traceback
            traceback.print_exc()
            return f"Bir hata oluştu: {str(e)}"

def main():
    """Main CLI loop with LangGraph-based chat."""
    try:
        # 1. Initialize LLM and checkpointer
        llm = initialize_chat_model()
        checkpointer = MemorySaver()
        
        # 2. Create session
        session = ChatSession(llm, checkpointer)
        
        # 3. Welcome and select levels
        selected_levels = welcome_and_get_levels()
        session.set_levels(selected_levels)
        
        # 4. Show help
        print("\n" + "="*70)
        print("💬 Sohbet başladı! Artık sorularınızı sorabilirsiniz.")
        show_help()
        print("="*70)
        
        # 5. Main chat loop
        while True:
            try:
                user_input = input("\n👤 Siz: ").strip()
                
                if not user_input:
                    continue
                
                user_input_lower = user_input.lower()
                
                if user_input_lower in ["/exit", "/cikis", "exit", "quit"]:
                    print("\n👋 Görüşmek üzere! İyi günler dileriz.")
                    break
                
                elif user_input_lower in ["/help", "/yardim"]:
                    show_help()
                    continue
                
                elif user_input_lower in ["/seviye", "/kademe"]:
                    new_levels = welcome_and_get_levels()
                    session.set_levels(new_levels)
                    continue
                
                elif user_input_lower in ["/temizle", "/clear"]:
                    session.clear_history()
                    continue
                
                # Normal chat
                print("\n🤖 Asistan: ", end="", flush=True)
                response = session.chat(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Program sonlandırıldı. İyi günler!")
                break
            except Exception as inner_e:
                print(f"\n⚠️ Bir hata oluştu: {inner_e}")
                print("Lütfen tekrar deneyin veya /help yazarak yardım alın.")

    except KeyboardInterrupt:
        print("\n\n👋 Program sonlandırıldı.")
    except Exception as e:
        print(f"\n❌ Beklenmedik bir hata oluştu: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
