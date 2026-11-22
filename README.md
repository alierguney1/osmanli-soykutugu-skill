# Osmanlı Soy Kütüğü, Paleografik Doğrulama ve Köy Tarihi Becerisi (`osmanli-soykutugu-skill`)

> **e-Devlet Alt-Üst Soy Bilgisi** belgeniz 1840–1905 bandında kesiliyor mu?  
> Bu açık kaynaklı **Agent Skill** paketi, şifrenizi hiçbir yere vermeden **T.C. Cumhurbaşkanlığı Devlet Arşivleri Başkanlığı Kataloğu** ve indirdiğiniz orijinal Osmanlıca defter görüntüleri üzerinden **anne ve baba tarafı soy kütüğünüzü** ve **köyünüzün 500 yıllık tarihini** **kalıcı koordinatlı kırpıntılar, yan yana HTML doğrulama (proofread), sıkı kanıt disiplini ve isteğe bağlı kalibre Decision Model (`d1.2-ultra`) triyajıyla** 1500'lere kadar indirmenizi sağlar.
>
> **Kaynak ve İlham:** Bu çalışma, **Said Sürücü**'nün seminerinden hareketle geliştirilen açık kaynaklı [**`shnfatih-hash/devlet-arsivleri-soykutugu`**](https://github.com/shnfatih-hash/devlet-arsivleri-soykutugu) becerisini temel alır; onun geniş arşiv rehberliği ve canlı katalog (`dab_helpers.js`) altyapısını, kendi çok-turlu arşiv araştırmamızda geliştirdiğimiz **kalıcı kırpıntı CSV + HTML proofread, `A/B/C/D` kanıt disiplini, yapısal kişi dizini ve kalibre `d1.2-ultra` doğrulama pipeline'ıyla** birleştirip ileri taşır.

---

## Bu Skill Neden Farklı?

Bu paket, [**`shnfatih-hash/devlet-arsivleri-soykutugu`**](https://github.com/shnfatih-hash/devlet-arsivleri-soykutugu) projesinin geniş kapsamlı Osmanlı arşiv rehberliğini **30 turluk gerçek bir arşiv araştırmasında sahada doğrulanmış veri mühendisliği pipeline'ıyla** birleştirir:

1. **500 Yıllık Geniş Arşiv Merdiveni & Canlı Katalog Keşfi** *(temel: **Said Sürücü** semineri & [**`shnfatih-hash/devlet-arsivleri-soykutugu`**](https://github.com/shnfatih-hash/devlet-arsivleri-soykutugu))*: `1450–1925` arası tam fon haritası (`NFS.d`, `ML.VRD.TMT.d`, `A.{RSK.d`, `MŞH.ŞSC.d`, `MAD.d`, `TT.d`, `EV.d`, `BCA`, `MSB`), Göçmen/Mübadil rehberi ve Chrome DevTools MCP için WAF-korumalı (`≥ 1800 ms`, `HTTP 418`) canlı katalog/fihrist aracı ([scripts/dab_helpers.js](./scripts/dab_helpers.js)).
2. **Sıfır-Uydurma Kanıt Disiplini (`A / B / C / D` + `[SÜLALE İZİ]`):** Orijinal görüntüde koordinatlı kırpıntısı bulunmayan hiçbir okuma `B` ve üstüne dayanak yapılamaz; emin olunmayan her harf/rakam `[?]` ile, her düzeltme `~~eski~~ **yeni**` iziyle kaydedilir; 16.–17. yy. tahrir kayıtları kan bağı değil `[SÜLALE İZİ]` sayılır.
3. **Kalıcı Koordinat CSV + Kırmızı Kutu Önizleme (`preview`) + Filtreli Yan Yana HTML Proofread ([scripts/crop_and_verify.py](./scripts/crop_and_verify.py)):** Tek seferlik kesitler yerine her kaydın ve şüpheli kelimenin kalıcı piksel koordinatı tutulur ve tek komutla filtreli HTML doğrulama sayfası üretilir.
4. **Saha Keşifleri:** `icmal` (isimsiz) defter elemesi, yoklama defterlerindeki `Hâne/Numro` esas-defter köprüsü, `Kütük ≠ biyolojik` kuralı, homonim (eş-adlı) köy ayrımı, Doğu Arapça el yazısı rakam (`٢/٣/٤/٥/٦`) kalibrasyon tuzakları ve çok oturumlu `[CLAIM]` protokolü.
5. **İsteğe Bağlı Decision Model (`d1.2-ultra`) Kalite Triyajı & Hane Eşleştirme ([scripts/verify_d1.py](./scripts/verify_d1.py)):** Sıfır ek bağımlılıkla çalışan, `--dry-run` maliyet tahminli kalibre doğrulama hattı — **aşağıdaki gerçek saha sonuçlarıyla kanıtlanmıştır.**

---

## Gerçek Saha Kıyaslaması: Decision Model (`d1.2-ultra`) Ne Kadar Başarılı?

**1831–1861 dönemine ait 29 gerçek Osmanlı Arşivi (`BOA, NFS.d` + `ML.VRD.TMT.d`) defteri** üzerinde yapılan tam üretim doğrulamasının özeti (ayrıntılı tablolar, A/B kalibrasyon ve olumsuz bulgular: **[benchmarks/d1-ultra-saha-sonuclari.md](./benchmarks/d1-ultra-saha-sonuclari.md)**):

| Alan | Kapsam | Sonuç / Yakalanan Gerçek Bulgu | Maliyet (`d1.2-ultra`) |
| :--- | :--- | :--- | :---: |
| **A/B *Yes-Bias* Kalibrasyonu** | 4 kırpıntı (`NFS.d 582`) | Osmanlıca ad ayrımı **`0.83` vs `0.03`** (sıfır *yes-bias*); el yazısı `٤↔٣` rakam zaafı erkenden yakalandı | `$0.00004` |
| **Görsel Kırpıntı Doğrulama** | **29 defter · 826 benzersiz kırpıntı** | Paleografik okuma hataları (`Şayeste → Âişe bint Osman`, `tâbi-i Koçoğlu → Kocaali`) ve **8 kesik/kaymış kırpıntı kutusu** yakalandı | **`$0.01614`** |
| **Hane-Sınırı Denetimi** | `NFS.d 582 + 663` (**314 tam kayıt**) | **`311/314` (`%99,0`)** mutabakat; ayrışan 3 kayıtta 2 yaşındaki çocuğu hane reisi gösteren **gerçek parser hatası** (`hane_basi_mi = 0.08`) yakalandı | `$0.00724` *(yukarıya dahil)* |
| **Köy İçi `1831 ↔ 1842` Keşfi** | Ömerli (**25 aday çift**) | **`11/11` doğru `ayni_kisi` (`0.46–0.98`)**, **`14/14` doğru `farkli_aile` (`0.01–0.08`)** — **0 yanlış pozitif!** | `$0.00075` |
| **Uyuşmaz Atıf Denetimi** | **93 `ad_uyusmuyor` çifti** | Yazım/unvan farkı altında gizlenen gerçek eşleşmeler (`Fazlı ↔ Feyz[i]: 0.98`, `Eyyûb ↔ Eyüp: 0.93`, `Ömer ↔ Kethüda: 0.89`) ve yanlış hane bağları (`0.07`) ayrıldı | `$0.00295` |
| **Kâtip Çelişkisi & Yeniden İsim Verme** | Çavuşlu (**26 çift**) | `1838`'de kırmızı `fevt` şerhli çocuğun `1842`'de hayatta yazıldığı **gerçek Osmanlı kâtip çelişkisi** yakalandı; ölen kardeşin adını alan yeni doğanlar (`0.92–0.95`) doğru ayrıldı | `$0.00082` |
| **Temettuat ↔ Nüfus & `≤ 5 km` Göç** | **170** Temettuat + **22** komşu çift | Tekil `ad+baba` eşleşmeleri `0.91–0.97`; `21/22` komşu adaş gürültüsü `0.01–0.06` ile elendi | `$0.00603` |
| **GENEL TOPLAM** | **1.196 değerlendirme · 666.635 token** | **Yüzlerce kırpıntı ve çapraz defter eşleştirmesi tek kahve fiyatının binde birine!** | **`$0.028` (2,8 sent)** |

> **Önemli Mimari Ders (Olumsuz Bulgular Dahil):** Kalibrasyon testlerimiz `d1.2-ultra`'nın **dar kırpıntılarda (`ad/metin`, `hane_basi_mi`, `serh_var_mi`) ve hane-bağlamlı JSON eşleştirmede çok keskin**, buna karşın **el yazısı Doğu Arapça yaş rakamlarında (`٤↔٣`) ve 960 px tam çift-sayfa başlık taramasında zayıf** olduğunu kanıtladı. Bu yüzden `scripts/verify_d1.py` yaş kırpıntılarında rakam okutmaz; rakamlar her zaman `crop --zoom 2.5 --nearest` + büyük VLM / insan gözüyle doğrulanır.

---

## 500 Yıllık Geriye Gidiş Merdiveni (2026 → 1500)

```text
  2026  ●  e-Devlet Alt-Üst Soy Bilgisi PDF'i (ve varsa GEDCOM) — Ham başlangıç katmanı
        │
  1905  ◉  Kütük Duvarı — Sicill-i Nüfus Atîk/Esas Kütükleri (1881–1905) + İlçe Nüfus kayıt örneği
        │
  1846  ●  Temettuat (ML.VRD.TMT.d) & İmam-Muhtar (A.{RSK.d, 1835–38) — Meslek, tarla, hayvan, muhtarlar
        │
  1831  ●  Nüfus & Yoklama Defterleri (NFS.d) — Eşkâlli erkek sayımları + Hâne/Numro köprülü vukuatlar
        │
  1750  ●  Kadı (Şer'iyye) Sicilleri (MŞH.ŞSC.d) & Evkaf (EV.d) — Tereke (eş ve kız çocukları / bint!)
        │
  1642  ●  Avârız ve Mukataa Defterleri (MAD.d) & Mühimme — Vergi haneleri, aşiret/cemaat iskânları
        │
  1500  ●  Tapu Tahrir Defterleri (TT.d / TK.GM.d) — Köyün ilk Osmanlı kaydı ([SÜLALE İZİ] katmanı)
```

---

## Kurulum

### 1. Skill Paketini Tek Komutla Kurma

**Proje Bazlı (Google Antigravity / Codex / Agent Skills standardı — Önerilen):**
```bash
git clone https://github.com/alierguney1/osmanli-soykutugu-skill.git .agents/skills/devlet-arsivleri-soykutugu
```

**Genel (Tüm Projeler — Google Antigravity):**
```bash
git clone https://github.com/alierguney1/osmanli-soykutugu-skill.git ~/.gemini/config/skills/devlet-arsivleri-soykutugu
```

**Claude Code:**
```bash
git clone https://github.com/alierguney1/osmanli-soykutugu-skill.git ~/.claude/skills/devlet-arsivleri-soykutugu
```

### 2. Görüntü Aracı Gereksinimi
```bash
pip install Pillow
```

### 3. Canlı Katalog Keşfi İçin Chrome DevTools MCP (İsteğe Bağlı)
1. MCP yapılandırmanıza `chrome-devtools-mcp` ekleyin:
   ```json
   {
     "mcpServers": {
       "chrome-devtools": {
         "command": "npx",
         "args": ["-y", "chrome-devtools-mcp@latest", "--autoConnect"]
       }
     }
   }
   ```
2. Chrome'da `chrome://inspect/#remote-debugging` → **Enable remote debugging** kutusunu işaretleyin.
3. Yeni sekmede `https://katalog.devletarsivleri.gov.tr` adresine **bizzat kendi e-Devlet oturumunuzla** giriş yapın.

---

## Araçların Hızlı Kullanımı

### A. Varak Bölme, 1:1 Piksel Kesit ve HTML Proofread (`scripts/crop_and_verify.py`)
```bash
# 1) İndirilen .zip / .jpg arşivini aç ve boyut envanterini çıkar
python3 scripts/crop_and_verify.py inventory --input ./indirilenler --output ./calisma

# 2) Çift varak defter pozunu Sağ (R) ve Sol (L) sayfalara + 3 yatay şeride böl
python3 scripts/crop_and_verify.py split --image ./defter/NFS_00012.jpg --output ./seritler --bands

# 3) Şüpheli harf/rakam için 1:1 veya keskin piksel (--nearest) büyütülmüş tekil kesit al
python3 scripts/crop_and_verify.py crop --image ./defter/NFS_00012.jpg --box 1200,850,1520,1040 --zoom 2.5 --nearest --output ./kesit.png

# 4) Koordinat CSV'sine eklemeden önce kırmızı çerçeveli önizlemeyle (x y w h) kutusunu test et
python3 scripts/crop_and_verify.py preview --image ./defter/NFS_00012.jpg 1200 850 320 190

# 5) Kalıcı koordinat CSV'sinden tüm kırpıntıları ve filtreli yan yana HTML proofread sayfasını üret
python3 scripts/crop_and_verify.py proofread \
  --csv archive/kirpintilar/582.csv \
  --images-dir archive/documents/boa_nfs-d-582 \
  --crops-dir archive/kirpintilar/img/582 \
  --html-out data/derived/proofread/582.html
```

### B. İsteğe Bağlı Decision Model (`d1.2-ultra`) Kalite Triyajı (`scripts/verify_d1.py`)
API anahtarınız yoksa yukarıdaki akışın tamamı hiçbir ek servis olmadan çalışır. `LIQUID_API_KEY` tanımladığınızda sıfır ek bağımlılıkla çalışan `verify_d1.py` devreye girer:

```bash
export LIQUID_API_KEY="liquid_..."

# 1) Kendi defterinizde A/B yes-bias kalibrasyon testi
python3 scripts/verify_d1.py calibrate \
  --image archive/kirpintilar/img/582/nfs582-ornek-s1.jpg \
  --true-reading "ابراهیم بن محمد (İbrahim bin Mehmed)" \
  --false-reading "مصطفی بن علی (Mustafa bin Ali)" --dry-run

# 2) Artımlı görsel doğrulama + ⚠️ Hane Uyuşmazı tespiti (önce --dry-run maliyet tahmini)
python3 scripts/verify_d1.py crops \
  --csv archive/kirpintilar/582.csv \
  --crops-dir archive/kirpintilar/img/582 \
  --index-csv data/derived/kisi-dizini/kayitlar.csv \
  --out-json data/derived/proofread/d1_582.json \
  --out-md data/derived/proofread/d1_582.md --only-new --dry-run

# 3) Rozetleri HTML proofread sayfasına işle
python3 scripts/crop_and_verify.py proofread \
  --csv archive/kirpintilar/582.csv \
  --images-dir archive/documents/boa_nfs-d-582 \
  --crops-dir archive/kirpintilar/img/582 \
  --index-csv data/derived/kisi-dizini/kayitlar.csv \
  --scores-json data/derived/proofread/d1_582.json \
  --html-out data/derived/proofread/582.html

# 4) Hane bağlamlı çapraz defter eşleştirme (Nüfus ↔ Nüfus veya Nüfus ↔ Temettuat)
python3 scripts/verify_d1.py match \
  --index-csv data/derived/kisi-dizini/kayitlar.csv \
  --doc1 "NFS.d 582" --doc2 "NFS.d 663" --village ornek_koy \
  --out-json data/derived/kisi-dizini/d1_match.json \
  --out-md data/derived/kisi-dizini/d1_match.md --dry-run
```

---

## Resmi Arşiv ve Nüfus Portalları

| Kurum / Hizmet | Adres | Amaç |
| :--- | :--- | :--- |
| **e-Devlet — Alt-Üst Soy Bilgisi** | https://www.turkiye.gov.tr/nvi-alt-ust-soy-bilgisi-sorgulama | Başlangıç soy ağacı PDF belgesi (`Cilt-Hane-Birey`). |
| **e-Devlet — İsim Denklik Belgesi** | https://www.turkiye.gov.tr/nvi-isim-denklik-belgesi-talep-ve-sorgulama | Balkanlar, Adalar ve Kafkasya göçmen/mübadil kayıtları. |
| **Devlet Arşivleri Kataloğu (DAB)** | https://katalog.devletarsivleri.gov.tr | e-Devlet ile ücretsiz Osmanlı (`BOA`) ve Cumhuriyet (`BCA`) katalog araması. |
| **İSAM — Kadı Sicilleri Arşivi** | https://kadisicilleri.org | Şer'iyye sicilleri katalogları ve yayımlanmış mahkeme/tereke defterleri. |
| **MSB — Şehit Bilgi Kapısı** | https://www.msb.gov.tr/SehitBilgiKapisi | 1877–1922 savaşları asker ve şehit künyeleri. |
| **TTK — Tarih Çevirme Kılavuzu** | https://www.ttk.gov.tr/tarih-cevirme-kilavuzu/ | Hicrî, Rûmî ve Milâdî tam gün/ay/yıl dönüşümü. |
| **YÖK Tez Merkezi & TKGM/VGM** | https://tez.yok.gov.tr • https://parselsorgu.tkgm.gov.tr • https://www.vgm.gov.tr | Akademik defter transkripsiyonları (`C` ikincil kaynak), parsel ve vakıf kayıtları. |

---

## Paket Yapısı

```text
osmanli-soykutugu-skill/
├── SKILL.md                                         # Ana beceri yönergesi, altın kurallar ve kırmızı bayraklar
├── README.md                                        # Kurulum, saha kıyaslaması, komutlar ve kullanım kılavuzu
├── LICENSE                                          # MIT Açık Kaynak Lisansı
├── benchmarks/
│   └── d1-ultra-saha-sonuclari.md                   # 29 Osmanlı defteri / 826 kırpıntı / 370 çift gerçek d1.2-ultra sonuçları
├── references/
│   ├── fon-kodlari-ve-paleografya-rehberi.md        # 1450–1925 fonlar, icmal uyarısı, yoklama köprüsü, takvim, varyantlar & rakam tuzakları
│   ├── gocmen-ve-mubadil-rehberi.md                 # Balkanlar, Adalar, Girit, Kırım ve Kafkasya göçmen/mübadil kılavuzu
│   └── veri-mimarisi-ve-dogrulama.md                # Depo şeması, kırpıntı CSV/HTML proofread, kişi dizini, homonim ayrımı & kalibrasyon
├── scripts/
│   ├── dab_helpers.js                               # Chrome DevTools MCP sıralı/WAF-korumalı (≥1800ms, HTTP 418) katalog yardımcıları
│   ├── crop_and_verify.py                           # Envanter + varak/şerit bölme + 1:1/nearest kesit + kırmızı kutu önizleme + HTML proofread
│   └── verify_d1.py                                 # İsteğe bağlı Liquid AI d1.2-ultra A/B kalibrasyon, artımlı kırpıntı triyajı & hane eşleştirme
└── examples/
    └── ornek-kullanim-promptlari.md                 # 5 farklı senaryo için hazır kopyala-yapıştır istem şablonları
```

---

## Atıf, Kaynak Proje ve Lisans

- **Kaynak Proje (`devlet-arsivleri-soykutugu`):** Bu beceri, MIT lisansı altında açık kaynak olarak paylaşılan [**`shnfatih-hash/devlet-arsivleri-soykutugu`**](https://github.com/shnfatih-hash/devlet-arsivleri-soykutugu) reposu temel alınarak ve onun üzerine inşa edilerek geliştirilmiştir. `scripts/dab_helpers.js`, `references/gocmen-ve-mubadil-rehberi.md`, temel `references/fon-kodlari-ve-paleografya-rehberi.md` çerçevesi ve `scripts/crop_and_verify.py`'nin `inventory/split/crop` çekirdeği o projeden alınmış; üzerine kendi saha araştırmamızda geliştirdiğimiz **kalıcı koordinatlı kırpıntı CSV + yan yana HTML proofread (`preview/proofread`), `A/B/C/D` kanıt disiplini, harf/rakam `[?]` izleme, yoklama `Hâne/Numro` köprüleme, yapısal kişi dizini, homonim/coğrafi ayrım ve kalibre `d1.2-ultra` doğrulama hattı (`scripts/verify_d1.py` + `benchmarks/`)** eklenmiştir.
- **İlham Kaynağı:** Yapay zekâ destekli Osmanlı arşiv ve soy kütüğü araştırmalarına öncülük eden semineri için **Said Sürücü**'ye teşekkür ederiz.
- **Lisans:** [MIT Lisansı](./LICENSE) — özgürce kullanılabilir, uyarlanabilir ve paylaşılabilir.
