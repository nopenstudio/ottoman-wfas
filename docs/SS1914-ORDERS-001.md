# SS1914-ORDERS-001 — Stage A deneyi

Durum **STAGE_A_POC_READY / GAME BLOCKED / USER TEST REQUIRED**. WFaS 1.143
istemcisi ve dedicated server bu ortamda çalıştırılamadı. Başlangıç
`f5aa5088bd3a81c924cf99ee3177476393feeceb`. Deney yalnız derleme sırasında
`WFAS_FIRE_ORDERS_POC=1` verildiğinde ve normal dedicated Team Deathmatch'te çalışır.

## Motor sorusu

`agent_set_wielded_item` (1747) eşya ID'si alır. Mevcut tüfeğin elinde olduğu
durumda bağlı companion ID'sini vermenin aynı fiziksel slottaki kullanım modunu
seçip seçmediği WFaS'te gözlenmelidir. Tüfek elde değilse ilk F9 ana tüfeği
kuşandırmayı, sonraki F9 bağlı modu seçmeyi dener. F10 ana tüfeğe dönüşü dener.
Her istek her uygun bot için en fazla bir kuşanma çağrısı yapar. Mod geçişinin
anlık sonucu ve sonraki F8 ölçümü ayrı kaydedilir.

`mordr_use_melee_weapons` 10'dur. `team_give_order` (1790) hedefi takım ve
division ile alır. Bu API oyuncu sahipliği aktaramadığı için deneydeki ağ isteği
takıma emir vermez. F8, native emrin ayrı bir oyun içi kontrol olarak ölçülmesi
için `team_get_weapon_usage_order` sonucunu ve botun kuşandığı ID'yi kaydeder.
Bu getter takım/division durumunu okur. Native MP komutunun varsa oyuncuya özel
durumunu göstermesi garanti değildir. `mordr_fire_at_my_command` 14 ve
`mordr_fire_at_will` 19 için eşdeğer, sahipliğe güvenli ateş davranışı henüz
doğrulanmadı. F10 yalnız silah modu denemesidir. Stage B motor ve sahiplik
kabulüne kadar bekler.

## Derle ve aynı kaynakları dağıt

1. Draft PR'daki exact HEAD'i checkout et. Kurulumdaki **Seddulbahir 1914**
   klasörünü yedekle. Deneyi özel bir test sunucusunda çalıştır.
2. `WFAS_FIRE_ORDERS_POC=1 python3 tools/build_module.py --python2 /path/to/pypy --output /tmp/wfas-orders`
   ile bir kez derle. `build.log` içindeki 29 processor çıktısını kontrol et.
3. Çıktıdaki derlenmiş `*.txt` dosyalarını mevcut ve birbirine eş WFaS 1.143
   istemci/sunucu **Seddulbahir 1914** mod kurulumlarına aynı paketten kopyala.
   `build.log` ve `generated_sources/` derleme kanıtıdır. Resource, SceneObj
   ve module.ini için mevcut eş kurulumları kullan. Sunucu ve bütün istemcilerde
   en azından `scripts.txt`, `mission_templates.txt` ve `item_kinds1.txt`
   SHA-256 değerlerini karşılaştır. Aynı karşılaştırmayı dağıtılan tüm TXT
   dosyalarına uygulayabilirsin.
4. Test sonunda yedeği geri yükle ya da varsayılan kapalı derlemeyi dağıt.

## Oyun kabulü

1. Dedicated TDM'de A ve B aynı takıma girsin. İkisinin de aynı division'da kendi
   uygun tüfekli botları olsun. C uzak gözlemci olsun. Diğer division'da A'ya
   bağlı bir bot varsa onu da kontrol olarak izle. A ve B F8 ile ayrı ayrı
   envanter modu/owner satırlarını alsın. Satır yoksa seçim, division ve bot
   liderini kontrol et. Bu durum başarılı komut sayılmaz.
2. A aynı division seçiliyken F9'a bassın. Sunucu satırlarını karşılaştır.
   Türk tüfek aralığı 921/922, İngiliz tüfek aralığı 923/924. F8 ile en az bir
   saniye sonra modu tekrar kontrol et. B ve seçimi dışındaki botlar değişmemeli.
   A, B ve C aynı eldeki model ve AI hareketlerini görmeli. Botun modeli,
   fiziksel slotu ve envanter sayısı geçişte korunmalı.
3. Denemeyi iki tüfekle tekrarla. Temas sırasında yalnız ileri saplama beklenir.
   Mevcut kaynak tanımı 24 pierce ve sıfır savurma hasarı içerir. Oyun içi
   hasar kontrolünü zırh ve diğer hasar çarpanlarını hesaba katarak kaydet.
4. Kısmen boşalmış şarjörle F9 → F10 yap. Botun fazladan doldurma tetiklemeden
   kalan atışlarını say. `ammo_before` / `ammo_after` eldeki mod için bir
   teşhistir ve tek başına şarjör sayısını kanıtlamaz. Atıştan sonraki ilk iki
   saniyede F9 ve F10 iste. Bu sırada `request=-1` beklenir. Mevcut deadline ve
   bolt klibinin yeniden başlamadığını ayrıca gözle.
5. Bot ölsün veya yeniden doğsun. A ölüyken ve spectator durumundayken isteği
   tekrarla. Sunucu bu istekleri uygulamamalı. A yeniden doğup yeni division
   seçtiğinde yalnız güncel canlı botlar kabul edilmeli.
6. Ayrı bir kontrol oturumunda, WFaS normal MP menüsü yakın dövüş silahı
   emrini sunuyorsa önce F8, sonra native emir, sonra tekrar F8 kullan.
   Native usage, eldeki ID, saldırı türü ve diğer oyuncunun botlarını kaydet.
   Menü emri sunmuyorsa native karşılaştırma **NOT RUN** kalır. PoC tuşları
   native emri tetiklemez.
7. F9'da `request` paired ID olduğu halde `after` ana tüfek ID'sinde kalırsa
   animasyonu ve AI davranışını da kaydet. Bir setter sonucunu tek başına
   motorun bütün yolları için ENGINE-BLOCKED kanıtı sayma. Geçiş gerçekleşip AI
   hemen geri dönüyorsa anlık ve gecikmeli F8 satırlarını ayrı bildir.
