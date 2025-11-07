"""
Tools for Multi-Tool Agent Architecture
Çözüm Koleji Veli Asistanı - LangChain Tool Definitions
"""

from langchain.tools import tool
from retriever import get_retrieved_documents, SUPPORTED_LEVELS
from typing import Optional


@tool
def retrieve_education_info(query: str, levels: Optional[list[str]] = None) -> str:
    """
    Eğitim programları, ders saatleri, İngilizce eğitimi, spor aktiviteleri hakkında bilgi alır.
    
    FAISS vector store'dan semantik arama yaparak okul eğitim dokümanlarından bilgi getirir.
    
    Args:
        query: Kullanıcının sorusu (örn: "Lise İngilizce programı nasıl?")
        levels: Eğitim kademeleri listesi - anaokulu, ilkokul, ortaokul, lise (opsiyonel)
    
    Returns:
        Formatlanmış doküman içerikleri veya "Bilgi bulunamadı" mesajı
    
    Örnekler:
        - "Lise programı nedir?"
        - "İngilizce kaç saat?"
        - "Spor faaliyetleri neler?"
        - "Ders saatleri nasıl?"
    """
    # Varsayılan olarak tüm kademelerde ara
    if not levels:
        levels = list(SUPPORTED_LEVELS)
    
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
        title = doc.metadata.get('title', 'Başlık yok')
        content = doc.metadata.get('original_content', doc.page_content)
        context_parts.append(f"[{level}] {title}\n{content}")
    
    return "\n\n---\n\n".join(context_parts)


@tool
def search_school_news(query: str) -> str:
    """
    Okul etkinlikleri, haberler, duyurular hakkında güncel bilgi alır.
    
    Okulun web sitesinden güncel haberleri ve etkinlikleri çeker.
    
    Args:
        query: Kullanıcının sorusu (örn: "Bu hafta etkinlik var mı?")
    
    Returns:
        Güncel haberler ve etkinlikler listesi
    
    Örnekler:
        - "Bu hafta etkinlik var mı?"
        - "Yaklaşan duyurular neler?"
        - "Okul haberleri"
        - "Etkinlik takvimi"
    
    NOT: Bu tool henüz implement edilmedi. Placeholder döndürüyor.
    """
    # TODO: Web scraping implementasyonu
    # import requests
    # from bs4 import BeautifulSoup
    # 
    # url = "https://cozumkoleji.com/haberler"
    # response = requests.get(url)
    # soup = BeautifulSoup(response.text, 'html.parser')
    # ...
    
    return """Üzgünüm, okul haberlerini çekme özelliği henüz aktif değil.
    
Güncel etkinlikler ve duyurular için lütfen okulumuzun resmi web sitesini ziyaret edin:
https://cozumkoleji.com

Veya doğrudan okul yönetimi ile iletişime geçin."""


# Tool listesi - agent'e verilecek
AVAILABLE_TOOLS = [retrieve_education_info, search_school_news]
