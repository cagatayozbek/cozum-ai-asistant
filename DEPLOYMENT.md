# 🚀 Deployment Rehberi - Streamlit Cloud

Bu rehber Çözüm Veli Asistanı'nı Streamlit Community Cloud'a deploy etmek için adım adım talimatlar içerir.

## 📋 Ön Hazırlık

### 1. GitHub'a Push Edin

```bash
# Değişiklikleri commit edin
git add .
git commit -m "Add Streamlit app for deployment"

# GitHub'a push edin
git push origin main
```

### 2. Gerekli Dosyaların Kontrolü

✅ Aşağıdaki dosyaların mevcut olduğundan emin olun:

- `app.py` - Streamlit uygulaması
- `chat.py` - Chat logic
- `retriever.py` - RAG sistemi
- `requirements.txt` - Bağımlılıklar (streamlit dahil)
- `.streamlit/config.toml` - Streamlit tema ayarları
- `documents/` klasörü - Okul dokümanları
- `.env.example` - Örnek environment dosyası

## 🌐 Streamlit Cloud'a Deploy

### Adım 1: Streamlit Cloud'a Giriş

1. [share.streamlit.io](https://share.streamlit.io) adresine gidin
2. GitHub hesabınızla giriş yapın
3. Repository'nize erişim izni verin

### Adım 2: Yeni App Oluşturun

1. **"New app"** butonuna tıklayın
2. Aşağıdaki bilgileri girin:
   - **Repository:** `cagatayozbek/cozum-ai-asistant`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** İstediğiniz isim (örn: `cozum-veli-asistani`)

### Adım 3: Secrets Ekleyin

🔑 **ÇOK ÖNEMLİ:** API key'i secrets olarak ekleyin!

1. App sayfasında **"Settings"** > **"Secrets"** kısmına gidin
2. Aşağıdaki formatı kullanın:

```toml
GOOGLE_API_KEY = "AIzaSy..."
```

3. **"Save"** butonuna tıklayın

### Adım 4: Deploy Edin

1. **"Deploy!"** butonuna tıklayın
2. İlk deploy 5-10 dakika sürebilir
3. FAISS index oluşturulacak (ilk çalıştırmada biraz uzun sürer)

## ✅ Deploy Sonrası Kontroller

### Test Senaryoları

Deploy tamamlandıktan sonra aşağıdakileri test edin:

1. **Uygulama açılıyor mu?**

   - ✅ Başlık ve sidebar görünüyor
   - ✅ Kademe seçimi çalışıyor

2. **Chat çalışıyor mu?**

   - ✅ Kademe seç → Soru sor → Yanıt geliyor
   - ✅ "Merhaba" → Hızlı yanıt veriyor

3. **FAISS index yüklendi mi?**

   - ✅ İlk soruda biraz gecikme normal (index yükleniyor)
   - ✅ Sonraki sorular hızlı

4. **Hatalar var mı?**
   - ❌ "GOOGLE_API_KEY not found" → Secrets'ı kontrol et
   - ❌ "Module not found" → requirements.txt'yi kontrol et
   - ❌ "FAISS index not found" → documents/ klasörü var mı?

## 🛠️ Troubleshooting

### Sorun 1: "API key not found"

**Çözüm:**

1. Settings > Secrets'a git
2. GOOGLE_API_KEY'i ekle
3. App'i yeniden başlat (Reboot)

### Sorun 2: "Module 'streamlit' not found"

**Çözüm:**

1. `requirements.txt` dosyasında `streamlit==1.39.0` var mı kontrol et
2. Yoksa ekle ve commit/push yap
3. Streamlit Cloud otomatik yeniden deploy eder

### Sorun 3: FAISS Index Hatası

**Çözüm:**

1. `documents/` klasörünün GitHub'da olduğundan emin ol
2. `.gitignore` dosyasında `documents/` yazmadığından emin ol
3. İlk çalıştırmada index otomatik oluşturulacak

### Sorun 4: Yavaş Yanıtlar

**Beklenen Davranış:**

- İlk soru: 5-10 saniye (FAISS index yükleniyor)
- Sonraki sorular: 2-3 saniye

**Eğer hep yavaşsa:**

- Gemini API rate limit'e takılıyor olabilir
- Logs'u kontrol edin (Settings > Logs)

## 📊 Monitoring & Logs

### Logs Görüntüleme

1. App sayfasında sağ üst **"Manage app"** > **"Logs"**
2. Hataları ve performans metriklerini izleyin

### Önemli Log Mesajları

```
✅ "Loading FAISS index..." - Index yükleniyor
✅ "Chat session initialized" - Session başladı
❌ "APIError" - Gemini API sorunu
❌ "FileNotFoundError" - Dosya eksik
```

## 🔄 Güncelleme

Deploy edildikten sonra güncelleme yapmak için:

```bash
# Değişiklikleri yap
git add .
git commit -m "Update app"
git push origin main

# Streamlit Cloud otomatik yeniden deploy eder (1-2 dakika)
```

## 🎯 Production Checklist

Deploy etmeden önce kontrol edin:

- [ ] GitHub repository public veya Streamlit'e erişim verildi mi?
- [ ] `requirements.txt` tüm bağımlılıkları içeriyor mu?
- [ ] `GOOGLE_API_KEY` Secrets'a eklendi mi?
- [ ] `documents/` klasörü commit edildi mi?
- [ ] `.env` dosyası `.gitignore`'da mı? (API key GitHub'a gitmemeli!)
- [ ] Test senaryoları çalışıyor mu?

## 🌍 Özel Domain (Opsiyonel)

Streamlit Cloud ücretsiz plan `your-app.streamlit.app` URL'i verir.

Özel domain için:

1. Streamlit Cloud'da domain ayarlarını aç
2. DNS CNAME kaydı ekle
3. SSL sertifikası otomatik

## 📱 Mobil Uyumluluk

Streamlit otomatik responsive tasarım sağlar:

- ✅ Telefon
- ✅ Tablet
- ✅ Desktop

Ekstra işlem gerekmez!

## 💰 Maliyet

**Streamlit Community Cloud:**

- ✅ Ücretsiz
- ✅ 1 GB RAM
- ✅ Sınırsız app
- ✅ Public repos için

**Eğer private repo veya daha fazla kaynak gerekiyorsa:**

- Streamlit Cloud Teams (ücretli)
- Veya kendi sunucuda Docker ile deploy

## 🎉 Başarılı Deploy!

Uygulama linki: `https://your-app.streamlit.app`

Kuruma gönderirken:

- ✅ Link'i paylaşın
- ✅ DEMO_BİLGİLENDİRME.md'yi gönderin
- ✅ Test senaryolarını çalıştırmalarını isteyin
- ✅ Geri bildirim için süre belirleyin

---

**Sorularınız için:** [İletişim bilgisi]
