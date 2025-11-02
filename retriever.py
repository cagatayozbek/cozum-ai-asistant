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
CHUNKS_DIR = "chunks"
EMBEDDING_MODEL = "gemini-embedding-001"

# Desteklenen okul seviyeleri
SUPPORTED_LEVELS = ["anaokulu", "ilkokul", "ortaokul", "lise"]

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

def create_embedding_text(item: dict) -> str:
    """
    Chunk'tan embedding için zenginleştirilmiş metin oluşturur.
    Format: title + question + embedding_hint + content
    """
    parts = []
    
    if item.get("title"):
        parts.append(item["title"])
    
    if item.get("question"):
        parts.append(item["question"])
    
    if item.get("embedding_hint"):
        parts.append(item["embedding_hint"])
    
    if item.get("content"):
        parts.append(item["content"])
    
    return " ".join(parts)

def load_chunks_from_files(levels: list = None) -> list:
    """
    Belirtilen seviyeler için chunk'ları yükler.
    
    Args:
        levels: Yüklenecek okul seviyeleri listesi. None ise tüm seviyeler yüklenir.
    
    Returns:
        Tüm chunk'ların birleştirilmiş listesi.
    """
    if levels is None:
        levels = SUPPORTED_LEVELS
    
    all_chunks = []
    for level in levels:
        json_path = os.path.join(CHUNKS_DIR, f"{level}.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)
                all_chunks.extend(chunks)
                print(f"✓ {level}.json: {len(chunks)} chunk yüklendi")
        else:
            print(f"⚠ {json_path} bulunamadı, atlanıyor...")
    
    return all_chunks

def create_and_save_index(embedding_model: GoogleGenerativeAIEmbeddings, levels: list = None):
    """JSON'dan dokümanları okur, FAISS indeksini oluşturur ve diske kaydeder."""
    print(f"'{INDEX_PATH}' bulunamadı. Indeks sıfırdan oluşturuluyor...\n")
    
    # Tüm chunk'ları yükle
    raw_data = load_chunks_from_files(levels)
    
    if not raw_data:
        raise ValueError("Hiç chunk yüklenemedi! chunks/ klasörünü kontrol edin.")

    # Document nesneleri oluştur - zenginleştirilmiş embedding metni ile
    docs = [
        Document(
            page_content=create_embedding_text(item),
            metadata={
                "id": item.get("id"),
                "level": item.get("level"),
                "title": item.get("title"),
                "question": item.get("question"),
                "answer_type": item.get("answer_type"),
                "embedding_hint": item.get("embedding_hint"),
                "source": item.get("source"),
                "tags": item.get("tags"),
                "version": item.get("version"),
                "chunk_index": item.get("chunk_index"),
                "original_content": item.get("content")  # Orijinal içerik ayrı saklanıyor
            }
        )
        for item in raw_data
    ]
    
    print(f"\n{len(docs)} doküman için embedding oluşturuluyor ve indeksleniyor. Bu işlem zaman alabilir...")
    vectorstore = FAISS.from_documents(docs, embedding_model)
    vectorstore.save_local(INDEX_PATH)
    print(f"✓ Indeks başarıyla '{INDEX_PATH}' klasörüne kaydedildi.")
    return vectorstore

def load_vector_store(embedding_model: GoogleGenerativeAIEmbeddings, levels: list = None, force_recreate: bool = False, silent: bool = False) -> FAISS:
    """
    Mevcut FAISS indeksini diskten yükler veya yoksa yenisini oluşturur.
    
    Args:
        embedding_model: Kullanılacak embedding modeli
        levels: Yüklenecek okul seviyeleri (None ise tümü)
        force_recreate: True ise mevcut indeks silinip yeniden oluşturulur
        silent: True ise terminal çıktıları bastırılır
    
    Returns:
        FAISS vector store
    """
    if force_recreate and os.path.exists(INDEX_PATH):
        if not silent:
            print(f"⚠ Mevcut indeks siliniyor...")
        import shutil
        shutil.rmtree(INDEX_PATH)
    
    if os.path.exists(INDEX_PATH):
        if not silent:
            print(f"✓ Mevcut indeks '{INDEX_PATH}' klasöründen yükleniyor...")
        return FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)
    else:
        return create_and_save_index(embedding_model, levels)

def get_retrieved_documents(query: str, k: int = 3, levels: list = None, force_recreate: bool = False, silent: bool = False) -> list:
    """
    Verilen bir sorgu için FAISS veritabanından ilgili dokümanları ve skorlarını getirir.

    Args:
        query (str): Aranacak metin.
        k (int): Döndürülecek en benzer doküman sayısı.
        levels (list): Filtrelenecek okul seviyeleri (None ise tümü).
        force_recreate (bool): İndeksi yeniden oluştur.
        silent (bool): True ise terminal çıktıları bastırılır (chatbot kullanımı için).

    Returns:
        list: (Document, score) çiftlerinden oluşan bir liste.
    """
    try:
        embedding_model = initialize_embeddings()
        vectorstore = load_vector_store(embedding_model, levels, force_recreate, silent)
        
        if not silent:
            print(f"\n🔍 '{query}' sorgusu için en benzer {k} sonuç getiriliyor...")
        
        # Tüm sonuçları al
        results = vectorstore.similarity_search_with_score(query, k=k*2)  # Daha fazla al, filtrele
        
        # Eğer seviye filtresi varsa uygula
        if levels:
            results = [(doc, score) for doc, score in results if doc.metadata.get("level") in levels]
        
        # İstenen sayıda sonuç döndür
        return results[:k]
    except Exception as e:
        if not silent:
            print(f"❌ Retriever hatası: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(
        description="FAISS ve LangChain ile çoklu seviye RAG sorgusu yap.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python retriever.py "Anaokulunda İngilizce dersleri nasıl?"
  python retriever.py "Matematik dersleri" -k 5
  python retriever.py "Ödev politikası" --levels anaokulu ilkokul
  python retriever.py "Vizyon misyon" --recreate
        """
    )
    parser.add_argument("query", type=str, help="Vektör veritabanında aranacak sorgu.")
    parser.add_argument("-k", type=int, default=3, help="Döndürülecek en benzer doküman sayısı (varsayılan: 3).")
    parser.add_argument("--levels", nargs="+", choices=SUPPORTED_LEVELS, 
                       help="Sadece belirtilen okul seviyelerinde ara (varsayılan: tümü).")
    parser.add_argument("--recreate", action="store_true", 
                       help="FAISS indeksini yeniden oluştur (mevcut silinir).")
    args = parser.parse_args()

    try:
        print("=" * 70)
        print("🎓 Çözüm Eğitim Kurumları - RAG Retriever")
        print("=" * 70)
        
        # Seviye filtresi varsa göster
        if args.levels:
            print(f"📚 Arama kapsamı: {', '.join(args.levels)}")
        else:
            print(f"📚 Arama kapsamı: Tüm seviyeler ({', '.join(SUPPORTED_LEVELS)})")
        
        # 1. Benzerlik araması yap
        results_with_scores = get_retrieved_documents(
            args.query, 
            k=args.k, 
            levels=args.levels,
            force_recreate=args.recreate
        )

        # 2. Sonuçları yazdır
        if not results_with_scores:
            print("\n❌ Hiç sonuç bulunamadı.")
            return

        print(f"\n{'='*70}")
        print(f"📊 {len(results_with_scores)} Sonuç Bulundu")
        print(f"{'='*70}")

        for i, (doc, score) in enumerate(results_with_scores, 1):
            print(f"\n{'─'*70}")
            print(f"🔢 Sonuç {i} | 📈 Benzerlik Skoru: {score:.4f}")
            print(f"{'─'*70}")
            print(f"🏷️  ID: {doc.metadata.get('id')}")
            print(f"🎯 Seviye: {doc.metadata.get('level', 'N/A').upper()}")
            print(f"📖 Başlık: {doc.metadata.get('title')}")
            
            if doc.metadata.get('question'):
                print(f"❓ Soru: {doc.metadata.get('question')}")
            
            if doc.metadata.get('answer_type'):
                print(f"💡 Yanıt Tipi: {doc.metadata.get('answer_type')}")
            
            if doc.metadata.get('embedding_hint'):
                print(f"🔑 Anahtar Kelimeler: {doc.metadata.get('embedding_hint')}")
            
            # Orijinal içeriği göster (varsa)
            content = doc.metadata.get('original_content', doc.page_content)
            print(f"\n📄 İçerik:")
            print(content[:400] + ("..." if len(content) > 400 else ""))
            
            if doc.metadata.get('tags'):
                tags = doc.metadata.get('tags')
                if isinstance(tags, list):
                    print(f"\n🏷️  Etiketler: {', '.join(tags)}")

        print(f"\n{'='*70}")

    except Exception as e:
        print(f"\n❌ Bir hata oluştu: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()