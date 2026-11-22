# SS1914 — Windows kaynak derlemesi ve oyun testi

## BRF ve module.ini

Bu arşiv Module System kaynaklarını içerir. Oyun ve kurulu **Seddulbahir 1914**
modu gerekir. Depoda mevcut iki saniyelik bolt SMD'si vardır. Şarjör SMD'si,
kurulu BRF ve module.ini depoda bulunmadığından yerelde kontrol edilmelidir.

- OpenBRF ile modun yüklediği BRF'leri aç. Şarjör doldurma iskelet animasyonunun
  kaynak adı tam olarak `rifle_magazine_reload_7` olmalı ve 0–90 frame
  aralığını içermeli. Klip başka adla kayıtlıysa mevcut animasyonu bu adla
  kaydet veya Module System'deki kaynak adını ve frame aralığını gerçek
  değerlerle eşleştir. Yalnız bolt klibine sahipsen şarjör özelliğini kapalı tut.
- BRF'yi modun `Resource` dizininde tut. Satır zaten yoksa kurulu modun
  `module.ini` dosyasına `load_mod_resource = GERCEK_BRF_ADI` ekle.
  `GERCEK_BRF_ADI` yerine dosya adını `.brf` uzantısı olmadan yaz.
  Bolt kaynağı `rifle_bolt_cycle_2s` 0–60 frame olarak ayrı kalır.
- BRF ve module.ini yüklemesi yerel WFaS istemcileri ve sunucusunda eş olmalı.

Native `reload_musket` ve kademeli musket action kayıtları korunur.
Bazı tabancalar da musket reload capability'si kullanır. Global action
değişimi bu silahları etkileyebileceği için özel klip yalnız
`itcf_shoot_musket` sınıfındaki eldeki tüfek/karabina native reload
durumuna girdiğinde görsel olarak istenir. Oyuncu ve AI aynı filtreyi
kullanır. Mevcut bolt deadline ve şarjör işlemleriyle ilgili kaynak motor
durumunu veya mühimmatını ayarlamaz. Var olan R3 hız ayarı aynen kalır.
WFaS'te animasyon önceliği, kademeli reload davranışı, senkronizasyon ve
görsel klibin native doldurmayı kesintiye uğratıp uğratmadığı test edilmelidir.

## Standart build_module.bat

ZIP'i kaynak klasörüne aç. Oyunu kapat. Kurulu modun yedeğini al.
Windows Komut İstemi'nde kaynak dizinine gir ve `python --version` çıktısında
Python 2.7 veya PyPy2'nin Python 2.7 uyumluluğunu doğrula. Boş bir çıktı
dizini kullan. Örnek:

```bat
mkdir C:\wfas-stage-a-output
set "WFAS_EXPORT_DIR=C:\wfas-stage-a-output"
set "WFAS_FIRE_ORDERS_POC=1"
set "WFAS_MAGAZINE_BRF=0"
build_module.bat
```

Standart bat içinde bot testi varsayılan açıktır. Açıkça `0` verilirse
kapanır. BRF doğrulandıysa `WFAS_MAGAZINE_BRF=1` ile yeniden boş bir dizine
derle. Bu değişkeni ayarlamadan yapılan derlemede stok reload görselleri
kullanılır. Derleme konsolunda hata görürsen çıktıyı kurma. Üretilen 32 TXT
dosyasını yedeği alınan modun çalışan kopyasına koy. Aynı çıktıyı tüm
istemciler ve dedicated sunucu için kullan.

## Oyun testi

- Önce normal multiplayer Team Deathmatch aç. Listen host veya dedicated
  ve istemciyle ayrı ayrı dene. F8/F9/F10 ilk satırda
  `[SS1914] F8 ALGILANDI`, `[SS1914] F9 ALGILANDI` ve
  `[SS1914] F10 ALGILANDI` göstermeli. Mesaj ağ veya bot seçimi gerektirmez.
- Başka MP modunda algılama satırından sonra TDM gerekliliği görünür.
  TDM'de ölü oyuncu ve boş seçim uyarılarını kontrol et. Canlı TDM
  oyuncusuyla bot division'ı seç, tuşlar arasında yarım saniye bırak.
  F8 durum özeti, F9/F10 deneme sayısı verir. Bunlar motor kabulü değildir.
- Bot sahipliğini iki oyuncuyla kontrol et. Aynı division'da diğer
  oyuncunun botu değişmemeli. Listen host yalnız kendi yanıtını yerel
  görmeli. Uzak oyuncu yanıtını sunucudan özel olarak almalı.
- Şarjör BRF'si açık derlemede oyuncu ve AI ile hem Çanakkale tüfeğini hem
  stok musket/karabinayı dene. Bolt ve boş şarjör reload'u ayrı kaydet.
  Tabanca, yay, arbalet ve yakın dövüş animasyonlarını karşılaştır.
- Algılama satırı gelmezse mod, oyun tipi ve tuşu bildir. Algılama geliyor
  ama sonuç gelmiyorsa canlılık, seçili division, host türü ve varsa
  `@SS1914` sunucu loglarını PR #12'ye ekle. Native motor geçişi gerçek
  oyun testiyle doğrulanmalıdır.
