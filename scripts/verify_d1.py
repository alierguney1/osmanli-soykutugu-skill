#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Devlet Arşivleri Soy Kütüğü Becerisi — İsteğe Bağlı Decision Model (d1.2-ultra) Doğrulama Aracı
===============================================================================================
Liquid AI `d1.2-ultra` karar modeli (`https://api.liquid.ai/decisions/v1/systemone`, yalnızca
girdi tokenı ücretli, çıktı ücretsiz) ile sıfır harici bağımlılıkla (yalnızca Python stdlib):

  1) `calibrate` : Herhangi bir kırpıntıda Doğru vs. Yanlış okuma A/B (yes-bias) testi yapar.
  2) `crops`     : Koordinat CSV + kırpıntı görsellerini artımlı (`--only-new`) doğrular;
                   `🔴 Öncelikli / 🟡 Gri Bölge / 🟢 Uyumlu` + `⚠️ Hane Uyuşmazı` raporu ve
                   `crop_and_verify.py proofread --scores-json` ile uyumlu JSON üretir.
  3) `match`     : `kayitlar.csv` içindeki herhangi iki defterin kayıtlarını tüm hane bağlamıyla
                   (kardeşler, oğullar, eşkâl, şerh, lakap) yapısal JSON olarak eşleştirir.

Saha Kalibrasyon Kuralları (Yerleşik):
  - El yazısı Doğu Arapça yaş rakamları (`٢/٣/٤/٥/٦`) karar modellerinde güvenilmezdir;
    `etiket == "yas"` kırpıntılarında rakam okutulmaz, yalnızca `bos_mu` ve `okunabilirlik`
    denetlenir (rakam teyidi `crop --zoom 2.5 --nearest` + büyük VLM / insan gözüyle yapılır).
  - API anahtarı asla koda yazılmaz; ortam değişkeninden (`LIQUID_API_KEY`) okunur.
  - Her alt komut `--dry-run` ile API çağırmadan kesin token/maliyet tahmini basar.
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import math
import os
import re
import struct
import sys
import unicodedata
import urllib.error
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

API_URL = "https://api.liquid.ai/decisions/v1/systemone"
PRICE_PER_1M = {"d1.2-ultra": 0.042, "d1.2": 0.020}

EQUIV_NAMES = {
    "mehmet": "mehmed",
    "ahmet": "ahmed",
    "mahmut": "mahmud",
    "murat": "murad",
    "halit": "halid",
    "hamit": "hamid",
    "vahit": "vahid",
    "veysi": "veys",
    "veyis": "veys",
    "ebubekir": "bekir",
    "feyzi": "feyzullah",
    "eyup": "eyyub",
    "eyyup": "eyyub",
    "abdi": "abdullah",
}


def norm_name(text: str) -> str:
    s = (text or "").replace("I", "ı").replace("İ", "i").lower()
    s = re.sub(r"\[.*?\]", "", s)
    s = s.replace("ı", "i")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z]+", "", s)
    return EQUIV_NAMES.get(s, s)


def image_dimensions(path: Path) -> tuple[int, int]:
    """Harici kütüphane olmadan JPEG veya PNG genişlik/yükseklik okur."""
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", data[16:24])
        return w, h
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5 : i + 9])
            return w, h
        if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
        else:
            seg_len = struct.unpack(">H", data[i + 2 : i + 4])[0]
            i += 2 + seg_len
    return 360, 360


def estimate_image_tokens(path: Path) -> int:
    w, h = image_dimensions(path)
    return math.ceil(math.ceil(w / 32) * math.ceil(h / 32) * 1.5)


def image_data_url(path: Path) -> str:
    ext = path.suffix.lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def require_api_key() -> str:
    key = os.environ.get("LIQUID_API_KEY", "").strip()
    if not key:
        sys.exit("Hata: LIQUID_API_KEY ortam değişkeni tanımlı değil. Örnek: export LIQUID_API_KEY='liquid_...'")
    return key


def call_d1(api_key: str, model: str, state: dict | str, questions: dict, images: list[str] | None = None) -> dict:
    payload: dict = {"model": model, "state": state, "questions": questions}
    if images:
        payload["images"] = images
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {body}") from e


def crop_filename(row: dict) -> str:
    kid = row["kayit_id"].strip()
    etiket = (row.get("etiket") or "").strip()
    return f"{kid}__{etiket}.jpg" if etiket else f"{kid}.jpg"


def build_crop_questions(row: dict) -> tuple[str, dict]:
    okuma = (row.get("okuma") or "").strip()
    kapsam = (row.get("kapsam") or "kayit").strip()
    etiket = (row.get("etiket") or "").strip()

    if kapsam == "kelime" and etiket == "yas":
        state = (
            "An Ottoman Turkish population register age crop showing the area beneath 'سنه'/'سن'. "
            f"Recorded transcription: {okuma}"
        )
        return state, {
            "bos_mu": {
                "type": "noul",
                "instructions": "Is the age space beneath 'سنه'/'سن' completely blank (no numeral written)?",
            },
            "okunabilirlik": {
                "type": "score",
                "instructions": "How clearly visible and unobstructed is the age numeral?",
                "criteria": [
                    "Illegible, faded, stained, or covered by red lines",
                    "Partially unclear or ambiguous shape",
                    "Clearly visible and unobstructed",
                ],
            },
        }

    if kapsam == "kelime":
        state = (
            f"An Ottoman Turkish archival register word/note crop (type: {etiket or 'kelime'}). "
            f"Recorded transcription: {okuma}"
        )
        return state, {
            "ad_ve_metin_uyumlu": {
                "type": "noul",
                "instructions": f"Does the Ottoman Turkish Arabic-script text in this crop match '{okuma}'?",
            },
            "okunabilirlik": {
                "type": "score",
                "instructions": "How clearly legible is the Ottoman script in this crop?",
                "criteria": [
                    "Illegible, faded, or cut off at the border",
                    "Partially ambiguous or overlapping strokes",
                    "Clearly legible",
                ],
            },
        }

    state = (
        "An Ottoman Turkish population or tax register entry crop showing one individual's block "
        "(physical description/notes, name and father's name in Arabic script, age or marginal note). "
        f"Recorded transcription: {okuma}"
    )
    return state, {
        "ad_ve_metin_uyumlu": {
            "type": "noul",
            "instructions": f"Does the Ottoman Turkish name and father's name in this crop match '{okuma}'?",
        },
        "hane_basi_mi": {
            "type": "noul",
            "instructions": "Does this entry appear to be a household head (hâne başı: has 'بن' father's name and physical description, rather than starting with 'اوغلی', 'قرنداشی', 'طورونی', or 'اوكی اوغلی')?",
        },
        "serh_var_mi": {
            "type": "noul",
            "instructions": "Does this entry contain an added marginal/overlay note (e.g. death/فوت, birth/تولد, redif/ردیف, mansure/منصوره, or red strike-through)?",
        },
        "okunabilirlik": {
            "type": "score",
            "instructions": "How clearly legible is the Ottoman script in this crop?",
            "criteria": [
                "Illegible, cut off, or heavily damaged/faded",
                "Partially unclear or obscured by overlapping notes",
                "Clearly legible",
            ],
        },
    }


def classify_crop(kapsam: str, etiket: str, answers: dict) -> tuple[str, float]:
    if kapsam == "kelime" and etiket == "yas":
        bos = answers.get("bos_mu", {}).get("noul", 0.0)
        okun = answers.get("okunabilirlik", {}).get("score", 1.0)
        if bos >= 0.50:
            return "ONCELIKLI", 0.10
        return ("GRI_BOLGE", okun / 2.0) if okun < 1.2 else ("RAKAM_VLM", 0.75)

    p = answers.get("ad_ve_metin_uyumlu", {}).get("noul", 0.5)
    if p < 0.50:
        return "ONCELIKLI", p
    if p < 0.80:
        return "GRI_BOLGE", p
    return "UYUMLU", p


def cmd_calibrate(args: argparse.Namespace) -> None:
    img_path = Path(args.image)
    if not img_path.exists():
        sys.exit(f"Hata: Görüntü bulunamadı: {img_path}")

    state = "An Ottoman Turkish archival register crop showing a single name/entry in Arabic script."
    questions = {
        "dogru_okuma": {
            "type": "noul",
            "instructions": f"Does the Ottoman Turkish Arabic-script text in this crop read '{args.true_reading}'?",
        },
        "yanlis_okuma": {
            "type": "noul",
            "instructions": f"Does the Ottoman Turkish Arabic-script text in this crop read '{args.false_reading}'?",
        },
    }
    est_tok = estimate_image_tokens(img_path) + 120
    unit = PRICE_PER_1M[args.model]
    if args.dry_run:
        print(f"[DRY-RUN] calibrate ({args.model}): 1 kırpıntı, ~{est_tok:,} token (~${est_tok * unit / 1e6:.6f})")
        return

    api_key = require_api_key()
    resp = call_d1(api_key, args.model, state, questions, images=[image_data_url(img_path)])
    ans = resp.get("answers", {})
    tok = resp.get("usage", {}).get("input_tokens", 0)
    p_true = ans.get("dogru_okuma", {}).get("noul", 0.0)
    p_false = ans.get("yanlis_okuma", {}).get("noul", 0.0)
    gap = p_true - p_false
    print(f"Kalibrasyon ({img_path.name}, model={args.model}, tokens={tok}, ~${tok * unit / 1e6:.6f}):")
    print(f"  Doğru okuma  ('{args.true_reading}'): noul = {p_true:.3f}")
    print(f"  Yanlış okuma ('{args.false_reading}'): noul = {p_false:.3f}")
    print(f"  Ayırt edicilik farkı (Δ): {gap:+.3f} -> {'İYİ (yes-bias yok)' if gap >= 0.40 else 'ZAYIF (kalibrasyon kontrolü gerekir)'}")


def cmd_crops(args: argparse.Namespace) -> None:
    csv_path = Path(args.csv)
    crops_dir = Path(args.crops_dir)
    out_json = Path(args.out_json)
    if not csv_path.exists():
        sys.exit(f"Hata: Koordinat CSV bulunamadı: {csv_path}")
    if not crops_dir.exists():
        sys.exit(f"Hata: Kırpıntı klasörü bulunamadı: {crops_dir}")

    with csv_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    existing_cache: dict[str, dict] = {}
    if args.only_new and out_json.exists():
        try:
            prev = json.loads(out_json.read_text(encoding="utf-8"))
            for r in prev.get("sonuclar", []):
                if r.get("dosya"):
                    existing_cache[r["dosya"]] = r
        except Exception:
            pass

    akr_map: dict[str, str] = {}
    if args.index_csv and Path(args.index_csv).exists():
        with Path(args.index_csv).open(encoding="utf-8") as f:
            akr_map = {r["kayit_id"]: (r.get("akrabalik") or "").strip() for r in csv.DictReader(f) if r.get("kayit_id")}

    selected: list[tuple[dict, Path]] = []
    reused: list[dict] = []
    for row in rows:
        fname = crop_filename(row)
        fpath = crops_dir / fname
        if not fpath.exists():
            continue
        kapsam = (row.get("kapsam") or "kayit").strip()
        etiket = (row.get("etiket") or "").strip()
        okuma = (row.get("okuma") or "").strip()
        if args.mode == "suspicious" and ("[?]" not in okuma and "?" not in okuma and "[?]" not in (row.get("not") or "")):
            continue
        if args.mode == "record" and kapsam != "kayit":
            continue
        if args.mode == "age" and not (kapsam == "kelime" and etiket == "yas"):
            continue

        cached = existing_cache.get(fname)
        if args.only_new and cached and cached.get("okuma") == okuma:
            reused.append(cached)
        else:
            selected.append((row, fpath))

    selected = selected[: args.limit]
    est_tok = sum(estimate_image_tokens(p) + 180 for _, p in selected)
    unit = PRICE_PER_1M[args.model]
    if args.dry_run:
        print(
            f"[DRY-RUN] crops ({args.model}, mod={args.mode}): {len(selected)} yeni kırpıntı "
            f"(+{len(reused)} önbellekten) | ~{est_tok:,} token (~${est_tok * unit / 1e6:.5f})"
        )
        return

    api_key = require_api_key()
    results = list(reused)
    total_tok = 0

    def run_one(item: tuple[dict, Path]) -> tuple[dict, int]:
        row, fpath = item
        kapsam = (row.get("kapsam") or "kayit").strip()
        etiket = (row.get("etiket") or "").strip()
        state, questions = build_crop_questions(row)
        resp = call_d1(api_key, args.model, state, questions, images=[image_data_url(fpath)])
        ans = resp.get("answers", {})
        durum, skor = classify_crop(kapsam, etiket, ans)
        tok = resp.get("usage", {}).get("input_tokens", 0)
        return {
            "dosya": fpath.name,
            "kayit_id": row["kayit_id"].strip(),
            "kapsam": kapsam,
            "etiket": etiket,
            "okuma": (row.get("okuma") or "").strip(),
            "durum": durum,
            "skor": round(skor, 4),
            "input_tokens": tok,
            "answers": ans,
        }, tok

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = [pool.submit(run_one, it) for it in selected]
        for fut in as_completed(futs):
            rec, tok = fut.result()
            results.append(rec)
            total_tok += tok

    results.sort(key=lambda r: ({"ONCELIKLI": 0, "GRI_BOLGE": 1, "RAKAM_VLM": 2, "UYUMLU": 3}.get(r["durum"], 9), r["skor"]))
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps({"model": args.model, "mode": args.mode, "toplam_input_token": total_tok, "sonuclar": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    counts = defaultdict(int)
    hane_mismatches: list[tuple[dict, str, float]] = []
    for r in results:
        counts[r["durum"]] += 1
        hp = r.get("answers", {}).get("hane_basi_mi", {}).get("noul")
        if hp is not None and r["kayit_id"] in akr_map:
            akr = akr_map[r["kayit_id"]]
            if (not akr and hp < 0.30) or (akr and hp > 0.80):
                hane_mismatches.append((r, akr or "(hane reisi)", hp))

    if args.out_md:
        md_path = Path(args.out_md)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# d1.2 Kırpıntı Doğrulama Raporu (`{csv_path.stem}` — {args.mode})",
            "",
            f"- **Model:** `{args.model}` | **Yeni:** {len(selected)} (+{len(reused)} önbellek) | **Token:** {total_tok:,} (~`${total_tok * unit / 1e6:.5f}`)",
            f"- **Triyaj:** 🔴 Öncelikli: **{counts['ONCELIKLI']}** · ⚠️ Hane Uyuşmazı: **{len(hane_mismatches)}** · 🟡 Gri Bölge: **{counts['GRI_BOLGE']}** · 🔢 Rakam (VLM): **{counts['RAKAM_VLM']}** · 🟢 Uyumlu: **{counts['UYUMLU']}**",
            "",
        ]
        if hane_mismatches:
            lines += [
                "## ⚠️ Hane-Sınırı Uyuşmazlıkları",
                "",
                "| Kırpıntı | Dizindeki Akrabalık | `hane_basi_mi` | Okuma |",
                "|---|---|---:|---|",
            ]
            for r, akr, hp in hane_mismatches:
                lines.append(f"| `{r['dosya']}` | {akr} | {hp:.2f} | {r['okuma'].replace('|', '/')} |")
            lines.append("")
        lines += [
            "## Tüm Kırpıntılar (Öncelik Sırasıyla)",
            "",
            "| Durum | Kırpıntı | Skor | Okuma |",
            "|---|---|---:|---|",
        ]
        for r in results:
            lines.append(f"| `{r['durum']}` | `{r['dosya']}` | {r['skor']:.2f} | {r['okuma'].replace('|', '/')} |")
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        f"Tamamlandı: {len(results)} kırpıntı (yeni={len(selected)}, token={total_tok:,}, ~${total_tok * unit / 1e6:.5f}) "
        f"| 🔴 {counts['ONCELIKLI']} · ⚠️ {len(hane_mismatches)} · 🟡 {counts['GRI_BOLGE']} · 🟢 {counts['UYUMLU']}"
    )


def summarize_record(row: dict, households: dict) -> dict:
    members = []
    key = (row.get("belge", ""), row.get("yerlesim_id", ""), row.get("hane", ""))
    if all(key):
        for m in households.get(key, [])[:8]:
            members.append(f"{m.get('akrabalik') or 'reis'} {m.get('ad', '')} b. {m.get('baba_adi', '')} (yaş {m.get('yas') or '?'})")
    return {
        "kayit_id": row.get("kayit_id", ""),
        "belge": row.get("belge", ""),
        "yil": row.get("yil_m", ""),
        "koy": row.get("karye_ham") or row.get("yerlesim_id", ""),
        "hane": row.get("hane", ""),
        "akrabalik": row.get("akrabalik") or "hane_reisi",
        "lakap_unvan": " ".join(x for x in (row.get("lakap", ""), row.get("unvan", "")) if x),
        "ad": row.get("ad", ""),
        "baba_adi": row.get("baba_adi", ""),
        "yas": row.get("yas", ""),
        "tahmini_dogum": row.get("tahmini_dogum", ""),
        "eskal": row.get("eskal_not", ""),
        "serh": row.get("serh_vukuat", ""),
        "hane_uyeleri": members,
    }


def cmd_match(args: argparse.Namespace) -> None:
    idx_path = Path(args.index_csv)
    if not idx_path.exists():
        sys.exit(f"Hata: Kişi dizini CSV bulunamadı: {idx_path}")

    records: list[dict] = []
    households: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    with idx_path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            records.append(r)
            key = (r.get("belge", ""), r.get("yerlesim_id", ""), r.get("hane", ""))
            if all(key):
                households[key].append(r)

    g1 = [r for r in records if args.doc1.lower() in (r.get("belge") or "").lower()]
    g2 = [r for r in records if args.doc2.lower() in (r.get("belge") or "").lower()]
    if args.village:
        v = args.village.lower()
        g1 = [r for r in g1 if v == (r.get("yerlesim_id") or "").lower() or v in (r.get("karye_ham") or "").lower()]
        g2 = [r for r in g2 if v == (r.get("yerlesim_id") or "").lower() or v in (r.get("karye_ham") or "").lower()]

    by_village_name: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in g2:
        na = norm_name(r.get("ad", ""))
        if na:
            by_village_name[((r.get("yerlesim_id") or "").lower(), na)].append(r)

    pairs: list[tuple[dict, dict]] = []
    for r1 in g1:
        na = norm_name(r1.get("ad", ""))
        if not na:
            continue
        nb1 = norm_name(r1.get("baba_adi", ""))
        for r2 in by_village_name.get(((r1.get("yerlesim_id") or "").lower(), na), []):
            nb2 = norm_name(r2.get("baba_adi", ""))
            if args.require_father and nb1 and nb2 and nb1 != nb2:
                continue
            pairs.append((r1, r2))

    pairs = pairs[: args.limit]
    est_tok = len(pairs) * 520
    unit = PRICE_PER_1M[args.model]
    if args.dry_run:
        print(
            f"[DRY-RUN] match ({args.doc1} ↔ {args.doc2}, koy={args.village or 'tümü'}): "
            f"{len(pairs)} aday çift | ~{est_tok:,} token (~${est_tok * unit / 1e6:.5f})"
        )
        return

    api_key = require_api_key()
    questions = {
        "ayni_kisi": {
            "type": "noul",
            "instructions": "Do record_1 and record_2 refer to the exact same historical individual across the two Ottoman registers?",
        },
        "ayni_hane_ailesi": {
            "type": "noul",
            "instructions": "Do record_1 and record_2 belong to the same household/nuclear family (even if father/son/brothers)?",
        },
        "iliski_turu": {
            "type": "choice",
            "instructions": "What is the most likely relationship between record_1 and record_2?",
            "criteria": {
                "ayni_kisi": "The exact same person recorded in two registers",
                "ayni_aile_farkli_kisi": "Different members of the same household/family",
                "farkli_aile": "Unrelated people sharing a common name or village",
                "belirsiz": "Insufficient information",
            },
        },
        "yas_uyumu": {
            "type": "score",
            "instructions": "How consistent is the age difference with the year gap between the two registers (allowing +/-3 years Ottoman census rounding)?",
            "criteria": [
                "Inconsistent or impossible age difference",
                "Roughly plausible or one age missing",
                "Closely matches the expected year difference",
            ],
        },
    }

    def run_pair(pair: tuple[dict, dict]) -> tuple[dict, int]:
        r1, r2 = pair
        state = {
            "record_1": summarize_record(r1, households),
            "record_2": summarize_record(r2, households),
        }
        resp = call_d1(api_key, args.model, state, questions)
        tok = resp.get("usage", {}).get("input_tokens", 0)
        return {
            "kayit_1": r1["kayit_id"],
            "kayit_2": r2["kayit_id"],
            "ozet_1": f"{r1.get('belge')} {r1.get('ad')} b. {r1.get('baba_adi')} (yaş {r1.get('yas') or '?'})",
            "ozet_2": f"{r2.get('belge')} {r2.get('ad')} b. {r2.get('baba_adi')} (yaş {r2.get('yas') or '?'})",
            "input_tokens": tok,
            "answers": resp.get("answers", {}),
        }, tok

    results: list[dict] = []
    total_tok = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        for fut in as_completed([pool.submit(run_pair, p) for p in pairs]):
            rec, tok = fut.result()
            results.append(rec)
            total_tok += tok

    results.sort(key=lambda r: r["answers"].get("ayni_kisi", {}).get("noul", 0.0), reverse=True)
    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps({"model": args.model, "doc1": args.doc1, "doc2": args.doc2, "toplam_input_token": total_tok, "sonuclar": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if args.out_md:
        md_path = Path(args.out_md)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# d1.2 Çapraz Defter Eşleştirme ({args.doc1} ↔ {args.doc2})",
            "",
            f"- **Model:** `{args.model}` | **Çift:** {len(results)} | **Token:** {total_tok:,} (~`${total_tok * unit / 1e6:.5f}`)",
            "",
            "| Kayıt 1 | Kayıt 2 | Aynı Kişi | Aynı Aile | İlişki | Yaş Uyumu |",
            "|---|---|---:|---:|---|---:|",
        ]
        for r in results:
            a = r["answers"]
            lines.append(
                f"| `{r['kayit_1']}` {r['ozet_1']} | `{r['kayit_2']}` {r['ozet_2']} | "
                f"{a.get('ayni_kisi', {}).get('noul', 0):.2f} | {a.get('ayni_hane_ailesi', {}).get('noul', 0):.2f} | "
                f"`{a.get('iliski_turu', {}).get('choice', '?')}` | {a.get('yas_uyumu', {}).get('score', 0):.2f}/2 |"
            )
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    strong = sum(1 for r in results if r["answers"].get("ayni_kisi", {}).get("noul", 0) >= 0.70)
    print(f"Tamamlandı: {len(results)} çift (≥0.70 aynı kişi: {strong}) | token={total_tok:,} (~${total_tok * unit / 1e6:.5f})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="İsteğe bağlı Liquid AI d1.2-ultra görsel kırpıntı doğrulama ve hane-bağlamlı eşleştirme aracı."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_cal = sub.add_parser("calibrate", help="Tek bir kırpıntıda Doğru vs. Yanlış okuma A/B (yes-bias) kalibrasyonu yapar.")
    p_cal.add_argument("--image", required=True, help="Test edilecek kırpıntı görseli (.jpg/.png)")
    p_cal.add_argument("--true-reading", required=True, help="Bilinen doğru Osmanlıca/Türkçe okuma")
    p_cal.add_argument("--false-reading", required=True, help="Bilinen yanlış (çeldirici) okuma")
    p_cal.add_argument("--model", default="d1.2-ultra", choices=["d1.2-ultra", "d1.2"])
    p_cal.add_argument("--dry-run", action="store_true", help="API çağırmadan maliyet tahmini göster")
    p_cal.set_defaults(func=cmd_calibrate)

    p_crp = sub.add_parser("crops", help="Koordinat CSV + kırpıntıları artımlı doğrular ve HTML proofread uyumlu JSON üretir.")
    p_crp.add_argument("--csv", required=True, help="Koordinat CSV yolu")
    p_crp.add_argument("--crops-dir", required=True, help="Kırpıntı görselleri klasörü")
    p_crp.add_argument("--out-json", required=True, help="Çıktı JSON yolu (crop_and_verify.py proofread --scores-json ile uyumlu)")
    p_crp.add_argument("--out-md", default="", help="İsteğe bağlı Markdown triyaj raporu yolu")
    p_crp.add_argument("--index-csv", default="", help="İsteğe bağlı kayitlar.csv (⚠️ Hane Uyuşmazı denetimi için)")
    p_crp.add_argument("--mode", default="all", choices=["all", "suspicious", "record", "age"])
    p_crp.add_argument("--only-new", action="store_true", help="Önceki JSON'da aynı okumayla taranmış kırpıntıları atla")
    p_crp.add_argument("--limit", type=int, default=200)
    p_crp.add_argument("--workers", type=int, default=6)
    p_crp.add_argument("--model", default="d1.2-ultra", choices=["d1.2-ultra", "d1.2"])
    p_crp.add_argument("--dry-run", action="store_true", help="API çağırmadan token/maliyet tahmini göster")
    p_crp.set_defaults(func=cmd_crops)

    p_mat = sub.add_parser("match", help="kayitlar.csv içindeki iki defteri hane bağlamlı JSON ile eşleştirir.")
    p_mat.add_argument("--index-csv", required=True, help="Kişi dizini CSV yolu (kayitlar.csv)")
    p_mat.add_argument("--doc1", required=True, help="Birinci defter filtresi (örn. 'NFS.d 582')")
    p_mat.add_argument("--doc2", required=True, help="İkinci defter filtresi (örn. 'NFS.d 663' veya '4874')")
    p_mat.add_argument("--village", default="", help="İsteğe bağlı yerlesim_id veya karye filtresi")
    p_mat.add_argument("--require-father", action="store_true", help="Her iki tarafta baba adı varsa baba adının da eşleşmesini şart koş")
    p_mat.add_argument("--out-json", required=True, help="Çıktı JSON yolu")
    p_mat.add_argument("--out-md", default="", help="İsteğe bağlı Markdown rapor yolu")
    p_mat.add_argument("--limit", type=int, default=100)
    p_mat.add_argument("--workers", type=int, default=6)
    p_mat.add_argument("--model", default="d1.2-ultra", choices=["d1.2-ultra", "d1.2"])
    p_mat.add_argument("--dry-run", action="store_true", help="API çağırmadan token/maliyet tahmini göster")
    p_mat.set_defaults(func=cmd_match)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
