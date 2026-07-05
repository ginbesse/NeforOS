# NeforOS

NeforOS, gerçekçi bir mobil işletim sistemi hissi veren, tarayıcı üzerinden çalışan bir web tabanlı shell projesidir. Instagram, WhatsApp, Netflix, mesaj, kamera, tarayıcı, galeri ve mağaza akışlarını taklit eden ama kullanıcı etkileşimiyle çalışan bir deneyim sunar.

## Neden bu proje popüler olabilir?

- Gerçek telefon hissi veren arayüz
- Akıllı ekran, canlı durumlar, mesaj ve çağrı akışları
- Galeri, yükleme, favori ve albüm oluşturma gibi kullanıcı odaklı deneyimler
- Termux üzerinde kolayca kurulum
- Mobil cihazınıza benzer bir sanal işletim sistemi gibi çalışır

## Özellikler

- Ana ekran ve uygulama başlatma
- Batarya, depolama, ağ ve sistem durumu
- Browser arama akışı
- Mesajlaşma, kişi izni ve konuşma geçmişi
- Kamera önizleme ve çağrı akışı
- Galeri: görsel yükleme, favori, albüm oluşturma
- Mağaza benzeri kurulum akışı

## Kurulum

### 1) Depoyu klonla

```bash
git clone <repo-url>
cd Nefor
```

### 2) Python bağımlılıklarını kur

```bash
pip install -r requirements.txt
```

### 3) Uygulamayı çalıştır

```bash
python app.py
```

Ardından tarayıcıda şu adrese git:

```text
http://127.0.0.1:8000
```

## Termux ile kurulum

Termux üzerinde çalıştırmak oldukça kolaydır:

```bash
pkg update && pkg upgrade
pkg install python git
pip install -r requirements.txt
python app.py
```

Daha sonra cihazınızdaki bir tarayıcıdan:

```text
http://localhost:8000
```

veya cihaz IP'niz üzerinden erişebilirsiniz.

## SH DOSYASI OLARAK SİSTEM KURULUMU
İlk olarak ana klasöre gidiniz.
cd Nefor

İkinci olarak kurulum betiğini çalıştırınız.
chmod +x install.sh start.sh

Üçüncü olarak kurulumu başlatınız.
./install.sh

## İleriye dönük fikirler

- Gerçek dosya sistemi desteği
- Kamera ve galeri için medya yükleme
- Daha gerçekçi uygulama geçişleri
- Arka planda çalışan servisler
- Termux ve Android cihazlarla daha derin entegrasyon
