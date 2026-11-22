# Hazır Kullanım İstemleri (Kopyala – Yapıştır Prompt Şablonları)

Bu dosyadaki istemleri araştırma aşamanıza göre doğrudan kopyalayıp yapay zekâ ajanınıza (Google Antigravity, Claude Code, Codex, Cursor vb.) verebilirsiniz.

---

## 1. Başlangıç İstemi: e-Devlet Belgesi + Canlı Katalog Keşfi (`Chrome DevTools MCP`)

*Kullanım zamanı: e-Devlet'ten Alt-Üst Soy PDF belgenizi indirdiğinizde ve Chrome'da `katalog.devletarsivleri.gov.tr` oturumunuzu açtığınızda.*

```markdown
Sana e-Devlet'ten aldığım "Alt-Üst Soy Bilgisi" belgemi verdim. Chrome tarayıcımda `chrome://inspect/#remote-debugging` ayarını etkinleştirdim ve `https://katalog.devletarsivleri.gov.tr` adresine kendi e-Devlet şifremle giriş yaptım. (Bilinen aile lakaplarımız / notlarımız: [...varsa buraya yazın...])

Lütfen `devlet-arsivleri-soykutugu` becerisini kullanarak açık olan Devlet Arşivleri Kataloğu sekmeme bağlan ve şu adımları uygula:

1. **Kütük Duvarı ve 4 Altın İpucu:**
   - Baba ve anne tarafımdaki en eski ataları, Cilt–Hane–Birey numaralarını, doğum yıllarının Hicrî/Rûmî karşılıklarını, kütük/üvey çelişkisi ihtimallerini ve köylerimizin eski Osmanlıca adları + `Eyâlet → Sancak → Kazâ → Nâhiye/Dîvân` zincirini çıkar.

2. **Bütçe Koruyan "Önce Fihrist" Katalog Taraması (1880 → 1500):**
   - `NFS.d` (Nüfus & Yoklama), `ML.VRD.TMT.d` (Temettuat), `A.{RSK.d` (1835–38 İmam-Muhtar), `MŞH.ŞSC.d` (Şer'iyye Sicilleri / tereke), `MAD.d` (Avârız) ve `TT.d / TK.GM.d` (Tapu Tahrir) fonlarında tarama yap.
   - `icmal` (isimsiz sayısal özet) defterlerini ele. WAF (`HTTP 418`) tetiklememek için paralel istek atmadan (`≥1800 ms` sıralı) önce fihrist (`Mi=1..5`) pozlarını kontrol et; `Poz (Mi) ≠ Varak (vr.)` ofsetini hesaplayarak yalnızca hedef köylerin poz aralığını belirle.

3. **Kanıt Seviyeli Özet ve Nokta Atışı İndirme Tablosu:**
   - Önizlemeden görülebilen şüpheli harf ve rakamları `[?]` ile işaretle (filigranlı önizlemeyi en fazla `C/D` say).
   - e-Satış sepetinden yalnızca doğru sayfaları alabilmem için tam `Arşiv | Fon Kodu | Defter No | Tarih | Varak & Poz (Mi) | İçerik` tablosunu ver.
```

---

## 2. İndirilmiş `.zip / .jpg` Defterlerden Kırpıntılı ve HTML Proofread'li Tam Okuma

*Kullanım zamanı: Filigransız yüksek çözünürlüklü defter sayfalarını çalışma klasörünüze indirdiğinizde.*

```markdown
Devlet Arşivleri'nden indirdiğim filigransız yüksek çözünürlüklü `.zip / .jpg` defter sayfalarını çalışma klasörüne koydum.

Lütfen `devlet-arsivleri-soykutugu` becerisi ve `python3 scripts/crop_and_verify.py` aracını kullanarak:
1. `inventory` ile görüntü envanterini çıkar; brute-force baştan sona okumak yerine fihrist/örnekleme ile hedef köylerimizin sayfa aralığını nokta atışı tespit et.
2. Her hedef sayfanın başlığındaki `Karye-i ... tâbi-i ...` ve komşu köy sırasını teyit ederek eş-adlı (homonim) köy karışmasını önle; `split --bands` ile sağ (`R`) ve sol (`L`) varakları şeritlere böl.
3. Hedef köydeki tüm haneleri (yan kollar, amca/kardeş, doğum/vefat/askerlik şerhleri dahil) tam oku. Emin olmadığın her tekil harf, kelime ve rakamı `[?]` ile ve alternatifleriyle yaz; özellikle Doğu Arapça yaş rakamlarını (`٢/٣/٤/٥/٦`) `crop --zoom 2.5 --nearest` ile doğrula.
4. Her kayıt için `kayit`, her `[?]` kelime / yaş rakamı / vukuat şerhi / baba-lakap dayanağı için `kelime` satırını koordinat CSV'sine işle (`preview` ile kontrol et), ardından `proofread` komutuyla yan yana HTML doğrulama sayfasını üretip görsellerle okumaları son kez karşılaştır.
5. Sayımlar arası `+ΔYıl` yaş tutarlılığını ve yoklama defterlerindeki `Hâne/Numro` köprülerini denetleyerek bulguları `A / B / C / D` (16.–17. yy. için `[SÜLALE İZİ]`) kanıt seviyeleriyle raporla.
```

---

## 3. Çok Oturumlu Araştırma Deposu Kurma ve Çapraz Defter Tutarlılık Denetimi

*Kullanım zamanı: Birden fazla defteri uzun soluklu, tekrar üretilebilir bir Git deposunda yönetmek istediğinizde.*

```markdown
Bu çalışma klasörünü `devlet-arsivleri-soykutugu` becerisindeki `references/veri-mimarisi-ve-dogrulama.md` standardına göre çok oturumlu bir soy araştırma deposu olarak düzenle:
1. `data/source/` (değişmez ham PDF/GEDCOM), `data/derived/` (`proofread/`, `kisi-dizini/`), `archive/` (`documents/`, `transcriptions/`, `kirpintilar/`, `requests/`) ve `research/` (`people/`, `leads/`, `log/`) yapısını kur.
2. Okunan her defter için standart transkripsiyon tablosu, koordinat CSV'si ve HTML proofread çıktısı üret; düzeltmelerde eski okumayı `~~eski~~ **yeni**` biçiminde koru.
3. Kütük ≠ biyolojik çelişkilerini ve defterler arası yaş/isim tutarsızlıklarını `research/leads/` altında ayrı ayrı takip et; her oturum sonunda araştırma günlüğünü (`research/log/YYYY-MM-DD.md`) güncelle.
```

---

## 4. Göçmen ve Mübadil Aileler İçin Özel Tarama İstemi

*Kullanım zamanı: Ataları Balkanlar, Ege/Akdeniz Adaları, Girit, Kırım veya Kafkasya'dan göç etmiş / mübadeleyle gelmiş aileler için.*

```markdown
Atalarımız [Selanik / Drama / Girit / Bulgaristan-Tuna / Üsküp / Kafkasya vb.] bölgesinden gelerek [İl / İlçe / Köy] yerleşimine iskân edilmiş. e-Devlet Alt-Üst Soy belgemi (ve varsa İsim Denklik bilgimi) ekledim; Chrome'da `https://katalog.devletarsivleri.gov.tr` oturumum açık.

Lütfen `devlet-arsivleri-soykutugu` göçmen ve mübadil rehberini (`references/gocmen-ve-mubadil-rehberi.md`) izleyerek:
1. 1923–1925 mübadelesi ise Cumhuriyet Arşivi `130-16-13-2` (*Tasfiye Talepnameleri*) ve `272` (*Toprak İskân*) fonlarında; 93 Harbi, Balkan Harbi veya Kafkas göçü ise Osmanlı Arşivi `DH.SN..THR.`, `DH.İ.UM`, `DH.MKT.`, `Y..PRK.KOM.` ve `A.}MKT.NZD.` fonlarında sıralı (`≥1800 ms`) tarama yap.
2. Geldikleri tam kaza ve köy adını netleştirdikten sonra Osmanlı Arşivi'ndeki **1830–1875 Balkan/Adalar Nüfus (`NFS.d`) ve 1845 Temettuat (`ML.VRD.TMT.d`)** defterlerinde o köyün kaydını ara; icmal defterlerini eleyip indirmem gereken tam defter/poz (`Mi`) aralığını çıkar.
```

---

## 5. Final Sunumu: İnteraktif Web Soy Atlası veya *Ortsgeschichte* Köy-Aile Monografisi

*Kullanım zamanı: Birincil arşiv okumaları ve kırpıntı doğrulamaları olgunlaştığında kalıcı bir aile/köy eseri üretmek istediğinizde.*

```markdown
Doğrulanmış (`A/B` kanıtlı ve kırpıntılı) tüm birincil arşiv transkripsiyonlarımızı, kişi dizinimizi ve kırpıntı görsellerimizi kullanarak:
- [Seçenek A — Monografi]: Avrupa yerel ve mikro-tarihçiliği (*Ortsgeschichte*) disipliniyle baskıya hazır çok bölümlü HTML/PDF köy-aile kitabı hazırla. Her olayı tam arşiv künyesine bağla, 16.–17. yy. tahrir kayıtlarını `[SÜLALE İZİ]` olarak ayır, orijinal kırpıntı kesitlerini ilgili bölümlere tıpkıbasım levha olarak yerleştir.
- [Seçenek B — İnteraktif Atlas]: Sıfır-derlemeli (statik HTML/CSS/JS) bir Web Soy Atlası oluştur; doğrulanmış OSM koordinatlarıyla harita, etkileşimli şecere, kırpıntı büyüteci, çelişki günlüğü ve yaşayan bireyler için varsayılan gizlilik maskesi ekle.
```
