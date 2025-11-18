"""
Intent Detection Module
Kullanıcı sorgusunu sınıflandırarak doğru node'a yönlendirir
"""

from typing import Literal
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI


# Intent tipleri
IntentType = Literal["greeting", "education", "event", "price", "unknown"]


class IntentDetection(BaseModel):
    """Intent detection yapılandırılmış çıktısı."""
    intent: IntentType = Field(
        description="Kullanıcı sorgusunun intent tipi"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Intent tespitinin güven skoru (0-1 arası)"
    )
    reasoning: str = Field(
        description="Bu intent'i neden seçtiğinin kısa açıklaması"
    )


# Intent classification prompt
INTENT_DETECTION_PROMPT = """Sen bir intent sınıflandırıcısısın. Kullanıcının sorgusunu analiz edip aşağıdaki kategorilerden birine ata:

**INTENT KATEGORİLERİ:**

1. **greeting** - Selamlaşma, teşekkür, hoşçakal
   Örnekler: "Merhaba", "Günaydın", "Teşekkürler", "Hoşça kal"

2. **education** - Eğitim programları, dersler, aktiviteler, okul bilgileri
   Örnekler: 
   - "İngilizce eğitimi nasıl?"
   - "Lise programı nedir?"
   - "Spor faaliyetleri var mı?"
   - "Ders saatleri nedir?"
   - "Anaokulunda hangi etkinlikler var?"

3. **event** - Güncel haberler, etkinlikler, duyurular, takvim, "düzenlenen/yapılan" etkinlikler
   Örnekler:
   - "Bu hafta etkinlik var mı?"
   - "Son haberler neler?"
   - "Yaklaşan etkinlikler?"
   - "Okul tatili ne zaman?"
   - "Okulda hangi etkinlikler düzenlendi?"
   - "Geçen ay ne gibi etkinlikler oldu?"

4. **price** - Ücret, fiyat, kayıt, finansal sorular

5. **unknown** - Yukarıdaki kategorilere uymayan, belirsiz veya okul dışı sorular
   Örnekler:
   - "Hava nasıl?"
   - "Futbol maçı kim kazandı?"
   - Anlaşılamayan veya çok belirsiz sorular

**KURALLAR:**
- Eğitim programı, ders, aktivite tanımı → **education**
- **DİKKAT:** "Düzenlenen/yapılan/geçmiş etkinlikler" → **event** (haber arar)
- Fiyat/ücret kelimeleri → **price**
- Güncel haber/duyuru/takvim → **event**
- Merhaba/teşekkür → **greeting**
- Emin değilsen → **unknown**

**ÖNEMLİ:** 
- Kullanıcı hem selamlaşıp hem soru sorarsa (örn: "Merhaba, İngilizce eğitimi nasıl?") → **education** seç (soru öncelikli)
- Sadece "Merhaba" → **greeting**
- Confidence: 0.9+ eğer çok eminsen, 0.6-0.8 arası belirsizse, 0.5 altı bilinmiyorsa

Şimdi kullanıcının sorgusunu analiz et:

KULLANICI SORGUSU: {query}

Intent, confidence ve reasoning döndür."""


def detect_intent(
    llm: ChatGoogleGenerativeAI, 
    query: str
) -> IntentDetection:
    """
    Kullanıcı sorgusunun intent'ini tespit eder.
    
    Args:
        llm: LangChain ChatGoogleGenerativeAI modeli
        query: Kullanıcının sorusu
    
    Returns:
        IntentDetection: intent, confidence, reasoning içeren yapılandırılmış çıktı
    
    Examples:
        >>> detect_intent(llm, "Merhaba")
        IntentDetection(intent='greeting', confidence=0.95, reasoning='Basit selamlaşma')
        
        >>> detect_intent(llm, "İngilizce kaç saat?")
        IntentDetection(intent='education', confidence=0.9, reasoning='Ders saati sorusu')
    """
    # Structured output için LLM'i yapılandır
    structured_llm = llm.with_structured_output(IntentDetection)
    
    # Prompt ile intent detection
    prompt_text = INTENT_DETECTION_PROMPT.format(query=query)
    result = structured_llm.invoke(prompt_text)
    
    return result


def format_intent_result(detection: IntentDetection) -> str:
    """Intent detection sonucunu okunabilir formatta döndürür (debug için)."""
    return f"Intent: {detection.intent} | Confidence: {detection.confidence:.2f} | Reasoning: {detection.reasoning}"


# Test
if __name__ == "__main__":
    from chat import initialize_chat_model
    
    print("🧪 Intent Detection Test\n")
    
    llm = initialize_chat_model()
    
    test_queries = [
        "Merhaba",
        "İngilizce eğitimi nasıl?",
        "Bu hafta etkinlik var mı?",
        "Ücretler ne kadar?",
        "Hava nasıl?",
        "Merhaba, lise programı nedir?"  # Mixed: selamlaşma + soru
    ]
    
    for query in test_queries:
        print(f"📝 Query: '{query}'")
        result = detect_intent(llm, query)
        print(f"   {format_intent_result(result)}\n")
