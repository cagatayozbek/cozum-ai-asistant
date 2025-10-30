import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from retriever import get_retrieved_documents

# --- CONFIGURATION ---
CHAT_MODEL = "gemini-2.0-flash"

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
    context = []
    for i, (doc, score) in enumerate(documents, 1):
        context.append(f"--- Kaynak {i} (Benzerlik: {score:.4f}) ---\n{doc.page_content}")
    return "\n\n".join(context)

def main():
    """Kullanıcıdan sürekli girdi alan ve RAG ile cevap üreten ana sohbet döngüsü."""
    try:
        llm = initialize_chat_model()
        print("Sohbet modeli hazır. Çıkmak için 'exit' veya 'quit' yazın.")

        while True:
            user_query = input("\nSiz: ")
            if user_query.lower() in ["exit", "quit"]:
                print("Görüşmek üzere!")
                break

            # 1. Retriever ile ilgili dokümanları al
            retrieved_docs = get_retrieved_documents(user_query, k=4)
            if not retrieved_docs:
                print("Bot: Üzgünüm, bu konuyla ilgili bir bilgi bulamadım.")
                continue

            # 2. Dokümanları LLM için formatla
            context = format_context(retrieved_docs)

            # 3. Prompt'u oluştur
            prompt = f"""Sen Çözüm Koleji hakkında bilgi vermek için tasarlanmış bir veli asistanısın.
Yanıtlarını SADECE aşağıdaki BAĞLAM’daki bilgilere dayandır.
BAĞLAM’da cevap yoksa aynen şunu söyle: “Bu konuda bilgim yok.” Tahmin etme, dış bilgi kullanma.

Yanıt Üslubu:
- Türkçe, kısa, açık, hafif sıcak ve samimi (1–4 cümle).
- Gerekliyse doğrudan alıntı yerine özlü bir özet yaz.
- BAĞLAM birden çok olası yanıt içeriyorsa netleştirmek için yalnızca bir kısa soru sor (ör. “Hangi kampüs/seviye?”).

--- BAĞLAM ---
{context}
--- BAĞLAM SONU ---

SORU: {user_query}

CEVAP:"""
            # 4. LLM'i çağır ve cevabı yazdır
            print("Bot: Düşünüyorum...")
            response = llm.invoke(prompt)
            print("Bot:", response.content)

    except Exception as e:
        print(f"\nBeklenmedik bir hata oluştu: {e}")

if __name__ == "__main__":
    main()
