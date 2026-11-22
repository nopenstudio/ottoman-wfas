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

Önceki sürüm, motor reload durumundayken `agent_set_animation` ile başka bir
action başlatıyordu. Gerçek oyunda reload tamamlanmadı ve tekrarlandı.
Bu sonuç native action'ın kesilmesiyle uyumlu. Motorun iç durumunu bu
ortamda ölçemedik.

Yeni sürümde `WFAS_MAGAZINE_BRF=1` iken dört native musket reload action'ı
doğrudan aynı şarjör kaynağını kullanır. Tam klip 0–90, kademeli devam
aralıkları 29–90 ve 71–90'dır. Native action ID, süre ve hız ölçekleme
bayrakları korunur. Bu yüzden klibin oyun içi oynatma süresi sabit 3 saniye
olarak garanti edilmez. Tüfek ve karabinalar musket reload capability'sine
yönlendirilir. Musket yolunu paylaşan iki çift namlulu tabanca pistol
reload capability'sine alınır. Diğer tabancalar, yay, arbalet ve yakın
dövüş bağlantılarına dokunulmaz. Deneysel 100 hız ayarı kaldırıldı.
Doldurma, kesinti ve ateşe hazır olma işi motora bırakılır. Oyuncu ve AI
aynı native action kayıtlarını kullanır. Bolt klibi ve deadline ayrı kalır.

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
  F9/F10 hedefi, setter ile denenen geçişi ve isteğin hemen ardından elde
  gözlenen modu ayrı sayar. Reload devam ediyorsa veya bolt deadline
  dolmadıysa setter çağrılmaz. `GECIS GOZLENMEDI` anlık item ID sonucudur.
  Bir saniye sonra F8'e basarak AI modunun kalıp kalmadığını karşılaştır.
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

## Süngü yolu ve motor sınırı

Önceki oyun testinde paired melee ID isteği hiçbir botu değiştirmedi.
`agent_set_wielded_item` bir item ID'si alır. Yayımlanan WFaS 1.143
operation tablosunda bağlı item modunu doğrudan seçen veya okuyabilen
ayrı bir API bulunmadı. `agent_get_wielded_item` elde bildirilen item ID'sini
okur. Bu ID, geçici AI seçimini veya motorun iç modunu tek başına kanıtlamaz.
`agent_set_attack_action` saldırı hareketi seçer. Botun eşya modunu ayarlamaz.

`mordr_use_melee_weapons` ve `mordr_use_ranged_weapons` native takım
emirleridir. `team_give_order` takım ve division alır, sahiplik almaz.
Aynı division'ı paylaşan başka oyuncunun botlarına uygulanabilecek bir
emir gönderilmez. F9/F10 sahiplik kapsamındaki birer setter denemesi
olarak kalır. Testte anlık ve bir saniye sonraki F8 çıktısını, ayrıca
sunucu logundaki before/request/after, attack_state ve native_usage
alanlarını birlikte kaydet.

P0 kabulü için Çanakkale tüfeğiyle yedi atıştan sonra reload'un bittiğini
ve sekizinci atışın çıktığını aynı kayıtta göster. Stok musket/karabina ile
normal reload'u, iki çift namlulu tabanca ile reload ve sonraki atışı da
ayrı dene. F9/F10'u reload sırasında ve bolt deadline içindeyken dene.
Bekleme nedeni görünmeli ve o istek için setter deneme sayısı artmamalı.
