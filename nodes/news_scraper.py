"""
NEWS SCRAPER + SEARCH NODE
1. Scraper fonksiyonları: Çözüm Koleji web sitesinden haber listesi ve detay çeker
2. LangGraph node: Kullanıcı sorgusuyla haberleri arar ve context'e ekler
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import urllib.parse

# ChatState import sadece LangGraph node için gerekli
# __main__ test bloğunda kullanılmaz
try:
    from state_schema import ChatState
except ImportError:
    ChatState = None  # Test modunda gerekmiyor


# ============================================================================
# SCRAPER FUNCTIONS
# ============================================================================

def scrape_news_list(url: str) -> list:
    """
    Çözüm Koleji duyurular liste sayfasından:
    - image
    - title
    - summary
    - detail_url
    - date
    döndüren scraper.
    """
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        return {"error": f"Liste sayfası alınamadı: {e}"}
    
    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.select("div.col-md-12.mb-4.animated.fadeIn")
    results = []

    for item in items:
        # Ana kart
        card = item.select_one(".card-archive-item")
        if not card:
            continue
        
        # GÖRSEL (background-image içinde)
        img_div = card.select_one(".card__imagery")
        image_url = None
        if img_div and "style" in img_div.attrs:
            match = re.search(r'url\((.*?)\)', img_div["style"])
            if match:
                image_url = match.group(1)

        # BAŞLIK
        title_tag = card.select_one(".card__title a")
        title = title_tag.get_text(strip=True) if title_tag else None
        
        # DETAY LINK
        detail_url = title_tag["href"] if title_tag else None

        # AÇIKLAMA (en uzun olan d-none d-md-block)
        summary_tag = card.select_one(".card__body.d-none.d-md-block")
        summary = summary_tag.get_text(strip=True) if summary_tag else None

        # TARİH
        date_tag = card.select_one(".card__date span.d-none.d-md-block")
        if date_tag:
            date_text = date_tag.get_text(strip=True)
            # "Eklenme Tarihi:" kısmını temizle
            date_text = date_text.replace("Eklenme Tarihi:", "").strip()
        else:
            date_text = None
        
        results.append({
            "title": title,
            "summary": summary,
            "image": image_url,
            "detail_url": detail_url,
            "date": date_text
        })
    
    return results


def scrape_news_detail(url: str) -> dict:
    """
    Çözüm Koleji haber detay sayfasından
    - fotoğraf
    - başlık
    - içerik (HTML -> temiz text)
    
    döndüren scraper.
    
    NOT: Bazı haberlerde tek <p> var (title + content birleşik),
    bazılarında ayrı. Her ikisi de handle edilir.
    """
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        return {"error": f"Sayfa çekilemedi: {e}"}
    
    soup = BeautifulSoup(r.text, "html.parser")
    
    page_detail = soup.select_one("div.page-detail")
    if not page_detail:
        return {"error": "page-detail div bulunamadı"}

    # FOTO
    img_tag = page_detail.select_one(".news-image img")
    image_url = img_tag["src"] if img_tag and img_tag.has_attr('src') else None

    # BAŞLIK + İÇERİK
    p_tags = page_detail.select(".not-content p")
    if not p_tags:
        return {"error": "not-content altında p etiketi yok"}
    
    # Tek <p> durumu (title + content birlikte)
    if len(p_tags) == 1:
        full_text = p_tags[0].get_text(strip=True)
        # İlk cümleyi title olarak al (nokta veya ilk 100 karakter)
        if '.' in full_text[:150]:
            first_sentence_end = full_text.find('.', 0, 150) + 1
            title = full_text[:first_sentence_end].strip()
            content = full_text[first_sentence_end:].strip()
        else:
            # Nokta yoksa ilk 100 karakteri title yap
            title = full_text[:100] + "..." if len(full_text) > 100 else full_text
            content = full_text
    else:
        # Çoklu <p> durumu (klasik: ilk p = title, geri kalanlar = content)
        title = p_tags[0].get_text(strip=True)
        content_paragraphs = [p.get_text(strip=True) for p in p_tags[1:]]
        content = "\n\n".join(content_paragraphs)

    return {
        "title": title,
        "image": image_url,
        "content": content,
    }


# ============================================================================
# LANGGRAPH NODE
# ============================================================================


def news_search_node(state: ChatState) -> ChatState:
    """
    Kullanıcının sorusunu title parametresi olarak kullanarak
    Çözüm Koleji duyurular sayfasından haber listesi çeker.
    
    İlk 3 haberin DETAYLARINI da çekip full content ile birlikte
    LLM'e gönderir (daha zengin context).
    
    Sonuçları JSON string olarak state["retrieved_context"] içine yazar.
    """
    query = state.get("user_query", "").strip()

    if not query:
        state["retrieved_context"] = "Haber araması yapılamadı: user_query boş."
        return state

    print("\n📰 [NEWS SEARCH NODE] Haber araması başlıyor...")
    print(f"   🔍 Sorgu: {query}")

    # Kullanıcı sorusunu URL title parametresi haline getir
    encoded_title = urllib.parse.quote(query)

    # API-like endpoint (bu çalışıyor)
    base_url = "https://www.cozumkoleji.com.tr/icerik/duyurular/liste"
    url = f"{base_url}?title={encoded_title}&year="

    print(f"   🌐 Fetching URL: {url}")

    # Scraper'ı çalıştır
    data = scrape_news_list(url)

    # Error case
    if isinstance(data, dict) and "error" in data:
        print("   ❌ Scraper hata verdi:", data["error"])
        state["retrieved_context"] = f"Scraper error: {data['error']}"
        return state

    # Eğer sonuç yoksa FALLBACK: Genel sorgu (tüm haberler)
    if len(data) == 0:
        print("   ⚠️  Spesifik sonuç yok, tüm haberler çekiliyor...")
        fallback_url = f"{base_url}?title=&year="
        data = scrape_news_list(fallback_url)
        
        # Fallback da başarısız olursa
        if isinstance(data, dict) and "error" in data:
            print("   ❌ Fallback de başarısız:", data["error"])
            state["retrieved_context"] = "Haber listesi alınamadı."
            return state
        
        if len(data) == 0:
            print("   ❌ Hiç haber bulunamadı (fallback).")
            state["retrieved_context"] = "Şu anda görüntülenebilecek duyuru bulunmuyor."
            return state
        
        print(f"   ✅ Fallback başarılı: {len(data)} haber bulundu")

    # İlk 3 haberi alalım (detay çekmek için)
    top_items = data[:3]

    print(f"   ✅ {len(top_items)} haber bulundu, detayları çekiliyor...")

    # LLM'e gönderilecek zengin context
    news_context = []

    for idx, item in enumerate(top_items, 1):
        detail_url = item.get("detail_url")
        
        # Detay sayfasını çek
        if detail_url:
            print(f"   📄 {idx}/{len(top_items)}: {item['title'][:50]}...")
            detail_data = scrape_news_detail(detail_url)
            
            if "error" in detail_data:
                # Detay çekilemezse sadece özet kullan
                print(f"      ⚠️  Detay çekilemedi, özet kullanılıyor")
                news_context.append({
                    "title": item["title"],
                    "summary": item["summary"],
                    "date": item["date"],
                    "url": detail_url,
                    "image": item["image"],
                    "content": None  # Detay yok
                })
            else:
                # Full content ile birlikte ekle
                content_preview = detail_data["content"][:100] + "..." if len(detail_data["content"]) > 100 else detail_data["content"]
                print(f"      ✅ Detay çekildi ({len(detail_data['content'])} karakter)")
                
                news_context.append({
                    "title": detail_data["title"],
                    "summary": item["summary"],  # Liste'den gelen özet
                    "date": item["date"],
                    "url": detail_url,
                    "image": detail_data["image"],
                    "content": detail_data["content"]  # ← FULL CONTENT!
                })
        else:
            # URL yoksa sadece liste bilgisiyle ekle
            news_context.append({
                "title": item["title"],
                "summary": item["summary"],
                "date": item["date"],
                "url": None,
                "image": item["image"],
                "content": None
            })

    print(f"   🎯 {len(news_context)} haber detayı LLM'e gönderiliyor")

    # State'e ekle (stringify)
    state["retrieved_context"] = json.dumps(news_context, ensure_ascii=False, indent=2)

    return state

# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TEST 1: DUYURU LİSTESİ")
    print("="*80)
    test_list_url = "https://www.cozumkoleji.com.tr/icerik/duyurular/liste?title=çözüm&year="
    data_list = scrape_news_list(test_list_url)
    
    if isinstance(data_list, dict) and "error" in data_list:
        print(f"❌ HATA: {data_list['error']}")
    else:
        print(f"✅ {len(data_list)} duyuru bulundu\n")
        for i, item in enumerate(data_list[:3], 1):
            print(f"{i}. {item['title']}")
            print(f"   📅 {item['date']}")
            print(f"   🔗 {item['detail_url']}")
            print(f"   📝 {item['summary'][:80] if item['summary'] else '(özet yok)'}...")
            print()
    
    print("\n" + "="*80)
    print("TEST 2: DUYURU DETAYI")
    print("="*80)
    test_detail_url = "https://www.cozumkoleji.com.tr/tr/duyuru/744/lgs-yks-hazirlik-kampimiz-tum-hiziyla-basladi"
    data_detail = scrape_news_detail(test_detail_url)
    
    if "error" in data_detail:
        print(f"❌ HATA: {data_detail['error']}")
    else:
        print(f"✅ Başlık: {data_detail['title']}")
        print(f"🖼️  Görsel: {data_detail['image']}")
        print(f"📄 İçerik ({len(data_detail['content'])} karakter):")
        print(data_detail['content'][:200] + "...")

    print("\n" + "="*80)
    print("TEST 3: NEWS_SEARCH_NODE (FULL WORKFLOW)")
    print("="*80)
    
    # Mock state (genel sorgu - boş title ile tüm haberler)
    mock_state = {
        "user_query": "çözüm",  # Çalışan bir sorgu (TEST 1'deki gibi)
        "retrieved_context": ""
    }
    
    result_state = news_search_node(mock_state)
    
    print("\n📋 LLM'E GÖNDERİLEN CONTEXT:")
    print("="*80)
    
    context_data = json.loads(result_state["retrieved_context"])
    
    for idx, item in enumerate(context_data, 1):
        print(f"\n{idx}. {item['title']}")
        print(f"   📅 {item['date']}")
        print(f"   🔗 {item.get('url', 'URL yok')}")
        
        if item.get("content"):
            content_len = len(item["content"])
            preview = item["content"][:150] + "..." if content_len > 150 else item["content"]
            print(f"   ✅ Full Content ({content_len} karakter):")
            print(f"      {preview}")
        else:
            print(f"   ⚠️  Sadece özet:")
            print(f"      {item['summary'][:100]}...")
    
    print("\n" + "="*80)
    print("✅ TÜM TESTLER TAMAMLANDI")
    print("="*80)
