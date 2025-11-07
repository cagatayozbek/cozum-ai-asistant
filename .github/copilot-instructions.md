# Çözüm Koleji Veli Asistanı - AI Coding Agent Instructions

## Project Overview

A RAG-powered parent assistant chatbot for Çözüm Koleji (Turkish school system) built with **Streamlit + LangChain Agents + FAISS + Google Gemini 2.5 Flash**. The system provides accurate, document-grounded answers about school programs across 4 education levels (anaokulu, ilkokul, ortaokul, lise) while avoiding hallucinations.

**Production Entry:** `streamlit run app.py` (NOT chat.py - that's CLI testing)

## Mimari: LangChain v1 Multi-Tool Agent Pattern

```
User Query (Streamlit)
  → LangChain Agent (create_agent)
    |
    ├─ LLM natively decides tool usage
    |    |
    |    ├─ retrieve_education_info → FAISS search
    |    ├─ search_school_news → Web scraper (placeholder)
    |    └─ No tool → Direct response
    |
    → LLM Response
```

**Kritik Dosyalar:**

- `app.py` - Streamlit UI ve session yönetimi (PRODUCTION)
- `chat.py` - LangChain Agent: `ChatSession` sınıfı, `create_agent()` ve tool definitions
- `retriever.py` - FAISS vector store, chunk yükleme, embedding oluşturma
- `tools.py` - DEPRECATED: Tools moved to chat.py (closure pattern for level filtering)

### Ana Tasarım Kararı: Multi-Tool Agent Pattern with Closure

**Neden Multi-Tool Agent?**

- ✅ LangChain v1 standardı (`create_agent` API)
- ✅ LLM native tool calling (manuel router yok)
- ✅ Kolay genişletilebilir (@tool decorator)
- ✅ 61% daha az kod (474 → 186 satır)
- ✅ 50% daha hızlı (2 LLM call → 1 LLM call)
- ✅ **Closure pattern** - Tools access self.levels for automatic filtering

**Nasıl Çalışır:**

1. `_create_tools()` - ChatSession içinde tools oluştur (closure ile self.levels erişimi)
2. `create_agent()` - LangChain v1 ile agent oluştur
3. LLM tools'u görebilir ve nerede kullanacağına karar verir
4. Tool otomatik olarak kullanıcının seçtiği kademelerde arama yapar
5. Soru → `retrieve_education_info` tool'unu çağır → FAISS'ten bilgi al
6. Etkinlik sorusu → `search_school_news` tool'unu çağır (henüz placeholder)

**Eski Pattern (Deprecated - Router Pattern):**

Eski kod `chat_backup_router_pattern.py`'de saklanıyor. Eski mimari:

- Router node → LLM classification → Conditional edge → Retrieve node → LLM node
- Sorun: Duplicate retrieval, ekstra LLM call, karmaşık state management

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

**State Schema (Simplified in LangChain v1):**

LangChain v1 agent handles state internally. `ChatSession` only manages:

- `levels`: list[str] | None - Seçili eğitim kademeleri
- `conversation_history`: list[dict] - Sohbet geçmişi (role + content)
- `thread_id`: str - Session identifier for checkpointer

**Agent State Pattern:**

Agent uses internal LangGraph state with standard message format:

```python
{
    "messages": list[BaseMessage]  # HumanMessage, AIMessage, ToolMessage
}
```

**Conversation History:**

- Stored as simple dict: `{"role": "user"|"assistant", "content": str}`
- Converted to LangChain messages (HumanMessage/AIMessage) before agent invoke
- Agent automatically handles tool calls and responses internally

**Session Persistence:** Uses `MemorySaver` checkpointer with `thread_id`. Each session has one thread. To reset conversation, change `thread_id`.

**Streamlit Integration (app.py):**

- Cache `llm` and `checkpointer` in `st.session_state` (avoid re-initialization)
- Cache `chat_session` for stateful conversations
- Multi-select sidebar updates `levels` dynamically

## Code Architecture Patterns

### Yardımcı Fonksiyonlar (chat.py)

**Asla manuel mesaj iterasyonu yapma** - yardımcı fonksiyonları kullan:

````python
## Code Architecture Patterns

### Yardımcı Fonksiyonlar (chat.py)

**Asla manuel mesaj iterasyonu yapma** - yardımcı fonksiyonları kullan:

```python
get_last_user_message(messages)  # Son HumanMessage'ı çıkar
format_retrieved_context(docs)    # Dokümanları LLM için formatla
detect_level_mentions(llm, query) # Yapılandırılmış kademe tespiti
````

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

## Değişiklik Yapma Kuralları

**Prompt Değiştirme:**

- `chat.py:_create_agent()` içindeki `system_prompt`'u düzenle
- **MUTLAKA %100 TÜRKÇE yaz** - İngilizce kelime yasak
- Fiyat soruları, takip soruları gibi uç durumlarla test et

**Yeni Kademe Ekleme:**

1. `chunks/{yeni_kademe}.json` dosyasına JSON ekle
2. `retriever.py` içinde `SUPPORTED_LEVELS` güncelle
3. `chat.py` içinde `get_level_display_name()` güncelle

**Yeni Tool Ekleme:**

- `chat.py:_create_tools()` içinde yeni `@tool` decorator ile fonksiyon ekle
- **Docstring TÜRKÇE olmalı** - Agent bu açıklamayı okur
- **Closure avantajı** - self.levels, self.llm gibi ChatSession property'lerine erişebilirsin
- Return listesine ekle
- Test et

**Streamlit UI:**

- Tüm değişiklikler `app.py` içinde
- Session state kırılgandır, iyice test et

## Recent Refactorings (November 2025)

### ✅ **Completed Improvements:**

1. **Multi-tool agent migration** - Router pattern → LangChain v1 `create_agent`
2. **61% code reduction** - 474 lines → 186 lines (chat.py)
3. **50% performance boost** - 2 LLM calls → 1 LLM call (no classification overhead)
4. **Tool-based architecture** - Easy to add new capabilities (@tool decorator)
5. **Native tool calling** - LLM decides tool usage (no manual routing)
6. **Type safety** - Pydantic modelleri tüm LLM yapılandırılmış çıktılar için
7. **%100 Türkçe promptlar** - LLM'e gönderilen tüm promptlar Türkçe
8. **Content blocks handling** - LangChain v1 response format support

**Migration Details:** See `MIGRATION_LOG.md` for full documentation

**Backup:** Old router pattern code in `chat_backup_router_pattern.py`

### ⚠️ **Current Limitations:**

1. **No streaming responses** - Entire response waits for completion
2. **No caching** - Frequent questions hit LLM every time
3. **No conversation persistence** - Session lost on refresh (in-memory only)
4. **Web scraper placeholder** - `search_school_news` not yet implemented

## Deployment

**Streamlit Cloud:** Main deployment target (see DEPLOYMENT.md)

- Set `GOOGLE_API_KEY` in Streamlit secrets
- Auto-deploys from main branch
- Demo URL: https://cozum-veli-asistani.streamlit.app (pending)

**Local:** `streamlit run app.py` on port 8501
