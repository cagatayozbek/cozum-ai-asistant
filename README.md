# 🎓 Çözüm Koleji Veli Asistanı

AI destekli veli asistanı - Okul programları, etkinlikler ve eğitim hakkında anında yanıt.

**🌐 [Demo'yu Deneyin →](https://cozum-veli-asistani.streamlit.app)** *(Deployment sonrası güncellenecek)*

## ✨ Özellikler

- 💬 **Doğal Dil Sohbet**: İnsan gibi konuşan AI asistanı
- 📚 **RAG Sistemi**: Sadece okul dokümanlarından bilgi verir, uydurma yapmaz
- 🎯 **Kademe Bazlı**: Anaokulu, İlkokul, Ortaokul, Lise - tümü için destek
- 🔄 **Sohbet Geçmişi**: Takip sorularını anlayan akıllı asistan
- ⚡ **Hızlı Yanıt**: Gereksiz aramalarda FAISS'i atlar, performanslı çalışır
- 📱 **Web UI**: Streamlit ile modern, responsive arayüz

## �️ Teknolojiler

- **Frontend:** Streamlit
- **LLM:** Google Gemini 2.5 Flash (temperature=0.4)
- **RAG:** LangChain + FAISS vector store
- **Graph:** LangGraph with router node for conditional retrieval
- **Embeddings:** Google Generative AI Embeddings

## 📁 Proje Yapısı

```
├── app.py                    # 🌐 Streamlit web UI (PRODUCTION)
├── chat.py                   # 🤖 LangGraph chat logic
├── retriever.py              # 🔍 FAISS RAG sistemi
├── documents/                # 📄 Okul dokümanları (DOCX)
├── faiss_index/              # � Vektör veritabanı (otomatik oluşturulur)
├── .streamlit/
│   └── config.toml          # 🎨 UI tema ayarları
├── requirements.txt          # 📦 Python bağımlılıkları
├── DEPLOYMENT.md            # 🚀 Deployment rehberi
├── DEMO_BİLGİLENDİRME.md   # 📋 Kurum için demo dokümanı
└── README.md                # 📖 Bu dosya
```

## 🚀 Hızlı Başlangıç

### Lokal Geliştirme

```bash
# 1. Repository'yi klonla
git clone https://github.com/cagatayozbek/cozum-ai-asistant.git
cd cozum-ai-asistant

# 2. Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # macOS/Linux
# veya
venv\Scripts\activate  # Windows

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. .env dosyası oluştur
cp .env.example .env
# GOOGLE_API_KEY'i .env dosyasına ekle

# 5. Streamlit uygulamasını başlat
streamlit run app.py
```

### 🔑 Google API Key Alma

1. [Google AI Studio](https://aistudio.google.com/apikey) adresine git
2. "Create API Key" butonuna tıkla
3. Key'i kopyala ve `.env` dosyasına ekle:
   ```
   GOOGLE_API_KEY=AIzaSy...
   ```

## 💡 Kullanım

### 🌐 Web Uygulaması (Ana Kullanım)

Streamlit UI ile kullanıcı dostu arayüz:

```bash
streamlit run app.py
```

**Özellikler:**
- 📱 Responsive tasarım (mobil uyumlu)
- 🎯 Sidebar'dan kademe seçimi
- 💬 Chat interface ile doğal sohbet
- 🔄 "Yeni Sohbet" butonu ile reset
- ⚡ Gerçek zamanlı yanıtlar

### �️ CLI Uygulaması (Test İçin)

Terminal'den hızlı test:

```bash
python chat.py
```

**Komutlar:**
- `/help` - Yardım
- `/seviye` - Kademe değiştir
- `/temizle` - Geçmişi sil
- `/cikis` - Çıkış

## 🧪 Örnek Sorular

```
👤 "Merhaba"
🤖 "Merhaba! Ben Çözüm Eğitim Kurumları'nın veli asistanıyım..."

� "Anaokulu programı nedir?"
🤖 "Anaokulumuzda Cambridge programı ile..."

👤 "Biyoloji kaç saat?" (takip sorusu)
🤖 [Önceki yanıttan devam eder]

👤 "Lise ve ortaokul matematik saatlerini karşılaştır"
🤖 [İki kademe için bilgi verir]
```

## 🌐 Production Deployment

### Streamlit Cloud (Ücretsiz)

1. GitHub'a push et
2. [share.streamlit.io](https://share.streamlit.io)'ya git
3. "New app" → Repository seç → `app.py` belirt
4. Secrets'a `GOOGLE_API_KEY` ekle
5. Deploy!

**Detaylı adımlar:** [DEPLOYMENT.md](DEPLOYMENT.md) dosyasına bakın.

### Diğer Platformlar

- **Docker:** Dockerfile hazır değil (eklenebilir)
- **Railway/Render:** Streamlit destekler
- **AWS/GCP:** Cloud Run veya EC2/Compute Engine

## 🏗️ Mimari

```
┌─────────────┐
│   User      │
│  (Streamlit)│
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   LangGraph     │
│   Router Node   │  ← Query classification
└────┬────────────┘
     │
     ├─→ Greeting? → Direct LLM
     │
     └─→ Question? → FAISS Retrieval → LLM
                          ▲
                          │
                   ┌──────┴──────┐
                   │  Documents  │
                   │   (DOCX)    │
                   └─────────────┘
```

**Akıllı Özellikler:**
- ✅ Selamlaşma/teşekkür → FAISS atla (hız++)
- ✅ Kısa takip soruları → Önceki context kullan
- ✅ Full conversation history → LLM'e geçir

## � Yapılacaklar

- [ ] Streaming responses
- [ ] Örnek soru önerileri
- [ ] Session persistence (disk)
- [ ] Web scraping (Instagram, website)
- [ ] Hybrid search (keyword + semantic)
- [ ] Analytics dashboard

**Detaylı roadmap:** [yapılacaklar.md](yapılacaklar.md)

## 📄 Lisans

Bu proje Çözüm Eğitim Kurumları için geliştirilmiştir.

## 📞 İletişim

- **GitHub:** [@cagatayozbek](https://github.com/cagatayozbek)
- **Repository:** [cozum-ai-asistant](https://github.com/cagatayozbek/cozum-ai-asistant)

---

**Demo için:** [DEMO_BİLGİLENDİRME.md](DEMO_BİLGİLENDİRME.md) dosyasına bakın.

## 📄 Lisans

Bu proje Çözüm Eğitim Kurumları için geliştirilmiştir.
