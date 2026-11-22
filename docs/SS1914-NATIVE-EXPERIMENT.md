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

## Windows oyun sonucu ve RED teşhisi

59ef87e8 Windows oyun testinde reload tamamlandı. F9 ile süngü geçişi
gözlenmedi. F10 dönüşü ölçülemedi. O oturuma ait sunucu logu burada
bulunamadığı için native çağrının çalışıp çalışmadığı belirsizdir.
Önceki paired-ID setter deneyi ayrıca başarısızdır ve geri eklenmedi.

Bu revizyon oyun davranışına yeni bir geçiş yöntemi eklemez. Mevcut
izole deneyin kararını etiketler. F9/F10 için logu filtrele:

    Select-String -Path .\SUNUCU_LOGU.txt -Pattern '@SS1914 (NATIVE|RED|SAMPLE)'

- `NATIVE ... order=10` ve ilgili `SAMPLE` satırları varsa native melee
  çağrısı yapılmıştır. Hemen sonraki örnekte ve bir saniye sonraki
  F8'de eldeki tüfek ile davranış değişmiyorsa native yöntem bu
  oturumda başarısızdır. `order=11` yalnız dönüş isteğini gösterir.
- `RED reason=N agent=ID` varsa native emir çağrılmamıştır. Ekrandaki
  Türkçe satır ilk reddi açıklar. `agent=-1` bir oturum koşulunu gösterir.
  Birden çok uygunsuz bot varsa ilk ihlal eden agent kaydedilir.
- İki satır da yoksa önce deney bayrağını ve dedike sunucuya kurulan
  derlemeyi kontrol et. F8 ile sunucuya ulaşıldığını doğrula. F9'dan önce
  canlı ol, seçim yap, en az yarım saniye bekle. Eski logda satırın
  bulunmaması tek başına bir motor sonucu vermez.

| Kod | RED nedeni |
| --- | --- |
| 1–5 | Sırasıyla sunucu yetkisi, dedicated, TDM, Captain, geçersiz emir |
| 6–10 | Şifre eksik, insan oyuncu sayısı, pasif komutan, tek division seçilmedi, boş division |
| 11–14 | Division'da oyuncu karakteri, insan tipi olmayan agent, farklı bot sahibi, aktif reload |
| 15–18 | Bolt beklemesi, uygunsuz birlik türü, tek Çanakkale tüfeği yok, ek silah |

## Tek slotu dönüştürme — ENGINE-BLOCKED

Tek botta bile mevcut WFaS 1.143 başlığında `agent_equip_item` hedef
fiziksel slot kabul etmez. `agent_get_ammo` ve `agent_set_ammo` yüklü
şarjör, yedek ve native reload durumunu fiziksel slot bazında ayrı ayrı
yedekleyip geri yükleme sözleşmesi sağlamaz. Çıkarıp yeniden takma ile
yedinci mermi kapasitesini korumak tek başına kalan merminin korunduğunu
kanıtlamaz. Silahı geri takma da özgün item örneğini geri getirmez.
Bu nedenle tek bot için bile envanter dönüşümü eklenmedi. Çalışan P0
reload, bolt, mühimmat ve animasyon kaynaklarına dokunulmadı.
