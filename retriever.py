import os
import json
import argparse

# OMP: Error #15: Initializing libomp.dylib... hatası için macOS geçici çözümü
# Bu ayar, OpenMP kullanan herhangi bir kütüphane (örn. faiss) import edilmeden önce yapılmalıdır.
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# --- CONFIGURATION ---
INDEX_PATH = "faiss_index"
SOURCE_JSON = "anaokulu.json"
EMBEDDING_MODEL = "gemini-embedding-001"

def initialize_embeddings() -> GoogleGenerativeAIEmbeddings:
    """API anahtarını yükler ve embedding modelini başlatır."""
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY ortam değişkeni bulunamadı. .env dosyasını kontrol edin.")
    
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=google_api_key
    )

def create_and_save_index(embedding_model: GoogleGenerativeAIEmbeddings):
    """JSON'dan dokümanları okur, FAISS indeksini oluşturur ve diske kaydeder."""
    print(f"'{INDEX_PATH}' bulunamadı. Indeks sıfırdan oluşturuluyor...")
    
    with open(SOURCE_JSON, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    docs = [
        Document(
            page_content=item["content"],
            metadata={key: item.get(key) for key in ["id", "level", "title", "source", "tags", "version", "chunk_index"]}
        )
        for item in raw_data
    ]
    
    print(f"{len(docs)} doküman için embedding oluşturuluyor ve indeksleniyor. Bu işlem zaman alabilir...")
    vectorstore = FAISS.from_documents(docs, embedding_model)
    vectorstore.save_local(INDEX_PATH)
    print(f"Indeks başarıyla '{INDEX_PATH}' klasörüne kaydedildi.")
    return vectorstore

def load_vector_store(embedding_model: GoogleGenerativeAIEmbeddings) -> FAISS:
    """Mevcut FAISS indeksini diskten yükler veya yoksa yenisini oluşturur."""
    if os.path.exists(INDEX_PATH):
        print(f"Mevcut indeks '{INDEX_PATH}' klasöründen yükleniyor...")
        return FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)
    else:
        return create_and_save_index(embedding_model)

def get_retrieved_documents(query: str, k: int = 3) -> list:
    """
    Verilen bir sorgu için FAISS veritabanından ilgili dokümanları ve skorlarını getirir.

    Args:
        query (str): Aranacak metin.
        k (int): Döndürülecek en benzer doküman sayısı.

    Returns:
        list: (Document, score) çiftlerinden oluşan bir liste.
    """
    try:
        embedding_model = initialize_embeddings()
        vectorstore = load_vector_store(embedding_model)
        print(f"\n'{query}' sorgusu için en benzer {k} sonuç getiriliyor...")
        return vectorstore.similarity_search_with_score(query, k=k)
    except Exception as e:
        print(f"Retriever hatası: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description="FAISS ve LangChain ile RAG sorgusu yap.")
    parser.add_argument("query", type=str, help="Vektör veritabanında aranacak sorgu.")
    parser.add_argument("-k", type=int, default=3, help="Döndürülecek en benzer doküman sayısı.")
    args = parser.parse_args()

    try:
        # 1. Benzerlik araması yap
        results_with_scores = get_retrieved_documents(args.query, k=args.k)

        # 2. Sonuçları yazdır
        if not results_with_scores:
            print("Hiç sonuç bulunamadı.")
            return

        for i, (doc, score) in enumerate(results_with_scores, 1):
            print(f"\n--- Sonuç {i} | Benzerlik Skoru: {score:.4f} ---")
            print("Başlık:", doc.metadata.get("title"))
            print("ID:", doc.metadata.get("id"))
            print("İçerik:", doc.page_content[:350], "...")

    except Exception as e:
        print(f"\nBir hata oluştu: {e}")

if __name__ == "__main__":
    main()