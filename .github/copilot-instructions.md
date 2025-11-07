# Çözüm Koleji Veli Asistanı - AI Coding Agent Instructions

## Project Overview

A RAG-powered parent assistant chatbot for Çözüm Koleji (Turkish school system) built with **Streamlit + LangGraph + FAISS + Google Gemini 2.5 Flash**. The system provides accurate, document-grounded answers about school programs across 4 education levels (anaokulu, ilkokul, ortaokul, lise) while avoiding hallucinations.

**Production Entry:** `streamlit run app.py` (NOT chat.py - that's deprecated CLI)

## Mimari: LangGraph ile Conditional Edge Pattern

```
User Query (Streamlit)
  → Router Node (LLM sınıflandırma)
    |
    ├─ decide_next_node() [CONDITIONAL EDGE]
    |    |
    |    ├─ casual/followup → "llm" (FAISS atla)
    |    └─ question → "retrieve" → "llm"
    |
    → LLM Response
```

**Kritik Dosyalar:**

- `app.py` - Streamlit UI ve session yönetimi (PRODUCTION)
- `chat.py` - LangGraph workflow: `ChatSession` sınıfı, router/retrieve/llm node'ları
- `retriever.py` - FAISS vector store, chunk yükleme, embedding oluşturma

### Ana Tasarım Kararı: Conditional Edge ile Akıllı Yönlendirme

**Neden Conditional Edge?**

- ✅ Profesyonel LangGraph pattern
- ✅ State-based karar verme (`RetrievalStatus` enum)
- ✅ `Command` pattern'den daha temiz ve anlaşılır
- ✅ Graph yapısı net görünür

**Nasıl Çalışır:**

1. `router_node()` - Sorguyu sınıflandır, `retrieval_status` ayarla
2. `decide_next_node()` - Status'a göre sonraki node'u belirle
3. `add_conditional_edges()` - Dinamik yönlendirme

**Neden FAISS atlanır:**

- Selamlaşma ("merhaba") → `NOT_NEEDED` → Direkt LLM
- Takip soruları ("Kaç saat?") → `NOT_NEEDED` → Mevcut context kullan
- Yeni sorular → `PENDING` → FAISS retrieval yap

## Data Structure: Pre-chunked JSON

Documents are **manually chunked** into JSON files (not auto-chunked at runtime):

- `chunks/{level}.json` - Each chunk has: `id`, `title`, `question`, `content`, `embedding_hint`, `tags`
- `embedding_hint` - Critical field for semantic search quality (included in embedding text)
- `original_content` - Stored separately in metadata (not embedded)

**Embedding Strategy (retriever.py:create_embedding_text):**

```python
embedding_text = title + question + embedding_hint + content
```

This enrichment improves retrieval accuracy.

## State Management: LangGraph + MemorySaver

**State Schema (ChatState in chat.py):**

```python
{
    "levels": list[str] | None,  # Seçili eğitim kademeleri
    "messages": list[BaseMessage],  # Tam sohbet geçmişi (with 'add' operator)
    "retrieved_docs": list[tuple[Document, float]],  # RAG dokümanları (formatlanmamış)
    "retrieval_status": RetrievalStatus  # PENDING | COMPLETED | NOT_NEEDED
}
```

**Profesyonel Memory Pattern (LangGraph Best Practice):**

- ✅ **State'te sadece raw data** - `retrieved_docs` formatlanmamış halde
- ✅ **SystemMessage state'e eklenmiyor** - Her çağrıda dinamik oluşturuluyor
- ✅ **Context injection LLM node'da** - `llm_node()` içinde format + inject
- ✅ **MemorySaver sadece messages'ı saklıyor** - HumanMessage ve AIMessage (SystemMessage değil)

**Neden Bu Yaklaşım?**

1. **Verimli storage** - SystemMessage her mesajda çoğaltılmıyor
2. **Dinamik promptlar** - `levels` değiştiğinde prompt otomatik güncelleniyor
3. **Temiz state** - Raw data state'te, formatlanmış data sadece LLM çağrısında
4. **LangGraph standardı** - Dokümanların önerdiği pattern

**Retrieval Status Pattern:** Uses enum instead of magic strings for clean state management:

- `RetrievalStatus.PENDING` - Router marked query as needing retrieval
- `RetrievalStatus.COMPLETED` - Documents retrieved and formatted
- `RetrievalStatus.NOT_NEEDED` - Casual/follow-up query, skip FAISS

**Session Persistence:** Uses `MemorySaver` checkpointer with `thread_id`. Each session has one thread. To reset conversation, change `thread_id`.

**Streamlit Integration (app.py):**

- Cache `llm` and `checkpointer` in `st.session_state` (avoid re-initialization)
- Cache `chat_session` for stateful conversations
- Multi-select sidebar updates `levels` dynamically

## Code Architecture Patterns

### Yardımcı Fonksiyonlar (chat.py)

**Asla manuel mesaj iterasyonu yapma** - yardımcı fonksiyonları kullan:

```python
get_last_user_message(messages)  # Son HumanMessage'ı çıkar
format_retrieved_context(docs)    # Dokümanları LLM için formatla
detect_level_mentions(llm, query) # Yapılandırılmış kademe tespiti
```

### Kademe Tespiti

Kullanıcı sorgularından **otomatik kademe tespiti** - yapılandırılmış LLM çıktısı kullanarak:

```python
class LevelDetection(BaseModel):
    detected_levels: list[str]
    should_add_to_context: bool
```

Örnek: "Lise programı nasıl?" → Otomatik "lise" kademesini bağlama ekler

**Regex parsing yok** - Tip güvenliği için Pydantic `with_structured_output()` kullanır

## Prompt Mühendisliği: "Siz" ile Türkçe Resmi Üslup

**KRITIK KURAL: TÜM LLM promptları %100 TÜRKÇE olmalı - İngilizce ifade yasak!**

**Sistem Promptu (chat.py:llm_node):**

- Sadece BAĞLAM'daki bilgileri kullan (uydurma yapma)
- Resmi "siz" ile hitap et (Türkçe nezaket)
- Özet ile başla, sonra detaylı açıklama ver (selamlaşma hariç)
- Takip sorularında sohbet geçmişini kullan (tüm mesaj listesi geçirilir)
- İlgili bilgi yoksa: "Üzgünüm, bu konuda size yardımcı olamıyorum."
- **Asla fiyat konuşma** - okul iletişimine yönlendir

**Temperature:** 0.4 (tutarlılık ve doğal dil dengesi)

## Development Workflow

### Running Locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Create .env with GOOGLE_API_KEY=AIzaSy...
streamlit run app.py
```

### Testing Changes

1. **FAISS Index:** Delete `faiss_index/` to force recreation if chunks change
2. **LangGraph Flow:** Check `langgraph_diagram.mmd` for graph structure
3. **Terminal:** Last command was `streamlit run app.py` (use for quick tests)

### Common Commands

```bash
# Force FAISS rebuild
rm -rf faiss_index && streamlit run app.py

# CLI testing (deprecated, prefer Streamlit)
python chat.py

# Query FAISS directly
python retriever.py "Anaokulu programı nedir?" --levels anaokulu
```

## Code Conventions

### İsimlendirme

- Türkçe docstring/yorumlar domain-spesifik mantık için (prompt mühendisliği)
- İngilizce teknik fonksiyonlar için (retriever, graph nodes)
- **Kademe isimleri:** Her zaman küçük harf (`anaokulu`, `Anaokulu` değil)
- **PROMPT İÇERİĞİ:** %100 Türkçe - İngilizce kelime/cümle yasak!

### Error Handling

- `silent=True` parameter in retriever functions (suppress output in production)
- Catch exceptions in `ChatSession.chat()` - return user-friendly Turkish messages
- `traceback.print_exc()` in development, but sanitize errors for users

### macOS Specific

```python
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # Fix OpenMP/FAISS conflict
```

**Must be set BEFORE importing FAISS** (top of retriever.py).

## Dependencies

**Core Stack:**

- `langchain` + `langchain-google-genai` + `langchain-community`
- `langgraph` - Graph-based orchestration with conditional edges
- `faiss-cpu` - Vector similarity search
- `streamlit` - Web UI
- `python-dotenv` - Environment variables

**API Keys:** Only `GOOGLE_API_KEY` needed (Gemini for both LLM + embeddings)

## Değişiklik Yapma Kuralları

**Prompt Değiştirme:**

- `chat.py:llm_node()` içindeki `system_prompt`'u düzenle
- **MUTLAKA %100 TÜRKÇE yaz** - İngilizce kelime yasak
- Fiyat soruları, takip soruları gibi uç durumlarla test et

**Yeni Kademe Ekleme:**

1. `chunks/{yeni_kademe}.json` dosyasına JSON ekle
2. `retriever.py` içinde `SUPPORTED_LEVELS` güncelle
3. `chat.py` içinde `get_level_display_name()` güncelle

**Router Mantığını İyileştirme:**

- `classify_query_with_llm()` fonksiyonunu değiştir
- **Promptu TÜRKÇE yaz**
- Sorular casual olarak sınıflanmasın diye dikkat et

**Streamlit UI:**

- Tüm değişiklikler `app.py` içinde
- Session state kırılgandır, iyice test et

## Recent Refactorings (November 2025)

### ✅ **Completed Improvements:**

1. **Conditional edge pattern** - `Command` yerine profesyonel `add_conditional_edges()` kullanımı
2. **Removed magic strings** - `"NEEDS_RETRIEVAL"` → `RetrievalStatus` enum
3. **Eliminated regex parsing** - Tag sistemi → Yapılandırılmış LLM çıktısı
4. **Added helper functions** - Manuel mesaj iterasyonu yok (DRY principle)
5. **Cleaner state management** - Enum-based retrieval status
6. **Type safety** - Pydantic modelleri tüm LLM yapılandırılmış çıktılar için
7. **%100 Türkçe promptlar** - LLM'e gönderilen tüm promptlar Türkçe

### ⚠️ **Current Limitations:**

1. **No streaming responses** - Entire response waits for completion
2. **Router sometimes over-retrieves** - Classification can be improved
3. **No caching** - Frequent questions hit LLM every time
4. **No conversation persistence** - Session lost on refresh (in-memory only)

## Deployment

**Streamlit Cloud:** Main deployment target (see DEPLOYMENT.md)

- Set `GOOGLE_API_KEY` in Streamlit secrets
- Auto-deploys from main branch
- Demo URL: https://cozum-veli-asistani.streamlit.app (pending)

**Local:** `streamlit run app.py` on port 8501
