# 🎓 Çözüm Eğitim Kurumları - AI Veli Asistanı

Çözüm Eğitim Kurumları'nın tüm okul seviyeleri (anaokulu, ilkokul, ortaokul, lise) için RAG (Retrieval-Augmented Generation) tabanlı soru-cevap sistemi.

## ✨ Özellikler

- **Çoklu Seviye Desteği**: Anaokulu'ndan lise'ye tüm okul seviyeleri için bilgi erişimi
- **Semantic Search**: Google Gemini embeddings ile gelişmiş anlam tabanlı arama
- **FAISS Vector Store**: Hızlı ve etkili benzerlik araması
- **Zenginleştirilmiş Embedding**: Başlık, soru, anahtar kelimeler ve içerik birleşimi
- **Seviye Filtreleme**: Belirli okul seviyelerinde arama yapabilme
- **Cross-Platform**: Windows, macOS ve Linux desteği

## 📁 Proje Yapısı

```
├── chunks/                  # Okul seviyelerine göre chunk dosyaları
│   ├── anaokulu.json       # Anaokulu bilgi parçaları (15 chunk)
│   ├── ilkokul.json        # İlkokul bilgi parçaları
│   ├── ortaokul.json       # Ortaokul bilgi parçaları
│   └── lise.json           # Lise bilgi parçaları
├── chat.py                 # 🤖 İnteraktif chatbot (ANA KULLANIM)
├── retriever.py            # 🔍 RAG retriever (test/debug)
├── docx-converter.py       # 📄 DOCX → Markdown dönüştürücü
├── requirements.txt        # Python bağımlılıkları
├── .env.example           # Örnek environment dosyası
└── README.md              # Bu dosya
```

## 🚀 Kurulum

### 1. Repository'yi Klonlayın

```bash
git clone <repo-url>
cd cozum-ai-asistant
```

### 2. Virtual Environment Oluşturun

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 4. API Anahtarı Ayarlayın

1. `.env.example` dosyasını `.env` olarak kopyalayın:

   ```bash
   cp .env.example .env
   ```

2. [Google AI Studio](https://aistudio.google.com/apikey)'dan ücretsiz API anahtarı alın

3. `.env` dosyasını düzenleyip API anahtarınızı ekleyin:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

## 💡 Kullanım

### 🤖 İnteraktif Chatbot (Önerilen)

En doğal deneyim için interaktif chatbot kullanın:

```bash
python chat.py
```

**Özellikler:**

- 🎯 Başlangıçta eğitim kademesi seçimi
- 💬 Doğal dil ile soru-cevap
- 🧠 Sohbet geçmişi (son 5 mesaj)
- 🔄 Kademe değiştirme (`/seviye`)
- 🗑️ Geçmişi temizleme (`/temizle`)

**Komutlar:**

- `/help` - Yardım mesajı
- `/seviye` - Kademe değiştir
- `/temizle` - Sohbet geçmişini sil
- `/cikis` - Çıkış

**Örnek Kullanım:**

```
Seçiminiz: 1,2              # Anaokulu ve ilkokul seçildi
Siz: İngilizce dersleri nasıl?
Asistan: Anaokulunda İngilizce eğitimi...
Siz: Peki ödevler nasıl veriliyor?
Asistan: [Geçmiş bağlamında yanıt]
```

### 🔍 Doğrudan Retriever (Test/Debug)

Terminal'den hızlı arama için:

```bash
# Temel sorgu
python retriever.py "Anaokulunda İngilizce eğitimi nasıl veriliyor?"

# Daha fazla sonuç
python retriever.py "Matematik dersleri" -k 5

# Belirli kademelerde ara
python retriever.py "Ödev politikası" --levels anaokulu ilkokul

# İndeksi yeniden oluştur
python retriever.py "test" --recreate

# Yardım
python retriever.py --help
```

## 📊 Chunk Yapısı

Her chunk şu alanları içerir:

```json
{
  "id": "anaokulu-01",
  "level": "anaokulu",
  "title": "Vizyon",
  "question": "Çözüm Eğitim Kurumları'nın vizyonu nedir?",
  "answer_type": "informational",
  "embedding_hint": "vizyon, hedef, geleceğe bakış",
  "content": "Detaylı içerik...",
  "source": "Anaokulu.VeliBilgilendirmeMetni.docx",
  "tags": ["vizyon", "kurumsal"],
  "version": "2025-10",
  "chunk_index": 0
}
```

### Embedding Stratejisi

Retriever, daha iyi semantik arama için şu formatta embedding oluşturur:

```
title + question + embedding_hint + content
```

Bu sayede:

- 📖 **Title**: Konuyu tanımlar
- ❓ **Question**: Doğal dil sorularını yakalar
- 🔑 **Embedding Hint**: Anahtar kelimeleri vurgular
- 📄 **Content**: Tam içeriği sağlar

## 🛠️ DOCX Dönüştürücü

DOCX dosyalarını Markdown formatına dönüştürmek için:

```bash
# Tek dosya
python docx-converter.py -i "Anaokulu.VeliBilgilendirmeMetni.docx" -o "output.md"

# Klasör
python docx-converter.py -i "docx_files/" -o "markdown_files/"
```

## 🔧 Geliştirme

### Yeni Chunk Ekleme

1. İlgili `chunks/<level>.json` dosyasını düzenleyin
2. Chunk şemasına uygun yeni entry ekleyin
3. İndeksi yeniden oluşturun:
   ```bash
   python retriever.py "test" --recreate
   ```

### Desteklenen Okul Seviyeleri

- `anaokulu` - Anaokulu
- `ilkokul` - İlkokul (1-4. sınıf)
- `ortaokul` - Ortaokul (5-8. sınıf)
- `lise` - Lise (9-12. sınıf)

## 📝 Notlar

- İlk çalıştırmada FAISS indeksi otomatik oluşturulur (~30-60 saniye)
- İndeks `faiss_index/` klasöründe saklanır
- Chunk dosyalarını güncelledikten sonra `--recreate` kullanın
- API limitleri için [Google AI Studio](https://ai.google.dev/pricing) sayfasına bakın

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje Çözüm Eğitim Kurumları için geliştirilmiştir.
