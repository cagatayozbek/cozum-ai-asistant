import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from retriever import get_retrieved_documents, SUPPORTED_LEVELS

# --- CONFIGURATION ---
CHAT_MODEL = "gemini-2.0-flash-exp"
MAX_HISTORY = 5  # Son 5 mesajı hatırla

def initialize_chat_model() -> ChatGoogleGenerativeAI:
    """API anahtarını yükler ve sohbet modelini başlatır."""
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY ortam değişkeni bulunamadı. .env dosyasını kontrol edin.")
    
    return ChatGoogleGenerativeAI(
        model=CHAT_MODEL,
        google_api_key=google_api_key,
        temperature=0.7,
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

class ChatSession:
    """Sohbet oturumu yönetimi."""
    
    def __init__(self, levels: list, llm):
        self.levels = levels
        self.llm = llm
        self.history = []  # (role, message) tuple'ları
    
    def add_to_history(self, role: str, message: str):
        """Sohbet geçmişine mesaj ekler."""
        self.history.append((role, message))
        # Maksimum geçmiş sınırı
        if len(self.history) > MAX_HISTORY * 2:  # user + assistant çiftleri
            self.history = self.history[-MAX_HISTORY * 2:]
    
    def get_history_context(self) -> str:
        """Sohbet geçmişini formatlar."""
        if not self.history:
            return ""
        
        formatted = "\n--- ÖNCEKİ SOHBET ---\n"
        for role, message in self.history[-6:]:  # Son 3 çift (6 mesaj)
            formatted += f"{role}: {message}\n"
        formatted += "--- ÖNCEKİ SOHBET SONU ---\n\n"
        return formatted
    
    def clear_history(self):
        """Sohbet geçmişini temizler."""
        self.history = []
        print("\n✅ Sohbet geçmişi temizlendi.")
    
    def change_levels(self) -> list:
        """Eğitim kademelerini değiştirir."""
        print("\n🔄 Yeni kademe seçimi yapılıyor...")
        return welcome_and_get_levels()
    
    def chat(self, user_query: str) -> str:
        """Kullanıcı mesajını işler ve yanıt üretir."""
        # Retriever ile ilgili dokümanları al (silent mode)
        retrieved_docs = get_retrieved_documents(
            user_query, 
            k=4, 
            levels=self.levels,
            force_recreate=False,
            silent=True  # Chatbot modunda sessiz çalış
        )
        
        if not retrieved_docs:
            return "Üzgünüm, bu konuyla ilgili bilgi bulamadım. Başka bir konuda size nasıl yardımcı olabilirim?"
        
        # Dokümanları formatla
        context = format_context(retrieved_docs)
        history_context = self.get_history_context()
        
        # Kademe bilgisini ekle
        level_info = ", ".join([get_level_display_name(l) for l in self.levels])
        
        # Prompt oluştur
        prompt = f"""Sen Çözüm Eğitim Kurumları için tasarlanmış yapay zeka destekli bir veli asistanısın.
Görevin: Velilere okul hakkında doğru, net ve samimi bilgi vermek.

KURALLAR:
1. Yanıtlarını SADECE aşağıdaki BAĞLAM'daki bilgilere dayandır
2. BAĞLAM'da cevap yoksa: "Bu konuda şu an bilgim yok, ancak okulumuzla iletişime geçerek detaylı bilgi alabilirsiniz."
3. Asla tahmin etme veya uydurma
4. Türkçe, açık, net ve samimi bir üslup kullan (2-5 cümle)
5. Gerekirse özet yap, doğrudan alıntı yapma
6. BAĞLAM belirsizse netleştirici TEK bir kısa soru sor

VELİNİN ÇOCUKLARINDAKİ KADEMELER: {level_info}

{history_context}

--- BAĞLAM ---
{context}
--- BAĞLAM SONU ---

VELİNİN SORUSU: {user_query}

YANITINIZ (samimi, kısa ve net):"""

        # LLM'i çağır
        response = self.llm.invoke(prompt)
        
        # Geçmişe ekle
        self.add_to_history("Veli", user_query)
        self.add_to_history("Asistan", response.content)
        
        return response.content

def main():
    """Kullanıcıdan sürekli girdi alan ve RAG ile cevap üreten ana sohbet döngüsü."""
    try:
        # 1. LLM'i başlat
        llm = initialize_chat_model()
        
        # 2. Veliyi karşıla ve seviye seç
        selected_levels = welcome_and_get_levels()
        
        # 3. Sohbet oturumu başlat
        session = ChatSession(selected_levels, llm)
        
        # 4. Yardım göster
        print("\n" + "="*70)
        print("💬 Sohbet başladı! Artık sorularınızı sorabilirsiniz.")
        show_help()
        print("="*70)
        
        # 5. Ana sohbet döngüsü
        while True:
            try:
                user_input = input("\n👤 Siz: ").strip()
                
                # Boş girdi kontrolü
                if not user_input:
                    continue
                
                # Komut kontrolü
                user_input_lower = user_input.lower()
                
                if user_input_lower in ["/exit", "/cikis", "exit", "quit"]:
                    print("\n👋 Görüşmek üzere! İyi günler dileriz.")
                    break
                
                elif user_input_lower in ["/help", "/yardim"]:
                    show_help()
                    continue
                
                elif user_input_lower in ["/seviye", "/kademe"]:
                    selected_levels = session.change_levels()
                    session.levels = selected_levels
                    continue
                
                elif user_input_lower in ["/temizle", "/clear"]:
                    session.clear_history()
                    continue
                
                # Normal sohbet
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
