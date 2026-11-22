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
  F9/F10 hedef sayısını, yapılan denemeleri, sonuçları ve istenen modda
  gözlenen botları ayrı gösterir. Güvenli geçiş yolu bulunmadığı için bu
  sürümde deneme sayısı sıfırdır. 'ATLANDI' hedeflenen moda zaten sahip
  olmayan botları sayar. F8 mevcut durumu okur.
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

Durum **ENGINE-BLOCKED**. Oyun testinde paired ID denemesi botu değiştirmedi.
Bu setter F9/F10 yolundan kaldırıldı.

- [Native emir sabiti](../header_mission_templates.py#L38) ve
  [team_give_order](../header_operations.py#L834) takım/division düzeyindedir.
  API oyuncu sahipliği parametresi almaz. itp_next_item_as_melee bağlantısının
  native melee emri altında gerçekten seçildiğine ilişkin WFaS 1.143 oyun
  kanıtı bulunamadı. Oyuncu izolasyonu doğrulanamadığından emir kullanılmaz.
- [agent_get_item_slot](../header_operations.py#L852) fiziksel slottaki ID'yi
  okuyabilir. [agent_unequip_item](../header_operations.py#L813) item ID'si
  alır. [agent_equip_item](../header_operations.py#L821) boş slot gerektirir
  ve WFaS başlığında hedef slot parametresi yoktur. Botun tek tüfek taşıması
  birden fazla slot boş olabileceği anlamına gelir. Çıkarıp eklemek aynı
  slotu veya aynı fiziksel item örneğini garanti etmez.
- [agent_get_ammo](../header_operations.py#L753) eldeki silah için mühimmat
  döndürür. [agent_set_ammo](../header_operations.py#L816) item ID'si alır.
  Belgelenen API yüklü şarjör, yedek mühimmat ve native reload durumunun
  fiziksel slot bazında bağımsız olarak geri yüklenmesini sağlamaz.
  Swap veya rollback sırasında şarjör durumunu koruma garantisi yoktur.
- F9/F10 envanter, mühimmat, native emir veya bolt slotlarına yazmaz.
  Hız sınırı ve bot sahipliği kontrolleri yerinde durur. F8 ile mevcut
  eldeki ID gözlenebilir. AI'nın yeni moda geçip orada kalması bu sürümde
  sınanmış sayılmaz.

P0 kabulü için Çanakkale tüfeğiyle yedi atıştan sonra reload'un bittiğini
ve sekizinci atışın çıktığını aynı kayıtta göster. Stok musket/karabina ile
normal reload'u, iki çift namlulu tabanca ile reload ve sonraki atışı da
ayrı dene. F9/F10'u reload sırasında ve bolt deadline içindeyken dene.
Uygun hedef istenen modda değilse bekleme nedeni görünmeli. Deneme sayısı sıfır kalmalı.
