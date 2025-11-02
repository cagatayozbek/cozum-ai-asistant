# 🎓 Çözüm Eğitim Kurumları - AI Veli Asistanı: Chatbot Kullanım Kılavuzu

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

### 🧠 Sohbet Geçmişi

Chatbot son 5 mesajınızı hatırlar ve bağlamsal yanıtlar verir:

```
Siz: Matematik dersleri var mı?
Asistan: Evet, matematik dersleri...

Siz: Kaç saat?                    # "Matematik dersleri" bağlamında
Asistan: Haftada X saat...        # Önceki soruyu hatırlıyor
```

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
# Manuel indeks oluşturma
python retriever.py "test" --recreate
```

### ⚠️ Yanıtlar yavaş

**Normal:** İlk sorgu FAISS indeksini yükler (5-10 saniye)
**Sonraki sorgular:** Hızlı (1-2 saniye)

### 🐛 Program donuyor

**Ctrl+C** ile güvenli çıkış yapabilirsiniz:

```
^C
👋 Program sonlandırıldı. İyi günler!
```

## 📊 Örnek Sohbet Senaryoları

### Senaryo 1: Anaokulu Velisi

```
Seçiminiz: 1

Siz: Çocuğum ilk kez okula başlayacak, uyum programınız var mı?
Asistan: Evet, okulumuzda oryantasyon ve uyum programı...

Siz: İngilizce dersleri kaç yaşında başlıyor?
Asistan: İngilizce eğitimi anaokulundan itibaren başlamaktadır...

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

✅ **Hızlı yanıtlar** → Anında bilgi
✅ **Çoklu kademe** → Tüm çocuklarınız için
✅ **Bağlamsal** → Doğal sohbet
✅ **Güvenilir** → Sadece resmi belgelerden bilgi

**Not:** Asistan sadece mevcut belgelerdeki bilgileri verir. Özel durumlarınız için okulumuzla doğrudan iletişime geçmenizi öneririz.

---

**Destek:** Teknik sorunlar için `github.com/cagatayozbek/cozum-ai-asistant` adresinden issue açabilirsiniz.
