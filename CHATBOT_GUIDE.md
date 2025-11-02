# 🎓 Çözüm Eğitim Kurumları - AI Veli Asistanı: Kullanım Kılavuzu

> **Teknoloji:** LangGraph + Google Gemini 2.0 Flash + FAISS Vector Store  
> **Mimari:** Retrieval-Augmented Generation (RAG) + Stateful Conversation

## 🆕 Son Güncellemeler (v2.0)

### LangGraph Mimarisi

- ✅ **Session-based'den Graph-based'e geçiş:** Daha esnek ve ölçeklenebilir
- ✅ **TypedDict State Schema:** Pydantic v2 uyumlu, type-safe
- ✅ **Otomatik Message Persistence:** `Annotated[list, add]` operator ile
- ✅ **MemorySaver Checkpointer:** Thread-based conversation history

### Performans İyileştirmeleri

- ⚡ **FAISS Indeks Caching:** Disk'e kaydedilir, tekrar yüklenmez
- ⚡ **Gemini 2.0 Flash:** Daha hızlı ve akıllı yanıtlar
- ⚡ **Normalized Vector Search:** IndexFlatIP + L2 normalization

### Bug Fixes

- 🐛 macOS OpenMP çoklu yükleme hatası düzeltildi (`KMP_DUPLICATE_LIB_OK=TRUE`)
- 🐛 Pydantic v2 deprecation warnings giderildi
- 🐛 State management sorunları çözüldü (manual state reconstruction kaldırıldı)

---

## 🚀 Hızlı Başlangıç

### 1. Chatbot'u Başlatın

```bash
python chat.py
```

### 2. Eğitim Kademesi Seçin

Program başladığında size çocuğunuzun eğitim kademesini soracak:

```
🎓 Çözüm Eğitim Kurumları - AI Veli Asistanı
======================================================================
Merhaba! Ben Çözüm Koleji AI asistanıyım.
Size okulumuz hakkında bilgi vermek için buradayım. 😊

Lütfen çocuğunuzun/çocuklarınızın eğitim kademesini seçin:
(Birden fazla çocuğunuz varsa, virgülle ayırarak girebilirsiniz)

1. Anaokulu
2. İlkokul (1-4. Sınıf)
3. Ortaokul (5-8. Sınıf)
4. Lise (9-12. Sınıf)
5. Tüm kademeler

Seçiminiz (örn: 1,2 veya 1):
```

**Örnekler:**

- `1` → Sadece anaokulu
- `1,2` → Anaokulu ve ilkokul (çocuklarınız farklı kademelerdeyse)
- `5` → Tüm kademeler (tüm bilgilere erişim)

### 3. Soru Sorun!

Kademe seçtikten sonra doğal dille sorularınızı sorun:

```
👤 Siz: İngilizce dersleri nasıl veriliyor?

🤖 Asistan: Anaokulunda İngilizce eğitimi, Cambridge Yayınları
ve Think&Talk programlarıyla verilmektedir. Main Course dersleri
haftada 12 saat, Think&Talk dersleri ise 2 saattir. Ayrıca
"Dil Duşu" yöntemi kullanılarak çocukların erken yaşta yabancı
dile aşinalık kazanması sağlanmaktadır.
```

## 🎯 Özellikler

### ✅ Çoklu Kademe Desteği

Birden fazla çocuğunuz varsa, hepsinin kademesini seçebilirsiniz:

```
Seçiminiz: 1,3        # Anaokulu + Ortaokul
```

Asistan her iki kademeye uygun yanıtlar verecektir.

### 🔍 RAG (Retrieval-Augmented Generation)

Her sorgunuzda:

1. **FAISS Vector Search** ile en alakalı 4 döküman bulunur (cosine similarity)
2. Dokümanlar LLM'e **context** olarak verilir
3. Gemini 2.0 Flash sadece bu context'e dayanarak yanıt üretir
4. **Halüsinasyon yok** - Sadece gerçek okul belgelerinden bilgi

**Avantajlar:**

- ✅ Güncel bilgi (embedding'ler yeniden oluşturulabilir)
- ✅ Doğru yanıtlar (kaynak belgelere dayalı)
- ✅ Hızlı arama (FAISS IndexFlatIP + L2 normalization)

### 🧠 Sohbet Geçmişi (LangGraph State Management)

Chatbot **tüm konuşma geçmişinizi** otomatik olarak saklar ve bağlamsal yanıtlar verir:

```
Siz: Matematik dersleri var mı?
Asistan: Evet, matematik dersleri...

Siz: Kaç saat?                    # "Matematik dersleri" bağlamında
Asistan: Haftada X saat...        # Önceki soruyu hatırlıyor

Siz: Peki İngilizce?              # Hala "ders saatleri" bağlamında
Asistan: İngilizce dersleri...    # Konuşma akışını takip ediyor
```

**Teknik Detay:** LangGraph'ın `MemorySaver` checkpointer'ı ile thread-based persistence kullanılıyor.

### 🔄 Dinamik Kademe Değiştirme

Sohbet sırasında kademe değiştirebilirsiniz:

```
Siz: /seviye
🔄 Yeni kademe seçimi yapılıyor...
[Kademe seçim ekranı yeniden açılır]
```

## 📝 Komutlar

| Komut      | Alternatif      | Açıklama                     |
| ---------- | --------------- | ---------------------------- |
| `/help`    | `/yardim`       | Yardım mesajını gösterir     |
| `/seviye`  | `/kademe`       | Eğitim kademesini değiştirir |
| `/temizle` | `/clear`        | Sohbet geçmişini siler       |
| `/cikis`   | `/exit`, `quit` | Programdan çıkar             |

## 💡 Kullanım İpuçları

### ✨ Doğal Dil Kullanın

Sorularınızı günlük konuşma dilinizle sorun:

✅ **İyi örnekler:**

- "İngilizce dersleri nasıl?"
- "Çocuğum için hangi etkinlikler var?"
- "Ödevler ne kadar veriliyor?"
- "Üniversite hazırlık programınız var mı?"

❌ **Gereğinden fazla detaylı:**

- "Sayın yetkili, çocuğumun İngilizce eğitimi hakkında detaylı bilgi almak istiyorum"

### 🎯 Bağlamı Kullanın

Önceki sorularınızla ilişkili takip soruları sorun:

```
Siz: GEMS programı nedir?
Asistan: GEMS, öğrencilerin fen ve matematik becerilerini...

Siz: Bu program hangi yaşlarda uygulanıyor?  # "GEMS" bağlamında
Asistan: GEMS programı anaokulu seviyesinde...
```

### 🔄 Kademe Filtreleme

Sadece belirli bir kademe için soru sormak isterseniz `/seviye` komutuyla değiştirin:

```
# Başlangıçta: Anaokulu + İlkokul seçildi
Siz: Lise programları hakkında bilgi istiyorum
Asistan: [Anaokulu ve ilkokul bazlı yanıt verir]

Siz: /seviye
# Sadece "Lise" seçin
Siz: Lise programları hakkında bilgi istiyorum
Asistan: [Liseye özel detaylı yanıt]
```

### 🗑️ Yeni Konu Başlatma

Yeni bir konuya geçerken geçmişi temizleyin:

```
Siz: /temizle
✅ Sohbet geçmişi temizlendi.

Siz: [Yeni konu hakkında soru]
```

**Teknik:** Yeni bir `thread_id` oluşturulur, önceki conversation state'i korunur ama yeni thread başlar.

## 🔧 Sorun Giderme

### ❌ "GOOGLE_API_KEY bulunamadı"

**Çözüm:**

1. `.env.example` dosyasını `.env` olarak kopyalayın
2. [Google AI Studio](https://aistudio.google.com/apikey)'dan API key alın
3. `.env` dosyasına key'i ekleyin: `GOOGLE_API_KEY=your_key_here`

### ❌ "Hiç bilgi bulamadım"

**Nedenleri:**

- FAISS indeksi oluşturulmamış olabilir
- İlk kullanımda indeks otomatik oluşturulur (~30-60 saniye)

**Çözüm:**

```bash
# Manuel indeks oluşturma (--recreate bayrağı ile)
python retriever.py "test sorgu" --recreate
```

### ❌ "OMP: Error #15" (macOS)

**Neden:** OpenMP kütüphanesi çoklu yükleme hatası (FAISS)

**Çözüm:** Zaten `retriever.py`'da `KMP_DUPLICATE_LIB_OK=TRUE` ayarı var, sorun oluşmamalı.

### ⚠️ Yanıtlar yavaş

**İlk sorgu:** FAISS indeksini yükler (5-10 saniye) - **NORMAL**  
**Sonraki sorgular:** Hızlı (1-2 saniye)

**Optimizasyon:** Indeks disk'e kaydedilir (`faiss_index/`), bir kez yüklenir.

### 🐛 Program donuyor

**Ctrl+C** ile güvenli çıkış yapabilirsiniz:

```
^C
👋 Program sonlandırıldı. İyi günler!
```

## 📊 Örnek Sohbet Senaryoları

### Senaryo 1: Anaokulu Velisi (Bağlamsal Takip)

```
Seçiminiz: 1

Siz: Çocuğum ilk kez okula başlayacak, uyum programınız var mı?
Asistan: Evet, okulumuzda oryantasyon ve uyum programı...

Siz: İngilizce dersleri kaç yaşında başlıyor?
Asistan: İngilizce eğitimi anaokulundan itibaren başlamaktadır...

Siz: Kaç saat?                            # "İngilizce dersleri" context'inde
Asistan: Main Course dersleri haftada 12 saat, Think&Talk dersleri ise 2 saattir...

Siz: Teşekkürler!
Asistan: Rica ederim! Başka sorunuz olursa çekinmeden sorabilirsiniz.
```

### Senaryo 2: İlkokul + Ortaokul Velisi

```
Seçiminiz: 2,3

Siz: İki çocuğum var, birisi ilkokul birisi ortaokul. Her ikisi için ödev politikanız nedir?
Asistan: İlkokul ve ortaokulda ödev politikamız...

Siz: /seviye
# Sadece ilkokul seç
Siz: İlkokul için detaylı ödev bilgisi
Asistan: [İlkokula özel detaylı bilgi]
```

### Senaryo 3: Lise Velisi (Üniversite Hazırlık)

```
Seçiminiz: 4

Siz: Üniversite hazırlık programınız var mı?
Asistan: Evet, lisemizde üniversite hazırlık...

Siz: Hangi üniversitelere öğrenci gönderiyorsunuz?
Asistan: [Mezunlarımızın yerleştikleri üniversiteler]

Siz: Rehberlik servisi var mı?
Asistan: Evet, rehberlik servisimiz...
```

## 🎓 Sonuç

Bu chatbot, Çözüm Eğitim Kurumları hakkında 7/24 bilgi almanızı sağlar:

✅ **Hızlı yanıtlar** → Anında bilgi (1-2 saniye)  
✅ **Çoklu kademe** → Tüm çocuklarınız için  
✅ **Bağlamsal** → Doğal sohbet, tam conversation history  
✅ **Güvenilir** → Sadece resmi belgelerden bilgi (RAG)  
✅ **Modern** → LangGraph state management + Gemini 2.0 Flash

**Not:** Asistan sadece mevcut belgelerdeki bilgileri verir. Özel durumlarınız için okulumuzla doğrudan iletişime geçmenizi öneririz.

---

## 🛠️ Teknik Mimari

### Stack

- **LLM:** Google Gemini 2.0 Flash (`gemini-2.0-flash`)
- **Embeddings:** Google Gemini Embedding Model (`gemini-embedding-001`)
- **Vector Store:** FAISS with IndexFlatIP (cosine similarity via normalized L2)
- **Framework:** LangGraph (StateGraph + MemorySaver checkpointer)
- **State Management:** TypedDict with `Annotated[list[BaseMessage], add]` for message persistence

### Workflow (Graph Nodes)

1. **START** → User message eklenir state'e
2. **retrieve_node** → FAISS'den ilgili dökümanları çeker, `state.context`'e yazar
3. **llm_node** → Context + user message ile Gemini'yi çağırır, AIMessage döndürür
4. **END** → Yanıt kullanıcıya iletilir

### State Schema

```python
class ChatState(TypedDict):
    levels: list[str] | None          # Seçili eğitim kademeleri
    messages: Annotated[list[BaseMessage], add]  # Tüm conversation history
    context: str                       # FAISS'den alınan dökümanlar
```

### Key Features

- **Automatic State Persistence:** `add` operator ile messages otomatik birikiyor
- **Thread-based Conversations:** Her kullanıcı için ayrı `thread_id`
- **Context Caching:** FAISS indeks disk'e kaydedilir (`faiss_index/`)
- **Level Filtering:** Retrieval sırasında kademe bazlı filtreleme

---

## 🎯 Gelişmiş Kullanım İpuçları

### 1. Multi-Turn Conversation

LangGraph sayesinde, karmaşık çok turlu konuşmalar desteklenir:

```
Siz: GEMS programı nedir?
Bot: GEMS, öğrencilerin fen ve matematik becerilerini geliştiren...

Siz: Bu programda hangi konular var?
Bot: [GEMS context'inde yanıt]

Siz: Peki hangi yaş grubu için?
Bot: [Hala GEMS + yaş grubu context'inde]
```

### 2. Level Switching On-the-Fly

```
# Başlangıç: Anaokulu seçili
Siz: Lise programları için soru var
Bot: [Anaokulu bazlı yanıt - lise bilgisi yok]

Siz: /seviye
# Lise seç
Siz: Lise programları için soru var
Bot: [Liseye özel detaylı yanıt]
```

### 3. Debug Mode (Geliştiriciler için)

Kodu çalıştırırken `[DEBUG]` çıktılarını görmek için:

```python
# chat.py içinde debug satırlarını uncomment edin
print(f"[DEBUG] Retrieved docs: {len(retrieved_docs)}")
```

### 4. Custom FAISS Parameters

`retriever.py`'da `k` parametresini değiştirerek daha fazla/az döküman alın:

```python
# Daha fazla context için k=8 yapın
retrieved_docs = get_retrieved_documents(query, k=8, levels=levels)
```

---

## 📚 Kaynaklar

- **LangGraph Docs:** https://langchain-ai.github.io/langgraph/
- **Gemini API:** https://ai.google.dev/
- **FAISS:** https://github.com/facebookresearch/faiss
- **Proje Repo:** https://github.com/cagatayozbek/cozum-ai-asistant

---

**Destek:** Teknik sorunlar için `github.com/cagatayozbek/cozum-ai-asistant` adresinden issue açabilirsiniz.

**Geliştirici:** [@cagatayozbek](https://github.com/cagatayozbek)  
**Lisans:** MIT  
**Son Güncelleme:** Kasım 2025
