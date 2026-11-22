# SS1914 — İzole native süngü deneyi

Bu dal 04cd8363d89077aae7e9a6ab60e1dae74ab5a143 referansından ayrılır.
PR #12'deki testten ayrı bir Windows kaynak derlemesidir. Motorun bağlı
süngü modunu seçip seçmediği ilk oyun testinde ölçülecek.

## Derleme ve oturum

1. Seddulbahir 1914 kurulumunun yedeğini al. Windows Komut İstemi'nde
   Python 2.7 veya PyPy2 ile kaynak dizininde çalış. `WFAS_EXPORT_DIR`
   değişkenini boş çıktı klasörüne ayarla.
2. `set "WFAS_NATIVE_BAYONET_EXPERIMENT=1"` ve
   `set "WFAS_FIRE_ORDERS_POC=1"` komutlarını çalıştır. Ardından
   `build_module.bat` çalıştır. Aynı derlenmiş TXT'leri istemci ve dedicated
   sunucudaki test kopyasına yerleştir. BRF ve reload ayarlarını
   [mevcut Windows yönergesine](SS1914-WINDOWS-SOURCE.md) göre koru.
3. Şifreli, özel/LAN dedicated TDM aç. Tek insan oyuncu olarak bağlan.
   Kendi Çanakkale tüfekli botlarının bulunduğu tek division'ı seç.
   Hedef division'da oyuncunun kendi karakteri, sahipsiz bot veya diğer
   birlik bulunursa istek reddedilir. Botların yalnız eşleşen Çanakkale
   tüfeği ve uygun mühimmatını taşıması gerekir. Reload ve bolt bitmeden
   emir verilmez.

Deney bayrağı varsayılan kapalıdır. Deney derlemesini açık bir sunucuda
kullanma. Native takım/division emri motor içinde kalıcı olabilir.
Testi bitirirken sunucuyu kapat veya görevi yeniden başlat ve normal
oturum için deney bayrağı kapalı kaynakla derlenen dosyaları kullan.

## Ölçüm

- F8 ile **önce** örnek al. Dedicated logda her bot için
  `@SS1914 SAMPLE` satırında `ms`, `bot`, `division`, `wielded_item`
  ve `usage_order` görünür.
- Yarım saniye sonra F9. `@SS1914 NATIVE` satırında native melee emrinin
  çağrısı ve hemen ardından `action=1` SAMPLE satırları bulunur.
  Sol altta yalnız çağrı bilgisi görünür.
- Yaklaşık bir saniye sonra F8. Aynı bot ID'lerini ve `ms` farkını
  karşılaştır. Beklenen çiftler Türk 921/922, İngiliz 923/924.
  Görsel saplama ve eldeki ID'yi birlikte kaydet. Sonra F10 ve bir
  saniye sonra F8 ile native ranged dönüşünü ölç.
- Emir değerleri melee 10 ve ranged 11. Getter çıktısı ve eldeki item ID
  ayrı kanıtlardır. Emir değerinin değişmesi modun değiştiğini kanıtlamaz.
- İkinci bir oyuncu spectator olarak bağlanırsa F9/F10'u dene.
  RED beklenir ve yeni `NATIVE` satırı oluşmamalı. Bu kontrol için
  taze görev başlat, önceki native emir durumunu taşımamaya dikkat et.

Kaynak motorun reload, bolt, slot ve mühimmatına doğrudan yazmaz.
Gerçek geçiş, modun kalıcılığı ve motorun mühimmatı koruması oyun
testine bağlıdır.
