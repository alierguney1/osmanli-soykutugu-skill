#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Devlet Arşivleri Soy Kütüğü Becerisi — Varak Ayırma, 1:1 Piksel Kesit ve HTML Proofread Aracı
=============================================================================================
İndirilen .zip veya .jpg/.png/.tif uzantılı Osmanlıca defter görüntüleri üzerinde:
  1) `inventory` : Klasördeki .zip arşivlerini güvenli açar, tüm görüntüleri boyutlarıyla listeler.
  2) `split`     : Çift varak taramaları Sağ (`_R`) ve Sol (`_L`) sayfalar ile yatay şeritlere böler.
  3) `crop`      : Tekil hane/satır/kelimeden 1:1 (veya `--zoom --nearest`) kanıt kesiti üretir.
  4) `preview`   : Koordinat CSV'sine yazmadan önce kırmızı çerçeveli önizleme görüntüsü üretir.
  5) `proofread` : Kalıcı koordinat CSV'sinden toplu kırpıntı + yan yana filtreli HTML doğrulama
                   sayfası üretir (isteğe bağlı kişi dizini ve karar-modeli rozetlerini yükler).

Gereksinim: Python 3.9+ ve Pillow (`pip install Pillow`)
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Hata: 'Pillow' kütüphanesi kurulu değil. Kurmak için: pip install Pillow")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}


def extract_zips_if_needed(input_dir: Path, extract_root: Path) -> list[Path]:
    """Klasördeki .zip arşivlerini zip-slip korumasıyla açar ve görüntü yollarını döndürür."""
    images: list[Path] = []
    for root, _, files in os.walk(input_dir):
        for fn in sorted(files):
            fpath = Path(root) / fn
            ext = fpath.suffix.lower()
            if ext == ".zip":
                target = extract_root / fpath.stem
                if not target.exists():
                    target.mkdir(parents=True, exist_ok=True)
                    with zipfile.ZipFile(fpath, "r") as zf:
                        for member in zf.infolist():
                            dest = (target / member.filename).resolve()
                            if not str(dest).startswith(str(target.resolve())):
                                raise ValueError(f"Güvensiz zip yolu reddedildi: {member.filename}")
                            zf.extract(member, target)
                for zroot, _, zfiles in os.walk(target):
                    for zfn in sorted(zfiles):
                        zp = Path(zroot) / zfn
                        if zp.suffix.lower() in IMAGE_EXTS:
                            images.append(zp)
            elif ext in IMAGE_EXTS:
                images.append(fpath)

    seen: set[Path] = set()
    unique_imgs: list[Path] = []
    for p in images:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            unique_imgs.append(p)
    return unique_imgs


def build_image_index(images_dir: Path) -> dict[str, Path]:
    """Verilen klasör altındaki tüm görüntüleri dosya adına göre dizinler."""
    index: dict[str, Path] = {}
    for root, _, files in os.walk(images_dir):
        for fn in sorted(files):
            p = Path(root) / fn
            if p.suffix.lower() in IMAGE_EXTS and fn not in index:
                index[fn] = p
    return index


def cmd_inventory(args: argparse.Namespace) -> None:
    in_dir = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    imgs = extract_zips_if_needed(in_dir, out_dir / "_extracted")
    print(f"Toplam Görüntü Sayısı: {len(imgs)}")
    for idx, p in enumerate(imgs, 1):
        with Image.open(p) as im:
            w, h = im.size
        print(f"[{idx:03d}] {p.name}  ({w}x{h} px)  ->  {p}")


def cmd_split(args: argparse.Namespace) -> None:
    img_path = Path(args.image)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(img_path) as im:
        im = im.convert("RGB")
        w, h = im.size
        stem = img_path.stem

        # Osmanlı defterlerinde sağ sayfa önce (a yüzü), sol sayfa sonra (b yüzü) okunur.
        halves = [
            ("R", im.crop((int(w * 0.47), 0, w, h))),
            ("L", im.crop((0, 0, int(w * 0.53), h))),
        ]
        for side, sub in halves:
            sw, sh = sub.size
            full_side = out_dir / f"{stem}_{side}_full.jpg"
            sub.save(full_side, quality=92)
            print(f"Kaydedildi: {full_side} ({sw}x{sh})")

            if args.bands:
                bands = [
                    ("1_top", (0, 0, sw, int(sh * 0.37))),
                    ("2_mid", (0, int(sh * 0.31), sw, int(sh * 0.69))),
                    ("3_bot", (0, int(sh * 0.63), sw, sh)),
                ]
                for bname, box in bands:
                    bp = out_dir / f"{stem}_{side}_{bname}.png"
                    sub.crop(box).save(bp)
                    print(f"  Şerit: {bp}")


def cmd_crop(args: argparse.Namespace) -> None:
    img_path = Path(args.image)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    vals = [float(v.strip()) for v in args.box.split(",")]
    if len(vals) != 4:
        sys.exit("Hata: --box parametresi 'x1,y1,x2,y2' formatında 4 sayı olmalıdır (0.0-1.0 oran veya piksel).")

    with Image.open(img_path) as im:
        im = im.convert("RGB")
        w, h = im.size
        if all(0.0 <= v <= 1.0 for v in vals):
            x1, y1, x2, y2 = int(vals[0] * w), int(vals[1] * h), int(vals[2] * w), int(vals[3] * h)
        else:
            x1, y1, x2, y2 = [int(v) for v in vals]

        crop = im.crop((max(0, x1), max(0, y1), min(w, x2), min(h, y2)))
        if args.zoom and args.zoom > 1:
            resample = Image.Resampling.NEAREST if args.nearest else Image.Resampling.LANCZOS
            crop = crop.resize((int(crop.width * args.zoom), int(crop.height * args.zoom)), resample)

        crop.save(out_path)
        print(f"1:1 Kanıt Kesiti Kaydedildi: {out_path} ({crop.width}x{crop.height} px, kaynak kutu=({x1},{y1},{x2},{y2}))")


def cmd_preview(args: argparse.Namespace) -> None:
    """Koordinat (x, y, w, h) değerini kırmızı çerçeve ve çevresel pay ile test eder."""
    img_path = Path(args.image)
    if not img_path.exists():
        sys.exit(f"Hata: Görüntü bulunamadı: {img_path}")

    x, y, bw, bh = args.x, args.y, args.w, args.h
    pad = args.pad

    with Image.open(img_path) as im:
        im = im.convert("RGB")
        iw, ih = im.size
        cx1 = max(0, x - pad)
        cy1 = max(0, y - pad)
        cx2 = min(iw, x + bw + pad)
        cy2 = min(ih, y + bh + pad)
        sub = im.crop((cx1, cy1, cx2, cy2))

    draw = ImageDraw.Draw(sub)
    rx1, ry1 = x - cx1, y - cy1
    draw.rectangle((rx1, ry1, rx1 + bw, ry1 + bh), outline=(220, 0, 0), width=4)

    out_path = Path(args.output) if args.output else (
        Path(tempfile.gettempdir()) / f"preview_{img_path.stem}_{x}_{y}_{bw}x{bh}.jpg"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sub.save(out_path, quality=85)
    print(f"Kırmızı çerçeveli önizleme: {out_path} (kutu x={x}, y={y}, w={bw}, h={bh})")


def load_scores(scores_paths: list[str]) -> dict[str, dict]:
    """İsteğe bağlı karar-modeli doğrulama JSON dosyalarını kırpıntı dosya adına göre birleştirir."""
    merged: dict[str, dict] = {}
    for sp in scores_paths:
        p = Path(sp)
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for row in data.get("sonuclar", data.get("results", [])):
            fname = row.get("dosya") or row.get("file")
            if fname:
                merged[fname] = row
    return merged


def format_score_cell(score_row: dict | None, index_row: dict | None) -> tuple[str, bool, str]:
    if not score_row:
        return "YOK", False, "<span class='b b-yok'>— taranmadı</span>"
    durum = score_row.get("durum", "GRI_BOLGE")
    ans = score_row.get("answers", {})
    badge_map = {
        "ONCELIKLI": ("b-onc", "🔴 Öncelikli"),
        "GRI_BOLGE": ("b-gri", "🟡 Gri Bölge"),
        "RAKAM_VLM": ("b-vlm", "🔢 Rakam (VLM)"),
        "UYUMLU": ("b-uyu", "🟢 Uyumlu"),
    }
    cls, label = badge_map.get(durum, ("b-gri", durum))
    parts: list[str] = []
    if "ad_ve_metin_uyumlu" in ans:
        parts.append(f"ad={ans['ad_ve_metin_uyumlu'].get('noul', 0):.2f}")
    if "bos_mu" in ans:
        parts.append(f"boş={ans['bos_mu'].get('noul', 0):.2f}")
    hane_err = False
    if "hane_basi_mi" in ans:
        hp = ans["hane_basi_mi"].get("noul", 0)
        parts.append(f"hane={hp:.2f}")
        if index_row:
            akr = (index_row.get("akrabalik") or "").strip()
            if (not akr and hp < 0.30) or (akr and hp > 0.80):
                hane_err = True
    if "serh_var_mi" in ans:
        parts.append(f"şerh={ans['serh_var_mi'].get('noul', 0):.2f}")
    if "okunabilirlik" in ans:
        parts.append(f"okun={ans['okunabilirlik'].get('score', 0):.2f}/2")
    warn = "<br><span class='b b-hane'>⚠️ Hane uyuşmazı</span>" if hane_err else ""
    detail = "<br><small>" + html.escape(" · ".join(parts)) + "</small>" if parts else ""
    return durum, hane_err, f"<span class='b {cls}'>{html.escape(label)}</span>{warn}{detail}"


def cmd_proofread(args: argparse.Namespace) -> None:
    """Koordinat CSV'sinden tüm kırpıntıları ve yan yana filtreli HTML doğrulama sayfasını üretir."""
    csv_path = Path(args.csv)
    if not csv_path.exists():
        sys.exit(f"Hata: Koordinat CSV dosyası bulunamadı: {csv_path}")

    images_dir = Path(args.images_dir)
    if not images_dir.exists():
        sys.exit(f"Hata: Görüntü klasörü bulunamadı: {images_dir}")

    crops_dir = Path(args.crops_dir)
    crops_dir.mkdir(parents=True, exist_ok=True)
    html_out = Path(args.html_out)
    html_out.parent.mkdir(parents=True, exist_ok=True)

    img_index = build_image_index(images_dir)
    index_map: dict[str, dict] = {}
    if args.index_csv and Path(args.index_csv).exists():
        with Path(args.index_csv).open(encoding="utf-8") as f:
            index_map = {r["kayit_id"]: r for r in csv.DictReader(f) if r.get("kayit_id")}

    scores_map = load_scores(args.scores_json or [])

    with csv_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        sys.exit(f"Uyarı: {csv_path} içinde işlenecek satır yok.")

    required_cols = {"kayit_id", "kapsam", "okuma", "goruntu", "x", "y", "w", "h"}
    missing_cols = required_cols - set(rows[0].keys())
    if missing_cols:
        sys.exit(f"Hata: CSV eksik sütunlar içeriyor: {sorted(missing_cols)}")

    rel_crops = os.path.relpath(crops_dir, html_out.parent).replace("\\", "/")
    counts = {"TUMU": len(rows), "SUPHELI": 0, "KELIME": 0, "ONCELIKLI": 0, "HANE": 0, "GRI_BOLGE": 0, "UYUMLU": 0}
    tr_html: list[str] = []
    cropped_ok = 0
    missing_imgs: list[str] = []

    for r in rows:
        kid = r["kayit_id"].strip()
        etiket = (r.get("etiket") or "").strip()
        kapsam = (r.get("kapsam") or "kayit").strip()
        okuma = (r.get("okuma") or "").strip()
        goruntu = r["goruntu"].strip()
        fname = f"{kid}__{etiket}.jpg" if etiket else f"{kid}.jpg"
        crop_path = crops_dir / fname

        src = img_index.get(goruntu)
        if src is None:
            cand = images_dir / goruntu
            src = cand if cand.exists() else None

        if src is None:
            missing_imgs.append(goruntu)
        elif args.force or not crop_path.exists():
            x, y, bw, bh = (int(float(r[k])) for k in ("x", "y", "w", "h"))
            with Image.open(src) as im:
                iw, ih = im.size
                k = im.crop((max(0, x), max(0, y), min(iw, x + bw), min(ih, y + bh))).convert("RGB")
                if args.max_width and k.width > args.max_width:
                    k = k.resize((args.max_width, max(1, round(k.height * args.max_width / k.width))), Image.Resampling.LANCZOS)
                k.save(crop_path, quality=args.quality, optimize=True)
            cropped_ok += 1
        else:
            cropped_ok += 1

        is_supheli = "[?]" in okuma or "?" in okuma
        if is_supheli:
            counts["SUPHELI"] += 1
        if kapsam == "kelime":
            counts["KELIME"] += 1

        idx_r = index_map.get(kid)
        veri_str = (
            f"{idx_r.get('akrabalik', '')} {idx_r.get('ad', '')} b. {idx_r.get('baba_adi', '')} "
            f"— yaş {idx_r.get('yas', '')} — hane {idx_r.get('hane', '')}"
            if idx_r
            else "<i>—</i>"
        )
        durum, hane_err, score_html = format_score_cell(scores_map.get(fname), idx_r)
        if durum in counts:
            counts[durum] += 1
        if hane_err:
            counts["HANE"] += 1

        tr_cls = " ".join(c for c in ("k" if kapsam == "kelime" else "", "hane-err" if hane_err else "") if c)
        img_tag = f"<img src='{rel_crops}/{html.escape(fname)}' loading='lazy'>" if crop_path.exists() else "<i>görüntü eksik</i>"
        tr_html.append(
            f"<tr class='{tr_cls}' data-kapsam='{html.escape(kapsam)}' "
            f"data-supheli='{'1' if is_supheli else '0'}' data-durum='{durum}' data-hane='{'1' if hane_err else '0'}'>"
            f"<td>{img_tag}</td>"
            f"<td><code>{html.escape(kid)}</code><br>{html.escape(kapsam)} {html.escape(etiket)}"
            f"<br><small>{html.escape(goruntu)} @ {r['x']},{r['y']},{r['w']},{r['h']}</small></td>"
            f"<td>{html.escape(okuma)}<br><small>{html.escape(r.get('not', ''))}</small></td>"
            f"<td>{veri_str}</td>"
            f"<td>{score_html}</td></tr>"
        )

    title = args.title or csv_path.stem
    doc = [
        f"<!doctype html><meta charset='utf-8'><title>Proofread — {html.escape(title)}</title>",
        "<style>body{font-family:system-ui,sans-serif;margin:16px;color:#1f2328}"
        "table{border-collapse:collapse;width:100%}td,th{border:1px solid #d0d7de;padding:6px;vertical-align:top}"
        "img{max-width:360px;height:auto;display:block}.k{background:#fff8e1}.hane-err{background:#fdecea}"
        ".bar{margin:10px 0;display:flex;gap:6px;flex-wrap:wrap}"
        ".bar button{padding:5px 10px;border:1px solid #bbb;border-radius:4px;background:#f7f7f7;cursor:pointer}"
        ".bar button.act{background:#222;color:#fff;border-color:#222}"
        ".b{display:inline-block;padding:2px 6px;border-radius:4px;font-size:12px;font-weight:600}"
        ".b-onc{background:#fadbd8;color:#922b21}.b-gri{background:#fcf3cf;color:#7d6608}"
        ".b-uyu{background:#d4efdf;color:#1e8449}.b-vlm{background:#d6eaf8;color:#1b4f72}"
        ".b-yok{background:#eee;color:#666}.b-hane{background:#c0392b;color:#fff;margin-top:4px}</style>",
        f"<h1>Proofread — {html.escape(title)}</h1>",
        "<p>Kırpıntı ile okumayı yan yana doğrulayın. Düzeltmede eski okumayı silmeden "
        "<code>~~eski~~ **yeni**</code> biçiminde işaretleyin; şüpheli her harf/rakamda <code>[?]</code> koruyun.</p>",
        "<div class='bar'>"
        f"<button class='act' onclick=\"filtre('TUMU',this)\">Tümü ({counts['TUMU']})</button>"
        f"<button onclick=\"filtre('SUPHELI',this)\">❓ Şüpheli [?] ({counts['SUPHELI']})</button>"
        f"<button onclick=\"filtre('KELIME',this)\">🔍 Kelime ({counts['KELIME']})</button>"
        f"<button onclick=\"filtre('ONCELIKLI',this)\">🔴 Öncelikli ({counts['ONCELIKLI']})</button>"
        f"<button onclick=\"filtre('HANE',this)\">⚠️ Hane Uyuşmazı ({counts['HANE']})</button>"
        f"<button onclick=\"filtre('GRI_BOLGE',this)\">🟡 Gri Bölge ({counts['GRI_BOLGE']})</button>"
        f"<button onclick=\"filtre('UYUMLU',this)\">🟢 Uyumlu ({counts['UYUMLU']})</button>"
        "</div>",
        "<table><tr><th>Kırpıntı</th><th>Kayıt & Koordinat</th><th>Okuma (CSV)</th><th>Dizin Verisi</th><th>Kalite / Doğrulama</th></tr>",
        *tr_html,
        "</table>",
        "<script>function filtre(k,b){document.querySelectorAll('.bar button').forEach(x=>x.classList.remove('act'));"
        "b.classList.add('act');document.querySelectorAll('table tr[data-durum]').forEach(tr=>{"
        "let ok=false;"
        "if(k==='TUMU')ok=true;"
        "else if(k==='SUPHELI')ok=tr.dataset.supheli==='1';"
        "else if(k==='KELIME')ok=tr.dataset.kapsam==='kelime';"
        "else if(k==='HANE')ok=tr.dataset.hane==='1';"
        "else ok=tr.dataset.durum===k;"
        "tr.style.display=ok?'':'none';});}</script>",
    ]
    html_out.write_text("\n".join(doc), encoding="utf-8")
    print(f"Proofread üretildi: {html_out} ({cropped_ok}/{len(rows)} kırpıntı, {counts['SUPHELI']} şüpheli [?])")
    if missing_imgs:
        uniq = sorted(set(missing_imgs))
        print(f"Uyarı: {len(uniq)} kaynak görüntü bulunamadı: {', '.join(uniq[:5])}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Osmanlıca arşiv defteri varak ayırma, 1:1 piksel kesit, önizleme ve HTML proofread aracı."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_inv = sub.add_parser("inventory", help="Klasördeki .zip ve görüntü dosyalarını açıp boyutlarıyla listeler.")
    p_inv.add_argument("--input", required=True, help="İndirilen arşiv dosyalarının bulunduğu klasör")
    p_inv.add_argument("--output", required=True, help="Açılan dosyaların yazılacağı klasör")
    p_inv.set_defaults(func=cmd_inventory)

    p_spl = sub.add_parser("split", help="Çift varaklı defter pozunu Sağ (R) ve Sol (L) sayfalara ve yatay şeritlere böler.")
    p_spl.add_argument("--image", required=True, help="Kaynak defter görüntüsü (.jpg/.png)")
    p_spl.add_argument("--output", required=True, help="Çıktı klasörü")
    p_spl.add_argument("--bands", action="store_true", help="Her sayfayı üst/orta/alt 3 okuma şeridine de böl")
    p_spl.set_defaults(func=cmd_split)

    p_crp = sub.add_parser("crop", help="Belirli bir hane veya satırdan 1:1 (veya büyütülmüş) kanıt kesiti alır.")
    p_crp.add_argument("--image", required=True, help="Kaynak görüntü dosyası")
    p_crp.add_argument("--box", required=True, help="'x1,y1,x2,y2' (0.0-1.0 oran veya piksel koordinatı)")
    p_crp.add_argument("--output", required=True, help="Kaydedilecek kesit dosya yolu (.png/.jpg)")
    p_crp.add_argument("--zoom", type=float, default=1.0, help="Büyütme katsayısı (örn. 2.0 veya 3.0)")
    p_crp.add_argument("--nearest", action="store_true", help="Harf noktaları için keskin piksel (NEAREST) büyütme kullan")
    p_crp.set_defaults(func=cmd_crop)

    p_prv = sub.add_parser("preview", help="Koordinat (x y w h) kutusunu kırmızı çerçeveli önizlemeyle test eder.")
    p_prv.add_argument("--image", required=True, help="Kaynak görüntü dosyası")
    p_prv.add_argument("x", type=int, help="Sol üst X (piksel)")
    p_prv.add_argument("y", type=int, help="Sol üst Y (piksel)")
    p_prv.add_argument("w", type=int, help="Genişlik (piksel)")
    p_prv.add_argument("h", type=int, help="Yükseklik (piksel)")
    p_prv.add_argument("--pad", type=int, default=150, help="Çevre payı (piksel, varsayılan 150)")
    p_prv.add_argument("--output", default="", help="Önizleme çıktı yolu (boşsa geçici dizine yazar)")
    p_prv.set_defaults(func=cmd_preview)

    p_prf = sub.add_parser("proofread", help="Kalıcı koordinat CSV'sinden toplu kırpıntı ve yan yana HTML doğrulama sayfası üretir.")
    p_prf.add_argument("--csv", required=True, help="Koordinat CSV yolu (sütunlar: kayit_id,kapsam,etiket,okuma,goruntu,x,y,w,h,...)")
    p_prf.add_argument("--images-dir", required=True, help="Orijinal defter görüntülerinin bulunduğu kök klasör")
    p_prf.add_argument("--crops-dir", required=True, help="Kırpıntı görsellerinin yazılacağı klasör")
    p_prf.add_argument("--html-out", required=True, help="Üretilecek HTML proofread sayfası yolu")
    p_prf.add_argument("--title", default="", help="HTML başlığı (varsayılan: CSV dosya adı)")
    p_prf.add_argument("--index-csv", default="", help="İsteğe bağlı kişi dizini CSV yolu (kayitlar.csv)")
    p_prf.add_argument("--scores-json", nargs="*", default=[], help="İsteğe bağlı karar-modeli doğrulama JSON dosyaları")
    p_prf.add_argument("--max-width", type=int, default=480, help="Kırpıntı üst genişlik sınırı (px, 0=sınırsız, varsayılan 480)")
    p_prf.add_argument("--quality", type=int, default=78, help="JPEG kalite puanı (varsayılan 78)")
    p_prf.add_argument("--force", action="store_true", help="Mevcut kırpıntıları da yeniden kırp")
    p_prf.set_defaults(func=cmd_proofread)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
