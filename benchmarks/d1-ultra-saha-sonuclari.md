# Gerçek Saha Kıyaslaması: Liquid AI `d1.2-ultra` Decision Modeli ile Osmanlıca Arşiv Doğrulaması

Bu belge, `scripts/verify_d1.py` ve `scripts/crop_and_verify.py` hattının **1831–1861 dönemine ait 29 gerçek Osmanlı Arşivi (`BOA, NFS.d` ve `ML.VRD.TMT.d`) defterinde** elde ettiği gerçek üretim metriklerini, yakaladığı somut hataları ve olumsuz kalibrasyon bulgularını paylaşır.

> **Gizlilik ve Telif Notu:** Aşağıdaki tüm örnekler yalnızca **1831–1861** tarihli tarihsel Osmanlı nüfus ve temettuat defterlerinden alınmış kamuya açık tarihsel kayıtlardır; yaşayan bireylere ait hiçbir veri ve ham arşiv tarama görseli paylaşılmaz.

---

## 1. Özet Üretim Metrikleri (Tek Bakışta)

| Ölçüt | Gerçekleşen Değer |
| :--- | :---: |
| **Taranan Osmanlı Defteri Sayısı** | **29 defter** (`BOA, NFS.d` + `ML.VRD.TMT.d`, 1831–1861) |
| **Doğrulanan Benzersiz Kırpıntı Sayısı** | **826 kırpıntı** (`384.357` girdi tokenı → **`$0.01614`**) |
| **Değerlendirilen Çapraz Defter Çifti** | **370 çift** (`282.278` girdi tokenı → **`$0.01186`**) |
| **Toplam Değerlendirme / Token** | **1.196 çağrı** · **`666.635` girdi tokenı** (`output_tokens = 0`) |
| **Toplam API Maliyeti (`d1.2-ultra`, `$0.042 / 1M`)** | **`$0.028` (2,8 ABD senti!)** |
| **Hane-Sınırı Mutabakatı (`NFS.d 582` + `663`)** | **`311 / 314` (`%99,0`)** — ayrışan `3/3` vakanın tamamı gerçek yapısal bulgu |
| **Ömerli `1831 ↔ 1842` Keşif İsabeti (`25` aday çift)** | **`11/11` doğru `ayni_kisi`**, **`14/14` doğru `farkli_aile`** (**0 yanlış pozitif!**) |

---

## 2. Adım 1 — Üretim Öncesi A/B Kalibrasyon Testi (Model Nerede Keskin, Nerede Zayıf?)

Yüzlerce kırpıntıyı körlemesine modele atmak yerine, önce aynı kırpıntıya hem **gerçek okuma** hem de **bilinen yanlış/eski okuma** sorularak *yes-bias* (her şeye evet deme) testi yapıldı (`4` kırpıntı, `1.005` token ≈ **`$0.00004`**):

| Kırpıntı (`BOA, NFS.d 582`, 1831) | Gerçek Değer | `noul` (Doğru vs. Yanlış) | `choice` | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| `nfs582-omerli-s1.jpg` | `ابراهیم بن محمد` (yaş `٧٦`) | Ad: **`0.83`** vs **`0.03`** | `76` (`0.43`) | **Osmanlıca ad ayrımı çok keskin** (`Δ = +0.80`, *yes-bias* yok) |
| `nfs582-karakadilar-s19__yas.jpg` | `٥٥` (55) · eski hata `35` | `55`: `0.21` · `35`: `0.16` | `belirsiz` (`0.51`) | Kırmızı çizgili/şerhli rakamda kararsız |
| `nfs582-omerli-s5__yas.jpg` | `٤٠` (40) · eski hata `60` | `40`: `0.20` · `60`: `0.31` | `30` (`0.51`) | **El yazısı `٤` rakamını `٣` sandı** |
| `nfs582-karakadilar-s28__yas.jpg` | `٤` (4) | Belirsiz: `0.31` | `3` (`0.68`) | **Yine `٤` rakamını `٣` sandı** |

### Canlı Tam-Sayfa Başlık Testi (İkinci Olumsuz Bulgu)
- `NFS.d 663` içinden 42 çift-sayfa görüntüsü (`960 px` küçültülmüş) köy başlığı tespiti için test edildi (`$0.00442`).
- Sayfa küçülünce köy başlıkları `~20 px` kaldığından tüm sayfalarda skorlar `0.05–0.34` bandında kaldı.

### Bu İki Testten Çıkan Hibrit Mimari Karar
- **Decision Model (`d1.2-ultra`) KULLAN:** Dar kayıt/kelime kırpıntıları (`ad_ve_metin_uyumlu`, `hane_basi_mi`, `serh_var_mi`, `okunabilirlik`) ve **yapısal hane-bağlamlı JSON eşleştirme**.
- **Decision Model KULLANMA:** El yazısı Doğu Arapça yaş rakamları (`٢/٣/٤/٥/٦`) ve `960 px` tam çift-sayfa başlık taraması — bunları büyük VLM + `crop --zoom 2.5 --nearest` + insan gözüyle doğrula.

---

## 3. Görsel Kırpıntı Doğrulamada Yakalanan Gerçek Hatalar

### A. Paleografik Okuma Düzeltmeleri (`🔴 Öncelikli` Kuyruğundan)
1. **Kadın adı okuma hatası (`ML.VRD.TMT.d 4867`, Hâne 20, 1846):**
   - Önceki okuma: `قائم والده سی شایسته بنت عثمان` (*kaim validesi Şayeste bint Osman*)
   - `d1.2-ultra` düşük uyum skoruyla bayrakladı → orijinal kırpıntıya dönülünce gerçek metnin **`قائم والده سی عائشه بنت عثمان` (*Âişe bint Osman*)** olduğu doğrulandı ve kutunun üst kenarı da genişletildi.
2. **İdari bağlılık başlığı düzeltmesi (`NFS.d 615` s. 19 & `NFS.d 616` s. 10, 1840–1843):**
   - Önceki okuma: `Koçoğlu Divanı tâbi-i Koçoğlu`
   - `d1.2-ultra` uyarısıyla yakın kesit tekrar incelendi → **`قوج اوغلی دیوانی تابع قوجه علی` (`tâbi-i Kocaali[?/Kocaeli?]`)** olarak düzeltildi.

### B. Kesik / Kaymış Kırpıntı Kutularının Otomatik Yakalanması
- `NFS.d 582`, `663`, `4867`, `9303` ve `9305` defterlerinde toplam **8 sıkışık/kesik kırpıntı kutusu** (`hatibler-s7__serh`, `ishakcilar-s26__serh`, `muratlar_himmetli-s2__serh`, `muratlar_himmetli-s9__baba`, `muratlar_himmetli-s6__lakap`, `tmt4867-cavuslu-h20__serh_kaimvalide`, `nfs9303-ishakcilar-s1`, `nfs9305-kasikci-s1`) `🔴 Öncelikli` (`0.27–0.49`) puanıyla yakalandı.
- Koordinatlar genişletilip yeniden kırpıldığında puanlar anında sıçradı (ör. `0.46 → 0.76` ve `0.46 → 0.63`).

### C. Hane-Sınırı Denetimi (`311/314` Mutabakat + Gerçek Ayrıştırıcı Hatası!)
`NFS.d 582` (`177` tam kayıt) ve `NFS.d 663` (`137` tam kayıt) üzerindeki **314 kırpıntıda** (`$0.00724`):
- Gerçek hane reislerine `hane_basi_mi = 0.85 – 0.99`, `oğlu / karındaşı / torunu` kayıtlarına `0.04 – 0.27` verdi.
- Dizindeki `akrabalik` sütunuyla **311/314 örtüştü**; ayrışan **3 kaydın 3'ü de gerçek vaka** çıktı:
  - **`nfs582-ishakcilar-s12` (`Mezbûr Mehmed'in oğlu Nu'mân`, yaş 2 — `hane_basi_mi = 0.08`):** Dizin ayrıştırıcı betik `"Mezbûr Mehmed'in oğlu"` ifadesini `akrabalik` yerine `lakap` sütununa attığı için 2 yaşındaki çocuk dizinde **hane reisi** görünüyordu — `d1.2-ultra` bu kod hatasını tek başına yakaladı!
  - Diğer 2 ayrışma (`güveyi` ve ayrı `ibn` baba adıyla yazılmış `diğer oğlu`) görselde gerçekten ayrı baba adı ve eşkâl taşıyan özel hane yapılarıydı (`0.86–0.94`).

---

## 4. Hane-Bağlamlı JSON Eşleştirmede Gerçek Sonuçlar

Kişiyi tek başına `"ad + yaş"` olarak değil, **aynı hanedeki tüm fertler (`hane_uyeleri`), eşkâl, lakap ve vukuat şerhiyle birlikte** tek JSON içinde sorduğumuzda elde edilen sonuçlar:

### A. Sıfır Yanlış Pozitif ile Yeni Eşleşme Keşfi — `Ömerli` (`NFS.d 582 [1831] ↔ NFS.d 663 [1842]`)
**25 eşleşmemiş aday çift · `17.917` token · maliyet `$0.00075`:**

| 1831 (`NFS.d 582`) | 1842 (`NFS.d 663`) | Karar (`iliski_turu`) | `ayni_kisi` | `ayni_aile` | Yaş Uyumu |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `Mehmed b. Ahmed` (H6, yaş 4) | `Mehmed` (H2, yaş 15) | **`ayni_kisi`** | **0.98** | 0.94 | 1.93/2 |
| `İbrahim b. Mehmed` (H1, yaş 76) | `İbrahim b. Mehmed` (H7, yaş 90) | **`ayni_kisi`** | **0.91** | 0.94 | 1.16/2 |
| `Ahmed b. Mustafa` (H4, yaş 10) | `Ahmed b. Mustafa` (H5, yaş 20) | **`ayni_kisi`** | **0.90** | 0.95 | 1.68/2 |
| `Ahmed b. Osman` (H6, yaş 40) | `Ahmed b. Osman` (H2, yaş 48) | **`ayni_kisi`** | **0.87** | 0.93 | 0.86/2 |
| `Mustafa b. Mustafa` (H2, yaş 50) | `Mustafa b. Mustafa[?]` (H8, yaş 60) | **`ayni_kisi`** | **0.87** | 0.91 | 1.67/2 |
| *(Diğer 6 gerçek eşleşme)* | *(1831 → 1842 aynı haneler)* | **`ayni_kisi`** | **0.46–0.74** | 0.76–0.95 | — |
| `Hüseyin b. İsmail` (H3, yaş 15) | `Hüseyin b. Ali` (H4, yaş 25) | **`farkli_aile`** | **0.08** | 0.20 | 0.47/2 |
| `Ahmed b. İbrahim` (H1, yaş 25) | `Ahmed b. Osman` (H2, yaş 48) | **`farkli_aile`** | **0.08** | 0.09 | 0.42/2 |
| *(Diğer 12 yanlış adaş çifti)* | *(Farklı babalar/haneler)* | **`farkli_aile`** | **0.01–0.08** | 0.05–0.33 | — |

> **Ayrım netliği:** En düşük doğru eşleşme **`0.46`**, en yüksek yanlış adaş **`0.08`** — arada **5,7 katlık temiz bir boşluk**, **0 yanlış pozitif**, **0 yanlış negatif**.

### B. Yazım ve Unvan Farkı Altında Gizlenen `ayni_kisi` Eşleşmeleri (`93` Uyuşmaz Çift · `$0.00295`)
Klasik metin karşılaştırmasının `"ad_uyusmuyor"` diye elediği 93 çiftte modelin bağlamdan yakaladığı gerçek eşleşmeler ve doğru ayrımlar:

| Kaynak Kayıt | Hedef Kayıt | Karar | `ayni_kisi` | `ayni_aile` | Açıklama |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `tmt4832` Fazlı b. Süleyman (1846) | `nfs663` Feyz[i] b. Süleyman (1842, yaş 38) | **`ayni_kisi`** | **0.98** | 0.79 | Yazım/okuma varyantı yakalandı |
| `nfs663` İbrahim b. Feyz[ullah] (1842) | `tmt4831` Kâhya[?] b. Feyzullah (1846) | **`ayni_kisi`** | **0.93** | 0.90 | Temettuat'ta yalnız unvanla yazılmış |
| `nfs663` Eyyûb b. Bekir (1842) | `tmt4831` Eyüp b. Bekir (1846) | **`ayni_kisi`** | **0.93** | 0.86 | İmla farkı temiz çözüldü |
| `nfs663` Ömer b. Ali[?/Osman?] (1842) | `tmt4867` Kethüda b. Osman (1846) | **`ayni_kisi`** | **0.89** | 0.67 | Köy kethüdası unvanıyla eşleşti |
| `nfs663` Ahad?] b. Ahmed (1842) | `tmt4874` Abdülahad b. Ahmet (1846) | **`ayni_kisi`** | **0.76** | 0.66 | Kısaltılmış ad eşleştirildi |
| `nfs9315` Osman b. Yakub (1858) | `tmt4832` Yakub b. Yakub (1846) | **`ayni_aile_farkli_kisi`** | 0.33 | **0.97** | Hane devri doğru ayrıldı (aynı kişi değil, aynı aile) |
| `nfs663-hatibler-s8` | `tmt4867-hatibler-h110` | **`farkli_aile`** | **0.07** | 0.14 | Yanlış hane atfı yakalandı |

### C. Gerçek 1838 Osmanlı Kâtip Çelişkisinin Yakalanması (`Çavuşlu`, `26` Çift · `$0.00082`)
- `NFS.d 582` Hâne 8 (`Oğlu Mustafa b. Süleyman`, yaş 8) ↔ `NFS.d 663` Hâne 19 (`Mustafa b. Süleyman`, yaş 18) çiftini **`ayni_kisi = 0.70`**, **`ayni_aile = 0.94`** olarak işaretledi.
- Orijinal `582` görüntüsü tekrar kontrol edildiğinde çocuğun üzerinde gerçekten kırmızı Z-çizgili `فوت ... ١٢٥٤` (1838 vefat) şerhi bulunduğu, buna rağmen `1842` sayımında `18` yaşında hayatta yazıldığı kanıtlandı (gerçek 19. yüzyıl kâtip/yoklama tutarsızlığı).
- Aynı köyde ölen çocuğun adının yeni doğan kardeşe verildiği iki vaka ise yanlışlıkla birleştirilmeden **`ayni_aile_farkli_kisi` (`0.92–0.95`)** olarak doğru ayrıştırıldı.

### D. Temettuat ↔ Nüfus (`170` Çift · `$0.00528`) ve Komşu Köy Göç Taraması (`≤ 5 km`, `22` Çift · `$0.00075`)
- **Temettuat ↔ Nüfus:** Sülale lakaplı Temettuat reisleri ile Nüfus kayıtları **`0.91–0.97`** bandında temiz eşleşti (ör. `tmt4874` Ömer b. İbrahim ↔ `nfs663` s4: **`0.96`**; `tmt4867` Mehmed b. Süleyman ↔ `nfs663` s44: **`0.92`**; `tmt4867` Kara Köle oğlu ↔ `nfs663` s1–s2: **`0.94–0.97`**).
- **Komşu Köy Göç Taraması (`≤ 5 km`):** 22 aday çiftten 21 gürültülü adaş çiftini **`0.01–0.06`** ile sıfır yanlış pozitif vererek eledi, yalnızca `2.7 km` mesafedeki tek anlamlı adayı (`0.40`) incelemeye çıkardı.

---

## 5. Kendi Defterlerinizde Aynı Hattı Nasıl Çalıştırırsınız?

Tüm bu akış projeden bağımsız olarak **[scripts/verify_d1.py](../scripts/verify_d1.py)** ve **[scripts/crop_and_verify.py](../scripts/crop_and_verify.py)** içinde hazır gelir:

```bash
export LIQUID_API_KEY="liquid_..."

# 1) Önce 1 kırpıntıyla kendi defterinizde A/B yes-bias kalibrasyonu (~$0.00001)
python3 scripts/verify_d1.py calibrate \
  --image archive/kirpintilar/img/582/ornek-s1.jpg \
  --true-reading "ابراهیم بن محمد (İbrahim bin Mehmed)" \
  --false-reading "مصطفی بن علی (Mustafa bin Ali)"

# 2) Kırpıntıları artımlı doğrula + ⚠️ Hane Uyuşmazı denetimi (--dry-run ile önce maliyet gör)
python3 scripts/verify_d1.py crops \
  --csv archive/kirpintilar/582.csv \
  --crops-dir archive/kirpintilar/img/582 \
  --index-csv data/derived/kisi-dizini/kayitlar.csv \
  --out-json data/derived/proofread/d1_582.json \
  --out-md data/derived/proofread/d1_582.md --only-new

# 3) Rozetleri yan yana HTML proofread sayfasına işle
python3 scripts/crop_and_verify.py proofread \
  --csv archive/kirpintilar/582.csv \
  --images-dir archive/documents/boa_nfs-d-582 \
  --crops-dir archive/kirpintilar/img/582 \
  --index-csv data/derived/kisi-dizini/kayitlar.csv \
  --scores-json data/derived/proofread/d1_582.json \
  --html-out data/derived/proofread/582.html

# 4) İki defteri hane bağlamlı JSON ile eşleştir
python3 scripts/verify_d1.py match \
  --index-csv data/derived/kisi-dizini/kayitlar.csv \
  --doc1 "NFS.d 582" --doc2 "NFS.d 663" --village omerli \
  --out-json data/derived/kisi-dizini/d1_match.json \
  --out-md data/derived/kisi-dizini/d1_match.md
```
