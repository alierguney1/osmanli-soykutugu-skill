---
name: devlet-arsivleri-soykutugu
description: >-
  Use when researching Turkish or Ottoman genealogy (soy ağacı, soy kütüğü,
  ata kaydı, eski köy adı, mübadil/muhacir) using e-Devlet Alt-Üst Soy PDFs,
  Devlet Arşivleri (BOA/BCA) catalogs, or Ottoman manuscript registers
  (NFS.d, ML.VRD.TMT.d, MŞH.ŞSC.d, A.{RSK.d, MAD.d, TT.d, TK.GM.d), or when
  transcribing, cropping, and verifying Ottoman archival images.
---

# Devlet Arşivleri Soy Kütüğü, Paleografik Doğrulama ve Köy Tarihi Becerisi

Bu beceri, **e-Devlet Alt-Üst Soy Bilgisi** belgesindeki kayıt sınırını ("Kütük Duvarı", 1881–1905) aşarak **T.C. Cumhurbaşkanlığı Devlet Arşivleri Başkanlığı Kataloğu** (`https://katalog.devletarsivleri.gov.tr`) ve indirilen filigransız defter görüntüleri üzerinden **anne ve baba tarafı soy kütüğünü**, **köyün eski adını ve idari evrimini** 16. yüzyıla kadar **koordinatlı kırpıntı kanıtıyla** araştırır.

> **Öncelik Kuralı:** Çalışılan depoda projeye özgü bir ajan talimat dosyası (`CLAUDE.md` / `AGENTS.md`) varsa, projeye özel dosya yolları ve kurallar bu becerinin üzerine çıkar.

### Başvuru Kılavuzları ve Araçlar (İhtiyaç Duyuldukça Yükleyin)
- **Fon Kodları, İcmal Uyarısı, Yoklama `Hâne/Numro` Köprüsü, Takvim, Varyantlar, Rakam Tuzakları ve Sözlük:** [references/fon-kodlari-ve-paleografya-rehberi.md](./references/fon-kodlari-ve-paleografya-rehberi.md)
- **Balkanlar, Adalar, Girit, Kırım ve Kafkasya Göçmen/Mübadil Rehberi:** [references/gocmen-ve-mubadil-rehberi.md](./references/gocmen-ve-mubadil-rehberi.md)
- **Depo Mimarisi, Kırpıntı CSV/HTML Proofread, Kişi Dizini, Homonim Köy Ayrımı, Karar-Modeli Kalibrasyonu ve `[CLAIM]` Protokolü:** [references/veri-mimarisi-ve-dogrulama.md](./references/veri-mimarisi-ve-dogrulama.md)
- **Tarayıcı İçi WAF-Korumalı Katalog Yardımcıları (`Chrome DevTools MCP`):** [scripts/dab_helpers.js](./scripts/dab_helpers.js)
- **Varak Bölme, 1:1 Piksel Kesit, Kırmızı Çerçeveli Önizleme ve HTML Proofread Aracı:** `python3 scripts/crop_and_verify.py --help` ([scripts/crop_and_verify.py](./scripts/crop_and_verify.py))
- **İsteğe Bağlı Decision-Model (`d1.2-ultra`) Kırpıntı Doğrulama & Hane Eşleştirme Aracı:** `python3 scripts/verify_d1.py --help` ([scripts/verify_d1.py](./scripts/verify_d1.py)) — yalnızca `LIQUID_API_KEY` varsa kullanılır
- **Hazır Kullanım İstemleri:** [examples/ornek-kullanim-promptlari.md](./examples/ornek-kullanim-promptlari.md)

---

## Zorunlu Altın Kurallar (Sıfır Taviz)

**Kuralların lafzını delmek, ruhunu delmektir. Süre baskısı veya önizleme kolaylığı bu kuralları askıya almaz.**

1. **Kanıt Seviyesi (`A/B/C/D` + `[SÜLALE İZİ]`) ve Kırpıntı Eşiği:**
   - **A:** Birincil belge doğrudan ilişkiyi belirtir (nüfus/yoklama kaydında ad+baba+hane veya şer'iyye terekesi) **ve** koordinatlı kırpıntıyla doğrulanmıştır.
   - **B:** Birincil belge var ama bağ dolaylıdır (aynı hane, `+ΔYıl` yaş uyumu, komşu kayıt) **ve** koordinatlı kırpıntıyla doğrulanmıştır.
   - **C:** İkincil/türev kaynak (tez, kitap, aile anlatısı) veya kırpıntısız / filigranlı ön okuma.
   - **D:** Tahmin / doğrulanmamış aday.
   - **`[SÜLALE İZİ]`** *(kan bağı değil)*: 15.–17. yy. tahrir/avârız defterlerinde (`TT.d`, `MAD.d`) aynı köyde geçen aynı ad veya lakap — aradaki kuşaklar belgelenmeden **asla** `A`/`B` veya üst soy bağı ilan edilemez.
   - **Kırpıntı Şartı:** Orijinal görüntüdeki koordinatlı 1:1 kırpıntısı kaydedilip kontrol edilmemiş hiçbir okuma **`B` veya `A`** düzeyinde bağa dayanak yapılamaz.

2. **Harf/Rakam Düzeyinde `[?]` ve İzli Düzeltme (Sıfır Uydurma):**
   - Okunamayan veya emin olunmayan **her kelime, tekil harf, hece, nokta ve rakam** mutlaka `[?]` ile ve olası alternatifleriyle işaretlenir (örn. `Kös[e]ler[?]`, `45[?]/43[?]`, `Hüseyin[?/Hasan?]`, `filigran[?]`).
   - Düzeltmelerde eski okuma silinmez; transkripsiyonda `~~eski~~ **yeni**`, kırpıntı CSV'sinde `not` sütununa düzeltme açıklaması yazılır.
   - Filigranlı düşük çözünürlüklü önizlemeden kesin okuma yapılmaz.

3. **Ham Veri Değişmez, Kütük ≠ Biyolojik, Çelişki Gizlenmez:**
   - Ham girdilere (`data/source/` — e-Devlet PDF, ham GEDCOM) dokunma; türev çıktıları ayrı dizine (`data/derived/`) yaz.
   - e-Devlet *Alt-Üst Soy Bilgisi* resmi nüfus kütüğünü gösterir; üvey/evlatlık bağları kütükte "anne/baba" görünebilir. Biyolojik bağ esas alınır, kütük bağı açık notla belirtilir; çelişkiler `research/leads/` altında izlenir. Aynı ön ada sahip iki eş asla birleştirilmez.

4. **Gizlilik, Şifre, CAPTCHA ve WAF (`HTTP 418`) Güvenliği:**
   - Kullanıcının T.C. kimlik no veya e-Devlet şifresi **asla** istenmez; yaşayan kişilerin kişisel verileri dış servislere gereksiz yere gönderilmez.
   - e-Devlet girişi, oturum zaman aşımı veya CAPTCHA çıktığında **derhal dur** ve kullanıcının tarayıcıda bizzat tamamlamasını bekle.
   - `BelgeGoster.aspx` sunucusuna **asla paralel (`Promise.all`) çoklu istek atma**; paralel istekler güvenlik duvarını (`HTTP 418 — Erişim Engellendi`) tetikler. Yalnızca sıralı ve **`≥ 1800 ms`** aralıklı istek kullan; `HTTP 418` alınırsa otomatik çekimi derhal durdur.

5. **Brute-Force Yapma — Ama Hedef Köyü Tam Oku:**
   - **Katalog / indirmede:** 300–500 sayfalık defteri körlemesine satın aldırma. Önce katalog özetinde **icmal vs. mufassal** kontrolü yap (icmal defterlerinde şahıs adı yoktur — alma!), sonra **fihrist (`Mi=1..5`)** veya örnekleme ile **`Poz (Mi) ≠ Varak (vr.)` ofsetini** hesaplayıp yalnızca hedef köylerin bulunduğu poz aralığını tespit et.
   - **Okumada:** İlgisiz tüm köyleri 1. sayfadan sona kadar brute-force okuma; hedef köyleri nokta atışı bulup 1–2 köylük küçük parçalar halinde ilerle. Ancak **hedef köyün içine girince** sadece tek kişiyi cımbızlama — aynı lakabı/kökü taşıyan amca, kardeş ve yan kol hanelerini yakalamak için **o köyün tüm hanelerini** oku.

6. **Çok Oturumlu Çalışmada `[CLAIM]`:** Depoda birden fazla oturum/ajan çalışıyorsa bir defter/köy okumasına başlamadan önce `[CLAIM / ÜZERİNDE ÇALIŞILIYOR]` notuyla ilgili aralığı işaretle (bkz. [veri-mimarisi-ve-dogrulama.md](./references/veri-mimarisi-ve-dogrulama.md)).

---

## Çalışma Modları

- **Mod A — Canlı Katalog ve Fihrist Keşfi (`Chrome DevTools MCP`):** Kullanıcının `chrome://inspect/#remote-debugging` ile açık tuttuğu ve e-Devlet'le bizzat giriş yaptığı `katalog.devletarsivleri.gov.tr` sekmesine bağlanır; [scripts/dab_helpers.js](./scripts/dab_helpers.js) ile sıralı (`≥1800 ms`) arama ve fihrist (`Mi=1..5`) taraması yaparak doğru defteri ve tam poz (`Mi`) aralığını çıkarır. *(Büyük sayfalarda `take_screenshot` zaman aşımına uğrayabileceğinden `<canvas>` `toDataURL` tercih edilir.)*
- **Mod B — İndirilmiş Filigransız `.zip / .jpg` Defterlerden Kırpıntılı Okuma:** Kullanıcının indirdiği yüksek çözünürlüklü defter sayfalarını `python3 scripts/crop_and_verify.py` ile envanterler, `split --bands` ile sağ/sol varak ve şeritlere böler, `preview` ile koordinat doğrular, koordinat CSV'sinden `proofread` ile yan yana HTML doğrulama sayfası üretir.

---

## 4 Adımlı Araştırma Akışı

### Adım 1: "Kütük Duvarı" Analizi ve 4 Altın İpucu
e-Devlet PDF'inden (ve varsa GEDCOM'dan) **Baba** ve **Anne** tarafı için ayrı ayrı çıkar:
1. **Köyün Eski Adı ve Harf Varyantları:** Cumhuriyet öncesi ad + Osmanlıca ses/harf varyantları (`k/g/ğ`, `t/d`, `b/p`, `c/ç`, ünlü düşmesi).
2. **1934 Öncesi Sülale Lakapları:** `...oğlu`, `...zâde`, `...uşağı`, meslek unvanları; kadın atalarda soyadının eş hanesinden gelebileceği ve kütük/üvey farkı kontrolü.
3. **En Eski Atalar ve Takvim Çevrimi:** İlk esas kütükten (1881–1905) önce ölen dedeler yalnızca çocuğunun "Baba Adı" sütununda kalır. Milâdî → Hicrî/Rûmî dönüşümüyle 1831–1846 defterlerindeki beklenen yaşı hesapla.
4. **Osmanlı İdari Zinciri ve Homonim Tuzağı:** `Eyâlet → Sancak → Kazâ → Nâhiye / Dîvân` geçmişini ve komşu kazaları belirle. Aynı kazada/sancakta eş-adlı iki köy (`Muradlar I vs II`, farklı divanlardaki aynı adlı köyler) ihtimalini her zaman açık tut.
   - *Aile Balkanlar, Adalar, Girit, Kırım veya Kafkasya göçmeni/mübadili ise* doğrudan [gocmen-ve-mubadil-rehberi.md](./references/gocmen-ve-mubadil-rehberi.md) akışını uygula (`İsim Denklik Belgesi`, `BCA 130-16-13-2`, `DH.SN..THR.`, 1830–1875 Rumeli `NFS.d`).

### Adım 2: 500 Yıllık Arşiv Merdiveni ve "Önce Fihrist" Taktiği
1. **1881–1905:** Sicill-i Nüfus Atîk/Esas Kütükleri (e-Devlet + İlçe Nüfus Cilt-Hane-Birey kayıt örneği)
2. **1830–1880 (`BOA, NFS.d`):** Esas Nüfus ve 6 aylık/yıllık **Yoklama (Vukuat)** defterleri *(yoklamadaki kırmızı `Hâne/Numro` rakamları doğrudan bir önceki esas nüfus defterine köprüdür!)*
3. **1835–1846 (`BOA, A.{RSK.d` & `ML.VRD.TMT.d`):** 1835–38 İmam-Muhtar defterleri + 1844–46 Temettuat gelir/emlak defterleri
4. **1450–1924 (`BOA, MŞH.ŞSC.d` / `kadisicilleri.org` & `EV.d`):** Kadı sicilleri (**tereke** kayıtları kadın ataları — `bint` — bulmanın ana yoludur) ve vakıf defterleri
5. **1600–1750 (`BOA, MAD.d` & `A.{DVNSMHM.d`):** 1642 Avârız vergi haneleri, aşiret/mukataa ve Mühimme fermanları
6. **1450–1600 (`BOA, TT.d` & `TK.GM.d`):** Klasik mufassal Tapu Tahrir defterleri *(+ 1877–1922 askerî kayıtlar için MSB Şehit Bilgi Kapısı)*

- Katalogda önce **icmal defterlerini ele**, ardından **fihrist (`Mi=1..5`)** ve **`Poz (Mi) ≠ Varak (vr.)`** ofsetini bizzat doğrulayarak yalnız hedef köylerin poz aralığını listele.

### Adım 3: Kırpıntılı Okuma, Kuşak Matematiği ve Doğrulama
1. **İlk Bakış & Başlık Teyidi:** Yeni indirilen pozlarda `python3 scripts/crop_and_verify.py split --image <img.jpg> --output <out> --bands` ile sağ (`R` = ön/a) ve sol (`L` = arka/b) sayfaları şeritlere ayır. Her sayfa başlığındaki `Karye-i ... tâbi-i ...` ve komşu köy sırasını kontrol ederek eş-adlı köy karışmasını önle.
2. **Kesin Piksel & Rakam Kontrolü:** Şüpheli harf noktaları ve özellikle el yazısı **Doğu Arapça yaş rakamları (`٢/٣/٤/٥/٦`)** için `crop --zoom 2.5 --nearest` kesiti al *(küçük/karar modellerine el yazısı rakamda güvenme — bkz. [fon-kodlari-ve-paleografya-rehberi.md](./references/fon-kodlari-ve-paleografya-rehberi.md) §4)*.
3. **Kalıcı Kırpıntı CSV + HTML Proofread:** Tam okunan her kayıt için `kayit`, içinde `[?]` olan her kelime / yaş rakamı / tarih-vukuat şerhi / baba-lakap dayanağı için `kelime` satırını koordinat CSV'sine işle (`preview` ile kırmızı kutu testi → `proofread` ile yan yana HTML doğrulama sayfası üret ve commit/teslim öncesi görselleri okumayla yan yana kontrol et). Ortamda `LIQUID_API_KEY` tanımlıysa `python3 scripts/verify_d1.py` ile artımlı triyaj (`crops --only-new`) ve hane-bağlamlı çapraz eşleştirme (`match`) çalıştırıp `--scores-json` ile `🔴 Öncelikli / ⚠️ Hane Uyuşmazı` rozetlerini HTML'ye işle (bkz. [veri-mimarisi-ve-dogrulama.md](./references/veri-mimarisi-ve-dogrulama.md) §5).
4. **Kuşak Matematiği & Çapraz Doğrulama:**
   - **`+ΔYıl` Yaş Tutarlılığı:** İki sayım arası yıl farkı aynı hanedeki tüm fertlere tutarlı (`±2–3` yıl taşra yuvarlamasıyla) yansımalıdır.
   - **Yoklama `Hâne/Numro` Köprüsü:** Yoklama defterindeki hane/sıra numarasını bir önceki esas defterde doğrula; hedef bölüm okunmamışsa atıf uydurma, `"hedef okunmadı"` yaz.
   - **Yan Soy & Komşu Köy Havzası (`≤ 5 km`):** Aynı hanedeki kardeş/amca/torunları, ölen çocuğun adının yeni doğana verilmesi vakalarını ve komşu köyler arası evlilik/damatlık (`güveyi`) akışını izle.

### Adım 4: Çıktı ve Sunum Düzeni
- **Çok oturumlu proje deposunda:** [veri-mimarisi-ve-dogrulama.md](./references/veri-mimarisi-ve-dogrulama.md) dizin yapısına (`archive/transcriptions/`, `archive/kirpintilar/`, `data/derived/proofread/`, `data/derived/kisi-dizini/`, `research/people/`, `research/leads/`, `research/log/`) yaz.
- **Kullanıcı özet raporunda şu 4 bölüm zorunludur:**
  1. **Soy Kütüğü Sentezi (Baba & Anne Ayrı):** Kuşak şeması, Osmanlıca yazılışlar, `[?]` belirsizlikleri ve her halkanın kanıt seviyesi (`A/B/C/D` veya `[SÜLALE İZİ]`).
  2. **Köyün Tarihçesi, Eski Adı ve İdari Evrimi:** İdari bağlılık zinciri, homonim ayrımları ve kaynaklı demografik/mali tablo.
  3. **Çelişkiler ve Açık İpuçları:** Kütük vs. biyolojik farklar, yaş/okuma sapmaları ve doğrulama yolu.
  4. **Arşiv Künyesi ve Nokta Atışı İndirme Tablosu:** `Arşiv | Fon Kodu | Defter No | Tarih (H/R & M) | Varak & Poz (Mi) | İçerik / Kırpıntı Durumu`.
- *(İsteğe Bağlı İleri Çıktılar):* Kullanıcı isterse **interaktif Web Soy Atlası** (harita + şecere + kırpıntı büyüteci + gizlilik maskesi) veya **Avrupa *Ortsgeschichte* tarzı HTML/PDF köy-aile monografisi** üretilir.

---

## Kırmızı Bayraklar — Dur ve Kurala Dön

| Yaygın Bahane / Hata | Gerçek ve Zorunlu Tepki |
| :--- | :--- |
| *"Vakit az, `BelgeGoster.aspx`'ten paralel 10–20 `fetch` atayım"* | **DUR.** Paralel istek `HTTP 418` WAF engeli yer. Yalnızca sıralı ve `≥ 1800 ms` bekleme kullan; önce `Mi=1..5` fihristine bak. |
| *"350 sayfalık defteri 1'den 350'ye sırayla okuyayım"* | **DUR.** Önce icmal mi kontrol et; sonra fihrist / ikili aramayla hedef köylerin poz aralığını bul ve küçük parçalarla ilerle. |
| *"Filigranlı önizlemede 45'e benziyor, kesin (`A`) yazayım"* | **DUR.** Filigranlı/kırpıntısız okuma en fazla `C` veya `D` olabilir; her belirsiz harf/rakam `45[?]/43[?]` diye işaretlenir ve filigransız 1:1 kırpıntı + `proofread` HTML ile teyit edilir. |
| *"Köy adı tuttu (`Karye-i ...`), kesin bizim köy"* | **DUR.** Sayfa başlığındaki `tâbi-i ...` divan/kaza kaydını ve komşu köy sırasını kontrol et; aynı kazada bile iki eş-adlı köy olabilir. |
| *"e-Devlet resmi belge, üvey şüphesini boş verip biyolojik yazayım"* | **DUR.** Kütük ≠ biyolojik. Biyolojik bağı esas al, kütük kaydını notla koru ve çelişkiyi `research/leads/` altında izle. |
| *"1584 `TT.d` tahririnde aynı lakap var, 12. kuşak dede bağlayayım"* | **DUR.** 250 yıllık ara kuşaklar belgelenmeden kan bağı kurulamaz; yalnızca `[SÜLALE İZİ]` olarak köy tarihine işle. |
| *"Küçük model / OCR yaşı `30` dedi, kontrol etmeye gerek yok"* | **DUR.** El yazısı Doğu Arapça `٤` (4) sıkça `٣` (3) okunur; yaş rakamını mutlaka `--nearest` 2×–3× kesitle bizzat doğrula. |
