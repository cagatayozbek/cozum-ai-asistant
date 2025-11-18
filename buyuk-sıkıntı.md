langchain dokumanlarını incele. sana sıkıntıyı açıklıyorum. ben retrieved dokumanları zaten llm_node da prompt olarak veriyorum. query classification yaptığım kısımdaki langsmithten eriştiğim promptu sana veriyorum:

Bu mesajı TEK bir kategoriye sınıflandır:

- casual: Selamlaşma, teşekkür, veda, kimlik sorusu (merhaba, teşekkürler, hoşçakal, sen kimsin)
- followup: Önceki yanıta bağımlı takip sorusu (tek başına anlamsız)
- question: Okul hakkında bağımsız yeni soru (veri tabanı araması gerekli)

ÖNCEKİ BAĞLAM:
Asistan: Erdemliler Topluluğu, ortaokul kademesindeki öğrencilerimizin gönüllü katılımıyla düzenlenen özel bir faaliyettir. Bu topluluk, öğrencilerimizin gelişimine çok yönlü katkı sağlamayı hedeflemektedir.

Erdemliler Topluluğu'nun temel amaçları ve faaliyetleri şunlardır:

- **Milli ve Manevi Değerleri İçselleştirme:** Öğrencilerimizin kendi kültür ve inanç değerlerini anlamalarını ve benimsemelerini sağlamak.
- **Sosyal Sorumluluk Bilinci Kazanma:** Topluma karşı sorumluluklarını fark etmelerini ve bu yönde adımlar atmalarını teşvik etmek.
- **Sivil Toplum Kuruluşlarıyla İş Birliği:** Çeşitli sivil toplum kuruluşlarıyla ortak projelerde yer alarak öğrencilerimizin toplumsal fayda sağlayan çalışmalara aktif katılımını desteklemek.

Bu hedefler doğrultusunda, topluluğa katılan öğrencilerimizle birlikte **sosyal, kültürel ve sportif etkinlikler** organize edilmektedir. Bu sayede öğrencilerimiz hem kişisel gelişimlerini destekler hem de toplumsal hayata daha aktif ve bilinçli bir şekilde dahil olurlar.
Kullanıcı: lise hakkında bilgi almak istiyorum
Asistan: Lise kadememiz hakkında bilgi almak istediğinizi anlıyorum. Çözüm Eğitim Kurumları olarak lisemizde öğrencilerimizin akademik başarılarının yanı sıra sosyal, kültürel ve fiziksel gelişimlerini de destekleyen kapsamlı bir eğitim sunmaktayız.

Hangi konuda detaylı bilgi almak istersiniz?

- **Genel Ders Saatleri**
- **Eğitim Programları**
- **İngilizce Eğitimi ve Dijital Platformlar**
- **Spor Faaliyetleri**
- **Ücretler**
- **Servis**

Lütfen belirtin, size yardımcı olmaktan memnuniyet duyarım.

ŞU ANKİ MESAJ: "spor faaliyetleri hakkında bilgi verir misin"

ANA TEST: "Bu mesaj önceki yanıt olmadan anlamlı mı?"
→ Selamlaşma/teşekkür/veda = casual
→ Kısa/belirsiz + önceki yanıta bağlı = followup
→ Spesifik okul sorusu = question

ÖRNEKLER:
"Merhaba" / "Teşekkürler" / "Sen kimsin?" → casual
"Kaç saat?" (program tartışmasından sonra) → followup
"Ücret ne kadar?" (hizmet tartışmasından sonra) → followup
"manevi eğitim var mı" → question
"İngilizce eğitimi nasıl?" → question

SADECE kategori adını döndür:

burdaki sıkıntılı nokta şu: ben lise hakkında bilgi almak istiyorum diye sorduğumda bunu şu şekilde retrieve ediyor:

[
[
{
"id": "8bb5a466-66f0-456b-946e-8b7f0cf6c1a7",
"metadata": {
"answer*type": "text",
"chunk_index": 1,
"embedding_hint": "lisede dersler saat kaçta başlıyor, kaçta bitiyor, gün içinde ders saatleri",
"id": "lise-01",
"level": "lise",
"original_content": "• Ders Saatleri: 09.00-16.30",
"question": "Lise ders saatleri nedir?",
"source": "Lise_Haftal_k_Ders_Program*.csv",
"tags": [
"ders saatleri",
"lise",
"başlangıç",
"bitiş",
"09.00",
"16.30"
],
"title": "Ders Saatleri",
"version": "2025-10"
},
"page_content": "Ders Saatleri Lise ders saatleri nedir? lisede dersler saat kaçta başlıyor, kaçta bitiyor, gün içinde ders saatleri • Ders Saatleri: 09.00-16.30",
"type": "Document"
},
0.3038680851459503
],
[
{
"id": "dea21b2c-c69f-423b-a1fe-1406076f5929",
"metadata": {
"answer_type": "table_and_paragraph",
"chunk_index": 8,
"embedding_hint": "lise ingilizce ders saati, 9. sınıf, 10. sınıf, 11. sınıf, main course, think&talk, lingua attack, online kitap okuma",
"id": "lise-08",
"level": "lise",
"original_content": "Lise İngilizce Ders Saatleri\n\nLise\n\nMain Course\n\nThink&Talk\n\n9\nve 10. Sınıf\n\n8\n\n2\n\n11. Sınıf\n\n4\n\n2\n\nLisede Kullanılan Dijital Platform:\nLingua Attack\nonline kitap okuma platformu kullanılmaktadır.",
"question": "Lisede İngilizce ders saatleri nasıldır ve hangi dijital platformlar kullanılır?",
"source": "Lise.VeliBilgilendirmeMetni.docx",
"tags": [
"ingilizce",
"ders saati",
"lise",
"lingua attack",
"dijital platform"
],
"title": "Lise İngilizce Ders Saatleri ve Lingua Attack Platformu",
"version": "2025-10"
},
"page_content": "Lise İngilizce Ders Saatleri ve Lingua Attack Platformu Lisede İngilizce ders saatleri nasıldır ve hangi dijital platformlar kullanılır? lise ingilizce ders saati, 9. sınıf, 10. sınıf, 11. sınıf, main course, think&talk, lingua attack, online kitap okuma Lise İngilizce Ders Saatleri\n\nLise\n\nMain Course\n\nThink&Talk\n\n9\nve 10. Sınıf\n\n8\n\n2\n\n11. Sınıf\n\n4\n\n2\n\nLisede Kullanılan Dijital Platform:\nLingua Attack\nonline kitap okuma platformu kullanılmaktadır.",
"type": "Document"
},
0.3891749382019043
],
[
{
"id": "cc10aa21-aec9-4b7e-8879-1d8ab0b44888",
"metadata": {
"answer_type": "table_and_paragraph",
"chunk_index": 8,
"embedding_hint": "lise ingilizce ders saati, 9. sınıf, 10. sınıf, 11. sınıf, main course, think&talk, lingua attack, online kitap okuma",
"id": "lise-08",
"level": "lise",
"original_content": "Lise İngilizce Ders Saatleri\n\n| Lise | Main Course | Think&Talk |\n| :--- | :--- | :--- |\n| 9 ve 10. Sınıf | 8 | 2 |\n| 11. Sınıf | 4 | 2 |\n\nLisede Kullanılan Dijital Platform:\nLingua Attack online kitap okuma platformu kullanılmaktadır.",
"question": "Lisede İngilizce ders saatleri nasıldır ve hangi dijital platformlar kullanılır?",
"source": "Lise.VeliBilgilendirmeMetni.docx",
"tags": [
"ingilizce",
"ders saati",
"lise",
"lingua attack",
"dijital platform"
],
"title": "Lise İngilizce Ders Saatleri ve Lingua Attack Platformu",
"version": "2025-10"
},
"page_content": "Lise İngilizce Ders Saatleri ve Lingua Attack Platformu Lisede İngilizce ders saatleri nasıldır ve hangi dijital platformlar kullanılır? lise ingilizce ders saati, 9. sınıf, 10. sınıf, 11. sınıf, main course, think&talk, lingua attack, online kitap okuma Lise İngilizce Ders Saatleri\n\n| Lise | Main Course | Think&Talk |\n| :--- | :--- | :--- |\n| 9 ve 10. Sınıf | 8 | 2 |\n| 11. Sınıf | 4 | 2 |\n\nLisede Kullanılan Dijital Platform:\nLingua Attack online kitap okuma platformu kullanılmaktadır.",
"type": "Document"
},
0.39402446150779724
],
[
{
"id": "8cb9d273-fcf3-4780-8729-414476cbb5d7",
"metadata": {
"answer_type": "paragraph_and_table",
"chunk_index": 13,
"embedding_hint": "spor faaliyetleri, beden eğitimi, periyotlu sistem, voleybol, basketbol, okçuluk, masa tenisi, futbol, postür",
"id": "lise-13",
"level": "lise",
"original_content": "Lisede\nSpor Faaliyetleri\n\nÇözüm Koleji olarak, öğrencilerimizin\nbedensel ve zihinsel gelişimlerini desteklemek amacıyla Beden Eğitimi\nderslerini 9’ar haftalık periyotlar hâlinde planlamaktayız. Dersleri yıl\niçerisinde dört farklı spor branşı üzerinden şekillendirerek, her öğrencinin\nyıl sonunda dört farklı spor dalında beceri kazanmasını ve ait hissettiği\nbranşa yönelmesini sağlıyoruz.\nKas ve iskelet sistemi gelişimi yaş\ngruplarına göre farklılık gösterdiği için, spor branşları öğrencilerin fiziksel\ngelişimlerine en uygun olacak şekilde belirlenmektedir. Branş seçimleri, kas ve\niskelet sistemini destekleyen, öğrencilerin eğlenerek sosyalleşmelerini\nsağlayan, postür bozukluklarının giderilmesine yardımcı olan etkinlikler\nüzerinden oluşturulmaktadır.\n\nLise Beden Eğitimi\nve Spor Dersi Periyotları\n\n| | Lise (Kız) | Lise (Erkek) |\n| :--- | :--- | :--- |\n| 1. Periyot | Voleybol | Voleybol |\n| 2. Periyot | Masa Tenisi | Basketbol |\n| 3. Periyot | Okçuluk | Masa Tenisi |\n| 4. Periyot | Basketbol | Futbol |",
"question": "Lisede beden eğitimi ve spor dersleri nasıl planlanır ve branşlar nelerdir?",
"source": "Lise.VeliBilgilendirmeMetni.docx",
"tags": [
"spor",
"beden eğitimi",
"periyot",
"voleybol",
"basketbol",
"futbol",
"okçuluk"
],
"title": "Lisede Spor Faaliyetleri ve Periyotları",
"version": "2025-10"
},
"page_content": "Lisede Spor Faaliyetleri ve Periyotları Lisede beden eğitimi ve spor dersleri nasıl planlanır ve branşlar nelerdir? spor faaliyetleri, beden eğitimi, periyotlu sistem, voleybol, basketbol, okçuluk, masa tenisi, futbol, postür Lisede\nSpor Faaliyetleri\n\nÇözüm Koleji olarak, öğrencilerimizin\nbedensel ve zihinsel gelişimlerini desteklemek amacıyla Beden Eğitimi\nderslerini 9’ar haftalık periyotlar hâlinde planlamaktayız. Dersleri yıl\niçerisinde dört farklı spor branşı üzerinden şekillendirerek, her öğrencinin\nyıl sonunda dört farklı spor dalında beceri kazanmasını ve ait hissettiği\nbranşa yönelmesini sağlıyoruz.\nKas ve iskelet sistemi gelişimi yaş\ngruplarına göre farklılık gösterdiği için, spor branşları öğrencilerin fiziksel\ngelişimlerine en uygun olacak şekilde belirlenmektedir. Branş seçimleri, kas ve\niskelet sistemini destekleyen, öğrencilerin eğlenerek sosyalleşmelerini\nsağlayan, postür bozukluklarının giderilmesine yardımcı olan etkinlikler\nüzerinden oluşturulmaktadır.\n\nLise Beden Eğitimi\nve Spor Dersi Periyotları\n\n| | Lise (Kız) | Lise (Erkek) |\n| :--- | :--- | :--- |\n| 1. Periyot | Voleybol | Voleybol |\n| 2. Periyot | Masa Tenisi | Basketbol |\n| 3. Periyot | Okçuluk | Masa Tenisi |\n| 4. Periyot | Basketbol | Futbol |",
"type": "Document"
},
0.40573155879974365
]
]

ŞU ANKİ MESAJ: "spor faaliyetleri hakkında bilgi verir misin"

dediğimde bunun katagorisi {"category": "question"} olarak dönüyor fakat ben daha önceden bununla ilgili bilgi retrieve edip node llme prompt olarak vermiştim. yani retrieve edilen bir bilgi yeniden retrieve edilmiş.

senden yapmanı istediğim langchain dokumanlarını incele eğer retrieve kararı almayla ilgili bir durum bulursan onu uygulayalım.
eğer dokumanlarda boyle bir bilgi yer almıyorsa boşu boşuna query classification ı şişirmeyelim her dokuman retrieve edilsin. sadece merhaba falan dersek retrieve falan gitmeyelim yada retrieve hiç yapmayalım.

Sakın kodu değiştirme, sadece bana sektör standardında yaklaşım bul ve benimle paylaş
