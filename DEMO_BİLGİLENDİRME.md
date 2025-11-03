**# 🎓 Çözüm Koleji Veli Asistanı - İlk Demo**

- **\*Tarih:\*\*** 3 Kasım 2025
- **\*Durum:\*\*** Erken Aşama Demo (MVP - Minimum Viable Product)
- **\*Demo Adresi:\*\*** [Streamlit üzerinden test edilebilir]
- **--**

**## 📋 Demo Hakkında**

Bu, AI Veli Asistanı projesinin \***\*ilk çalışan versiyonudur\*\***. Temel işlevselliği test etmek ve geri bildirim almak amacıyla hazırlanmıştır.

**### ⚠️ ÖNEMLİ NOT**

Bu bir \***\*prototip/demo\*\*** versiyonudur. Henüz production (canlı kullanım) için hazır değildir. Amacımız:

1. Temel mantığın doğru çalıştığını görmek

2. Sağlanan dokümanların yeterli olup olmadığını anlamak

3. Eksik/yanlış bilgileri tespit etmek

4. Sizin beklentilerinizi netleştirmek

- **--**

**## ✅ ŞU AN ÇALIŞAN ÖZELLİKLER**

**### 1. Temel Sohbet Deneyimi**

- ✅ Kademe bazlı (Anaokulu, İlkokul, Ortaokul, Lise) soru-cevap
- ✅ Çoklu kademe seçimi (örn: "Lise ve ortaokul matematik saatlerini karşılaştır")
- ✅ Doğal dil ile sohbet (komut yazmaya gerek yok)
- ✅ Konuşma geçmişi tutma (takip soruları sorabilme)

**### 2.Soru Sınıflandırma**

- ✅ Selamlaşma, teşekkür gibi basit mesajlara hızlı yanıt
- ✅ Sadece gerçek sorularda dokümanlardan bilgi arama (performans optimizasyonu)
- ✅ Kısa takip sorularını ("Kaç saat?", "Biyoloji ne zaman?") önceki yanıtla ilişkilendirme

**### 3. Kademe Yönetimi**

(Test amaçlı daha sonra seçme işlemi değiştirelecek)

- ✅ Sidebar'dan kolayca kademe seçimi/değiştirme
- ✅ Birden fazla kademe aynı anda aktif olabilir
- ✅ Yeni sohbet başlatma (reset) özelliği

**### 4. RAG (Retrieval-Augmented Generation) Sistemi**

- ✅ Sağlanan dokümanlardan (DOCX) vektör veritabanı oluşturma
- ✅ Semantik arama (anlamsal benzerlik)
- ✅ Sadece dokümanlardan bilgi verme (uydurma yok)
- **--**

**## 🚧 HENÜZ OLMAYAN ÖZELLİKLER (İlerde Eklenecek)**

- ❌ Streaming yanıtlar (kelime kelime görünme)
- ❌ Örnek soru önerileri
- ❌ Sohbet geçmişini kaydetme/yükleme
- ❌ Web ve İnstagramdan veri çekme

**## 🧪 TEST EDİLMESİ GEREKEN SENARYOLAR**

Lütfen aşağıdaki senaryoları test edin ve geri bildirimde bulunun:

**### A) Temel Sorular**

- "Anaokulu programı nedir?"
- "İlkokulda İngilizce kaç saat?"
- "Lise biyoloji ders saati nedir?"
- "Ücretler hakkında bilgi verir misin?"

**### B) Karşılaştırmalı Sorular**

- "Lise ve ortaokul matematik saatlerini karşılaştır"
- "Hangi kademelerde robotik kodlama var?"

**### C) Takip Soruları**

- İlk soru: "11. sınıf programı nedir?"
- Takip: "Biyoloji kaç saat?" (önceki yanıtı kullanmalı)

**### D) Genel Konuşma**

- "Merhaba" / "Günaydın"
- "Teşekkür ederim"
- "Sen kimsin?"

**### E) Eksik/Hatalı Bilgi Tespiti**

- Eğer asistan "Bu bilgi dokümanlarımda yok" derse → NOT EDİN
- Eğer yanlış/eski bilgi veriyorsa → NOT EDİN
- Eğer çok genel yanıt veriyorsa → NOT EDİN
- **--**

**## 📝 SİZDEN BEKLENEN GERİ BİLDİRİMLER**

**### 1. Doküman Kalitesi**

- **\*SORU:\*\*** Sağlanan dokümanlar (DOCX) yeterli mi?

Lütfen kontrol edin:

- **\*Eksik kademeler var mı?\*\*** (Bazı kademeler için bilgi hiç yok mu?)
- **\*Güncel değil mi?\*\*** (Eski akademik yıl bilgileri mi var?)
- **\*Detay seviyesi yeterli mi?\*\*** (Çok yüzeysel mi, yoksa çok detaylı mı?)
- **\*Formatlar düzgün mü?\*\*** (okunabilir mi, tablolar bozuk mu?)

**### 2. Yanıt Kalitesi**

- **\*SORU:\*\*** Asistanın yanıtları beklentinizi karşılıyor mu?

Lütfen değerlendirin:

- **\*Üslup uygun mu?\*\*** (Çok resmi mi, çok samimi mi?)
- **\*Uzunluk ideal mi?\*\*** (Çok kısa/çok uzun?)
- **\*Netlik var mı?\*\*** (Anlaşılır mı, karmaşık mı?)
- **\*Profesyonel mi?\*\*** (Okul imajına uygun mu?)
- **\*NOTLARINIZ:\*\***

```

[Buraya yanıt kalitesi hakkında notlarınızı yazın]

```

**### 3. Eksik/Yanlış Bilgiler**

- **\*SORU:\*\*** Hangi konularda yanlış veya eksik bilgi veriyor?

Lütfen örneklerle belirtin:

- **\*ÖRNEK FORMAT:\*\***

```

Soru: "Anaokulu ücretleri nedir?"

Beklenen: "2024-2025 dönemi için 45.000 TL/yıl"

Verilen: "Bu bilgi dokümanlarımda yok"

SORUN: Ücret bilgisi dokümanlarda eksik

(Ücreti asistan zaten göstermeyecek bu sadece bir örnek)

```

- **\*SİZİN ÖRNEKLER:\*\***

```

[Buraya test ederken bulduğunuz hataları/eksiklikleri yazın]

```

**### 4. Ek Özellik İstekleri**

- **\*SORU:\*\*** Hangi özellikler mutlaka olmalı?

Öncelik sırasına göre:

1. [...]

2. [...]

3. [...]

**## 📞 İLETİŞİM & DESTEK**

- **\*Demo testi sırasında sorun mu yaşadınız?\*\***
- Hataları not edin (ekran görüntüsü alın)
- Hangi soruya ne yanıt verdi kaydedin
- Beklediğiniz davranışı açıklayın
- **\*Geri bildirimlerinizi nasıl iletebilirsiniz?\*\***
- Bu dokümanı doldurup geri gönderin
- Ekran görüntüleri ile örnekler paylaşın

- **--**

**## 🙏 TEŞEKKÜRLER**

Zaman ayırıp bu demo'yu test ettiğiniz için teşekkür ederiz. Geri bildirimleriniz projenin başarısı için \***\*kritik önem\*\*** taşımaktadır.

İyi testler! 🚀

- **--**
- **\*Not:\*\*** Bu doküman projenin şu anki durumunu yansıtmaktadır. Her demo sonrası güncellenecektir.
