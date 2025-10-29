Çözüm Veli Asistanı

Bu proje, anaokulu ile ilgili bazı dosyaları ve küçük bir yardımcı script (`docx-converter.py`) içerir.

Dosyalar:

- `anaokulu.json` - Proje verileri (JSON).
- `Anaokulu.md`, `Anaokulu.txt` - Metin belgeleri.
- `docx-converter.py` - DOCX dönüştürme yardımcı betiği.

Kısa yardımcı betikler

Projede platforma özel çalıştırma kolaylığı için iki yardımcı betik eklendi:

- Windows PowerShell: `run-windows.ps1` — PowerShell'de sanal ortamı etkinleştirip scripti çalıştırır.
- macOS / Linux: `run-unix.sh` — Bash ile sanal ortamı etkinleştirip scripti çalıştırır. Çalıştırılabilir yapmak için macOS'ta: `chmod +x run-unix.sh`

Örnek kullanım:

- Windows PowerShell: `.un-windows.ps1 -Input "Anaokulu.VeliBilgilendirmeMetni.docx"`
- macOS / Linux: `./run-unix.sh Anaokulu.VeliBilgilendirmeMetni.docx`

Kullanım:

1. Yerel bir Git deposu oluşturun ve ilk commit'i yapın.
2. İsterseniz GitHub'da bir repo oluşturup uzak origin ekleyin ve push yapın.

Not: Uzak repo oluşturulmasını isterseniz devam etmeden önce GitHub kimlik doğrulaması veya `gh` CLI erişimi sağlayın.
