# Yapılacaklar Listesi - Çözüm AI Veli Asistanı

## 🎯 Öncelikli İyileştirmeler

### 1. Prompt İyileştirmeleri ✅ (Kısmen Tamamlandı)

- [x] Üslup düzeltmeleri (sen/siz problemi)
- [x] Genel soru rehberliği
- [ ] **Prompt'u daha kısa ve net yap** - Şu an çok uzun
- [ ] **Few-shot examples ekle** - AI'a örnek diyaloglar göster
- [ ] **Temperature ayarla** - Şu an yok, tutarlılık için 0.3-0.5 arası dene

### 2. Conditional Retrieval (Önemli!) 🔥

- [ ] **Her soruda retrieve yapma**
  - Genel konuşma ("merhaba", "teşekkürler") → Retrieve atla
  - "Sen kimsin?" → Retrieve atla
  - "Kademe değiştir" → Retrieve atla
  - Sadece OKUL HAKKINDA sorularda retrieve yap
- [ ] **Router node ekle**: START → router → (retrieve VEYA direkt llm)
- [ ] **Classifier fonksiyonu**: Sorunun türünü belirle (greeting, question, command)

### 3. CLI Komutlarını Kaldır 🚧

- [ ] **/help, /seviye, /temizle** komutlarını kaldır
- [ ] **Doğal dil ile her şeyi yap:**
  - "Başka bir kademe ekle" → Otomatik kademe ekleme
  - "Sohbeti temizle" → Thread reset
  - "Yardım lazım" → Rehberlik göster
- [ ] **welcome_and_get_levels() fonksiyonunu daha akıcı yap**
  - CLI menü yerine conversational onboarding

### 4. Kademe Yönetimi Stratejisi 💡

- [ ] **Akıllı kademe önerisi:**
  - Kullanıcı profili çıkar (hangi konularla ilgileniyor)
  - "Lise programları" dediğinde otomatik liseyi ekle, onay isteme
- [ ] **Kademe geçişi daha smooth:**
  - Tag sistemi yerine state update ile yap
  - Kullanıcıya bildirim: "✨ Lise kademesi eklendi"
- [ ] **Çoklu kademe sonuçlarını düzenle:**
  - Aynı anda 3 kademe seçiliyse, ilgili olanı önce göster

## 🚀 Gelecek Özellikler

### 5. Performans İyileştirmeleri

- [ ] **Streaming responses** - Yanıtları kelime kelime göster
- [ ] **Cache optimization** - Sık sorulan sorular için cache
- [ ] **Async retrieval** - Retrieval'ı async yap, hız kazanımı

### 6. Kullanıcı Deneyimi

- [ ] **Typing indicator** - "Yazıyor..." animasyonu
- [ ] **Markdown formatting** - Listeleri, bold'ları düzgün göster
- [ ] **Hata mesajlarını iyileştir** - Kullanıcı dostu hatalar
- [ ] **Session persistence** - Thread ID'yi dosyaya kaydet, kalıcı sohbetler

### 7. Akıllı Özellikler

- [ ] **Intent classification** - Kullanıcının ne istediğini daha iyi anla
- [ ] **Multi-turn planning** - Karmaşık soruları adımlara böl
- [ ] **Follow-up suggestions** - "Bunları da sormak ister misiniz?" önerileri
- [ ] **Context-aware responses** - Önceki sorulara göre akıllı yanıtlar

### 8. RAG İyileştirmeleri

- [ ] **Hybrid search** - Keyword + semantic search birleştir
- [ ] **Reranking** - FAISS sonuçlarını yeniden sırala (CrossEncoder)
- [ ] **Query expansion** - Kullanıcı sorgusunu genişlet
- [ ] **Document chunking optimization** - Chunk boyutunu optimize et

### 9. Test & Monitoring

- [ ] **Unit tests** - Kritik fonksiyonlar için test
- [ ] **Integration tests** - Graph flow testleri
- [ ] **Conversation logging** - Tüm konuşmaları logla (analytics için)
- [ ] **Performance metrics** - Latency, success rate ölç

### 10. Production Hazırlığı

- [ ] **Environment configs** - Dev/prod ayırımı
- [ ] **Rate limiting** - API çağrılarını sınırla
- [ ] **Error recovery** - API hatalarında retry mekanizması
- [ ] **Health checks** - Sistem sağlık kontrolü

## 📝 Dokümantasyon

- [x] CHATBOT_GUIDE.md güncellendi
- [ ] API documentation - Fonksiyonları dokümante et
- [ ] Architecture diagram - Sistem mimarisini görselleştir
- [ ] Deployment guide - Nasıl deploy edilir

## 🐛 Bilinen Sorunlar

- [ ] Bazen yanıt tekrar ediyor - Prompt'ta daha net kurallar gerek
- [ ] Gemini 2.5 Flash model adı doğru mu? (gemini-2.0-flash-exp daha stabil)
- [ ] Temperature parametresi yok - Tutarsızlık olabilir

---

## 📊 Öncelik Sırası

**Hemen Yapılmalı (Bu Hafta):**

1. Conditional retrieval (router node)
2. Prompt kısaltma + few-shot examples
3. Temperature ekleme
4. CLI komutlarını kaldırma

**Kısa Vadede (Bu Ay):** 5. Kademe yönetimi iyileştirme 6. Streaming responses 7. Intent classification 8. Conversation logging

**Uzun Vadede (Gelecek):** 9. Hybrid search + reranking 10. Production deployment
