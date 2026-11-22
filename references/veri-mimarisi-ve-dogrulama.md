# Soy Araştırması Veri Mimarisi, Kırpıntı Proofread ve Çapraz Doğrulama Rehberi

Bu kılavuz, tek seferlik sohbet okumalarının ötesine geçip **çok oturumlu, denetlenebilir, tekrar üretilebilir ve çok ajanlı** bir soy kütüğü araştırma deposu kurmak için saha deneyiminden süzülmüş mühendislik standartlarını tanımlar.

---

## 1. Standart Depo ve Veri Ayrımı Mimarisi

Ham veriyi türev çıktılardan ve yorumlardan kesin çizgiyle ayırın:

```text
proje-koku/
├── data/
│   ├── source/                 # DEĞİŞMEZ ham girdiler (e-Devlet PDF, dışa aktarılan GEDCOM)
│   └── derived/                # Betiklerle üretilen çıktılar (birleşik GEDCOM, kişi dizini CSV, proofread HTML, GeoJSON)
├── archive/
│   ├── documents/              # İndirilen orijinal belgeler (YYYY-MM-DD_kurum_kisa-aciklama/)
│   ├── transcriptions/         # Belge transkripsiyonları (aynı ad kökü ile .md)
│   ├── kirpintilar/            # Kalıcı koordinat CSV'leri (<belge>.csv) ve üretilen kırpıntı görselleri (img/<belge>/)
│   └── requests/               # Arşiv başvuruları, e-Satış sipariş/tutar kayıtları (kimlik/kart bilgisi ASLA yok)
├── research/
│   ├── people/                 # Kişi başına kanıt dosyaları (<ad-soyad-dogumyili>.md)
│   ├── leads/                  # Çelişkiler, okuma tutarsızlıkları, açık ipuçları ve defter öncelik haritası
│   └── log/                    # Tarihli araştırma günlüğü (YYYY-MM-DD.md)
└── scripts/                    # Tekrar üretilebilir ayrıştırma, kırpma, dizinleme ve coğrafi analiz betikleri
```

### Temel Veri Bütünlüğü Kuralları
1. **Ham veri salt-okunurdur:** `data/source/` dosyaları asla değiştirilmez; yeni birleşik GEDCOM sürümleri tarih ekli yeni dosya olarak `data/derived/` altına yazılır.
2. **Kütük ≠ biyolojik bağ:** e-Devlet *Alt-Üst Soy Bilgisi* resmi nüfus kütüğünü izler; üvey veya evlatlık bağları kütükte "anne/baba" görünebilir. Ağaçta biyolojik bağ esas alınır, kütük bağı açık notla belirtilir ve vaka `research/leads/` altında izlenir.
3. **Aynı isimli eşleri/kişileri birleştirme:** Özellikle aynı ön ada sahip iki eş (ör. iki ayrı `Ayşe` veya `Fatma`) ya da ölen çocuğun adının sonraki kardeşe verilmesi vakalarında ayrı kayıt tutulur.
4. **Çelişkiyi gizleme:** Nüfus PDF'i ile aile ağacı (GEDCOM) veya iki defter çelişirse birincil belge esas alınır, eski değer not alanında ve `research/leads/` çelişki günlüğünde korunur.

---

## 2. Kalıcı Kırpıntı CSV'si ve Yan Yana HTML Proofread Sistemi

Tek seferlik ekran görüntüsü veya sohbet içi kesit zamanla kaybolur ve sonradan denetlenemez. Her tam okunan kayıt için **kalıcı piksel koordinatı** kaydedilir:

### Koordinat CSV Şeması (`archive/kirpintilar/<belge>.csv`)

| Sütun | Açıklama |
| :--- | :--- |
| `kayit_id` | Kişi dizinindeki benzersiz kimlik (örn. `nfs582-ornek_koy-s7` veya `tmt4874-ornek_koy-h12`) |
| `kapsam` | `kayit` (kişinin tüm bloğu: eşkâl + ad + baba + yaş + şerh) veya `kelime` (tek kelime, rakam, şerh) |
| `etiket` | `kelime` satırları için kısa etiket: `yas`, `ad`, `baba`, `lakap`, `serh`, `baslik` |
| `okuma` | Osmanlıca + Türkçe okuma, **`[?]` işaretleriyle** (transkripsiyonla birebir aynı) |
| `goruntu`, `x`, `y`, `w`, `h` | Orijinal görüntü dosya adı ve **ham piksel koordinatları** (sol üst köşe, genişlik, yükseklik) |
| `okuyan`, `tarih`, `not` | Okuyan ajan/kişi, tarih (`YYYY-MM-DD`), düzeltme notu |

### Zorunlu Kırpıntı Kuralları
1. Tam okunan **her kayıt** için bir `kayit` satırı eklenir.
2. İçinde **`[?]` bulunan her kelime**, **her yaş rakamı**, **her tarih/vukuat şerhi** ve **kişi bağına dayanak olan her baba adı/lakap** için ayrıca bir `kelime` satırı eklenir.
3. Kutu yazıyı kesmemelidir; kenarlarda **20–40 px** pay bırakılır. CSV'ye yazmadan önce `python3 scripts/crop_and_verify.py preview --image <goruntu> <x> <y> <w> <h>` ile kırmızı çerçeveli önizleme kontrol edilir.
4. Okuma sonunda `python3 scripts/crop_and_verify.py proofread --csv ... --images-dir ... --crops-dir ... --html-out ...` çalıştırılarak yan yana HTML doğrulama sayfası üretilir ve görseller okumayla yan yana son kez kontrol edilir.
5. **Düzeltme izi:** Hatalı okuma saptandığında eski satır/metin silinmez; transkripsiyonda `~~eski~~ **yeni**`, CSV `not` sütununda `"eski okuma X düzeltildi"` biçiminde iz bırakılır.
6. **Kanıt eşiği:** Koordinatlı kırpıntısı bulunmayan hiçbir okuma **`B` veya `A`** düzeyinde bağa dayanak yapılamaz.

---

## 3. Transkripsiyon Tablosu ve Yapısal Kişi Dizini

Transkripsiyon Markdown dosyaları hem insan hem de otomatik dizinleme betiği tarafından okunabilir olmalıdır:

- **Nüfus tablosu sütunları:** `Sıra | Hâne | Kayıt | Sinn | ~Doğum | Sayfa | Vukuat/Şerh | Eşleşme`
- **Ad + baba vurgusu:** Ad ve baba adı kalın yazılır (`**İsmail ibn Ali**`).
- **Bölüm başlığı:** `Karye-i **Köy Adı**` veya `Der-Köy Adı`; aynı sancak/kazada eş-adlı köyler varsa numaralandırılır (`Muradlar (I)` / `Muradlar (II)`).
- **Defterler arası atıf kuralı:** Başka deftere atıf yazarken (`663 Hâne 5 (Sıra 14)`) hedef kayıt **hedef transkripsiyondan bizzat doğrulanır**; hedef bölüm okunmamışsa atıf uydurulmaz, `"hedef okunmadı"` yazılır.

### Önerilen Türev Kişi Dizini Tabloları (`data/derived/kisi-dizini/`)
- `kayitlar.csv` *(otomatik)*: Her nefer / hane reisi için tek satır (`kayit_id`, `belge`, `yil_m`, `yerlesim_id`, `sira`, `hane`, `akrabalik`, `unvan`, `lakap`, `ad`, `baba_adi`, `baba_kaynagi`, `yas`, `tahmini_dogum`, `serh_vukuat`, `belirsiz`, `kaynak_dosya`, `kaynak_satir`).
  - `baba_kaynagi` ayrımı kritik önem taşır: `kayit` (defterde açık yazılı) ile `cikarim_hane` / `cikarim_kardes` (aynı haneden çıkarım — **tahmin**) asla karıştırılmaz.
- `kayit_baglantilari.csv` *(otomatik)*: Transkripsiyonlardaki çapraz defter atıfları ve ad-uyum denetimi (`ad_uyumlu`, `ad_uyusmuyor`, `olumsuz_atif`, `hedef_bulunamadi`).
- `tutarlilik_raporu.md` *(otomatik)*: Sıra-düzeyi ad çelişkileri, sayımlar arası yaş sapmaları (`+ΔYıl` dışı kaymalar) ve küme içi baba adı tutarsızlıkları.
- `belgeler.csv`, `okuma_kapsami.csv`, `aday_baglar.csv`, `karye_esadlari.csv` *(elle tutulan kontrol tabloları)*.

### Eşdeğer İsim Normalizasyon Sözlüğü (Arama ve Otomatik Eşleştirme İçin)
Osmanlıca yazım ve taşra telaffuzu nedeniyle şu ad çiftleri arama anahtarında eşdeğer değerlendirilmelidir (orijinal metin korunur):
- `Mehmed ↔ Mehmet`, `Ahmed ↔ Ahmet`, `Mahmud ↔ Mahmut`, `Murad ↔ Murat`, `Halid ↔ Halit`, `Hâmid ↔ Hamit`, `Vahid ↔ Vahit`
- `Abdi ↔ Abdullah ↔ Abdurrahman` *(bağlamla)*, `Bekir ↔ Ebubekir`, `Feyzi ↔ Feyzullah`, `Veys ↔ Veysi ↔ Veyis`, `Eyyûb ↔ Eyüp`, `İsmâil ↔ İsmail`, `Süleymân ↔ Süleyman`, `Ömer ↔ Umar`
- **Dikkat:** `Hasan` ile `Hüseyin` Osmanlıca el yazısında (`حسن / حسين`) yalnızca tek bir `ي` (diş/iki nokta) ile ayrıldığı için kâtip veya okuma hatası sık olur; eşleştirmede aday olarak bayraklanır ama doğrudan aynı kişi ilan edilmez.

---

## 4. Coğrafi Yakınlık ve Homonim (Eş-Adlı) Köy Ayrımı

Aynı kazada, hatta komşu iki divanda **birebir aynı adı taşıyan iki farklı köy** bulunabilir (ör. aynı kazada iki farklı `Muradlar`, iki farklı `Hatibler` veya komşu kazalarda iki ayrı `Köseler` / `Ömerli`).

1. **Sadece köy adına bakma:** Her zaman sayfa başlığındaki `tâbi-i ...` (bağlı olduğu divan/nahiye/kaza) ibaresini ve **önceki/sonraki komşu köy sırasını** kontrol et.
2. **Defter bazlı eş-ad tablosu (`karye_esadlari.csv`):** `belge + karye_ham → yerlesim_id` eşlemesi kur; aynı köy adı farklı defterlerde farklı coğrafi yerleşime gidebilir.
3. **Doğrulanmış koordinat ve 5 km havzası:** Yerleşimlerin güncel karşılıkları için OpenStreetMap (`WGS84`) doğrulanmış koordinatlar ve Haversine kuş uçuşu mesafe matrisi tut. Evlilik, damatlık (`güveyi`) ve hane göçü taramalarında **≤ 5 km** komşu köyleri öncelikli arama havuzuna al; sentetik veya tahmini koordinat uydurma.

---

## 5. İsteğe Bağlı Hibrit Yapay Zekâ Doğrulama ve Kalibrasyon İlkeleri

Büyük kırpıntı setleri (`100+` kayıt) oluştuğunda küçük/hızlı karar modelleri veya çok modlu modellerle ikinci katman kalite denetimi yapılabilir. Saha kalibrasyonundan çıkan **4 zorunlu mimari kural**:

1. **Önce A/B Kalibrasyon (Yes-Bias Testi):** Bir modeli üretime almadan önce aynı kırpıntı görseline hem doğru okumayı hem de bilinen hatalı bir okumayı sorarak modelin "her şeye evet" deyip demediğini ölç.
2. **El yazısı Doğu Arapça rakamlara (`٢/٣/٤/٥/٦`) küçük modellerde güvenme:** Hafif/karar modelleri el yazısı `٤` (4) rakamını sistematik olarak `٣` (3) veya `٢` (2) okuyabilir. Yaş rakamları her zaman **büyük VLM + `--nearest` 2×–3× piksel kesiti + insan gözüyle** teyit edilmelidir; küçük modeller yaş kırpıntısında yalnız *boş hücre tespiti* ve *netlik* için kullanılır.
3. **Tam çift sayfa yerine dar kırpıntı + hane bağlamlı JSON:**
   - Tam çift sayfa (küçültülmüş ~960 px) görüntülerde köy başlıkları ~20 px kaldığından küçük modeller başlık tespitinde başarısız olur; fihrist/başlık taraması üst şerit kırpması veya büyük VLM ile yapılmalıdır.
   - Buna karşılık **dar kayıt kırpıntılarında** (`ad_ve_metin_uyumlu`, `hane_basi_mi`, `serh_var_mi`, `okunabilirlik`) ve **metin tabanlı hane-bağlamlı JSON eşleştirmede** (kişiyi tek başına değil, tüm hane üyeleri + eşkâl + şerhleriyle birlikte vererek `ayni_kisi` / `ayni_aile_farkli_kisi` / `farkli_aile` ayırmada) çok yüksek isabet sağlanır.
4. **Üç kovalı triyaj + hane-sınırı denetimi:** Çıktıları `🔴 Öncelikli (<0.50)`, `🟡 Gri Bölge (0.50–0.80)` ve `🟢 Uyumlu (≥0.80)` olarak sınıfla; `hane_basi_mi` skoru ile dizindeki `akrabalik` sütunu çelişirse **`⚠️ Hane Uyuşmazı`** bayrağı kaldırıp HTML proofread sayfasında öne çıkar (gerçek ayrıştırıcı ve hane-kayması hatalarını anında yakalar).

### Hazır Komutlar (`scripts/verify_d1.py` — Sıfır Ek Bağımlılık, İsteğe Bağlı)

API anahtarı yalnızca ortam değişkeninden okunur (`export LIQUID_API_KEY="liquid_..."`); her komut önce `--dry-run` ile kesin token ve maliyet tahmini (`d1.2-ultra`: `\$0.042 / 1M` girdi tokenı, çıktı ücretsiz) gösterir:

```bash
# 1) Üretime geçmeden önce kendi defterinden 1 kırpıntıyla A/B yes-bias kalibrasyonu
python3 scripts/verify_d1.py calibrate \
  --image archive/kirpintilar/img/582/nfs582-ornek-s1.jpg \
  --true-reading "ابراهیم بن محمد (İbrahim bin Mehmed)" \
  --false-reading "مصطفی بن علی (Mustafa bin Ali)"

# 2) Kırpıntıları artımlı doğrula + hane-sınırı uyuşmazlıklarını tara (önce --dry-run)
python3 scripts/verify_d1.py crops \
  --csv archive/kirpintilar/582.csv \
  --crops-dir archive/kirpintilar/img/582 \
  --index-csv data/derived/kisi-dizini/kayitlar.csv \
  --out-json data/derived/proofread/d1_582.json \
  --out-md data/derived/proofread/d1_582.md \
  --only-new --dry-run

# 3) Üretilen JSON rozetlerini doğrudan yan yana HTML proofread sayfasına işle
python3 scripts/crop_and_verify.py proofread \
  --csv archive/kirpintilar/582.csv \
  --images-dir archive/documents/boa_nfs-d-582 \
  --crops-dir archive/kirpintilar/img/582 \
  --index-csv data/derived/kisi-dizini/kayitlar.csv \
  --scores-json data/derived/proofread/d1_582.json \
  --html-out data/derived/proofread/582.html

# 4) İki defteri (ör. 1831 Nüfus ↔ 1842 Nüfus veya 1845 Temettuat) hane bağlamlı JSON ile eşleştir
python3 scripts/verify_d1.py match \
  --index-csv data/derived/kisi-dizini/kayitlar.csv \
  --doc1 "NFS.d 582" --doc2 "NFS.d 663" --village ornek_koy \
  --out-json data/derived/kisi-dizini/d1_match.json \
  --out-md data/derived/kisi-dizini/d1_match.md --dry-run
```

---

## 6. Çok Oturumlu / Çok Ajanlı Çalışma Protokolü (`[CLAIM]`)

Birden fazla oturum veya ajan aynı depo üzerinde çalışıyorsa çakışmayı ve tekrar işi önlemek için:

1. **Başlamadan önce güncelle:** En son sürümü çek (`git pull --rebase`), `research/leads/` ve son `research/log/YYYY-MM-DD.md` dosyalarındaki aktif `[CLAIM / ÜZERİNDE ÇALIŞILIYOR]` kayıtlarını kontrol et.
2. **Okumadan önce claim et:** Çalışacağın defter ve sayfa/köy aralığını `[CLAIM / ÜZERİNDE ÇALIŞILIYOR]` etiketi, oturum adı ve tarih-saat ile ilgili transkripsiyon dosyasına ve günlüğe yazıp okumaya başlamadan önce kaydet/pushla.
3. **Küçük parçalarla bitir:** 1–2 hedef köy veya 5–10 sayfalık küçük adımlarla ilerle; her adımın sonunda `kırpıntı → HTML proofread → kişi dizini → tutarlılık kontrolü` zincirini çalıştırıp claim işaretini `[TAMAMLANDI]` yap.
