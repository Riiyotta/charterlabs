#!/usr/bin/env python3
"""Derive schema/source-leakage-patterns.json from the REAL source project (R2).

Generation-mode PageSpecs must not reproduce the source company's identity or
content. This script reads the clone's real files and writes the patterns the
semantic validator uses for its GENERATION_MODE_* rules, each with file:line
evidence. Nothing is hand-typed and no source copy or source URL is stored as
text: copy is stored as sha256 of 5-word shingles (and of whole 3-4 word
phrases), URLs and hosts as sha256 fingerprints. Brand, partner and asset-file
names are stored as text (they are identifiers, not copy).

Inputs (relative to the project root that holds design-repo/):
  src/**/*.jsx|js     copy (string literals + JSX text), brand, partners, asset refs, URLs
  index.html          title + meta description, icons
  CLONE_SPEC.md, ASSETS.md   brand variants and URLs (not copy: spec prose is not site copy)
  public/**           the source asset files
  design-repo/assets/asset-roles.json   role -> leak category of each source file

    python3 extraction/build_leakage_patterns.py [--source-root DIR]          # rewrite
    python3 extraction/build_leakage_patterns.py [--source-root DIR] --check  # exit 1 on drift

Normalisation (shared with schema/semantic_validate.py, imported from there so it
can never drift): NFKC, zero-width/soft-hyphen removal, curly quotes -> straight,
dashes -> '-', whitespace collapsed, lower-cased; tokens = [a-z0-9]+('[a-z0-9]+)*.
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "schema"))
import semantic_validate as sv  # noqa: E402

OUT = "schema/source-leakage-patterns.json"
CLAIM_RX = re.compile(r"\d|%|\$|€|\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|seconds?|minutes?|hours?|days?|instantly|instant|fees?|near-zero)\b", re.I)
LITERAL_RX = re.compile(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"|`([^`$\n]*)`")
NONCOPY_CONTEXT = re.compile(r"(className|class|import|from|src|href|id|type|as|offset|tone|data-[a-z-]+|aria-[a-z]+|role|key|fetchpriority|loading|decoding)\s*[=:(]?\s*$")
ROLE_CATEGORY = sv.PINNED_LEAK_CATEGORY  # pinned in code (semantic_validate), not read from the registry


def _files(root, sub, exts):
    base = os.path.join(root, sub)
    out = []
    for d, dirs, fs in os.walk(base):
        dirs[:] = sorted(x for x in dirs if x not in ("node_modules", "dist", ".git"))
        for f in sorted(fs):
            if f.endswith(exts):
                out.append(os.path.relpath(os.path.join(d, f), root))
    return out


def _lines(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as f:
        return f.read().split("\n")


def _is_copy(s):
    """Natural-language test: >= 2 tokens and >= 60% plain words (rejects class lists, SVG paths, CSS values)."""
    toks = s.strip().split()
    if len(toks) < 2:
        return False
    words = [t for t in toks if re.match(r"^[(\"'“‘*]?[A-Za-z][A-Za-z'’]*[.,!?:;)\"'”’]*$", t) or re.match(r"^\d[\d.,%]*[%]?[.,]?$", t) or re.match(r"^[A-Z][a-z]+(-[a-z]+)+[.,]?$", t)]
    return len(words) * 10 >= len(toks) * 6 and sum(1 for t in toks if re.search(r"[A-Za-z]{2,}", t)) * 10 >= max(10, len(toks) * 4)


def copy_strings(root):
    """(file, line, text) for every copy string rendered by the clone."""
    out = []
    for rel in _files(root, "src", (".jsx", ".js")):
        if "/motion/" in rel.replace(os.sep, "/") and rel.endswith(".js"):
            continue
        in_block = False
        for i, raw in enumerate(_lines(root, rel), 1):
            line = raw.strip()
            if in_block:
                if "*/" in line:
                    in_block = False
                continue
            if line.startswith("/*") or line.startswith("/**"):
                in_block = "*/" not in line
                continue
            if line.startswith(("//", "*", "import ", "export {")):
                continue
            code = re.sub(r"\s//\s.*$", "", raw)
            for m in LITERAL_RX.finditer(code):
                s = next(g for g in m.groups() if g is not None)
                if NONCOPY_CONTEXT.search(code[:m.start()]):
                    continue
                if _is_copy(s):
                    out.append((rel, i, s.replace("\\'", "'")))
            # JSX text: a line that is only prose between tags
            t = line
            if t and not re.search(r"[<>{}=;:?'\"`]|=>|^\w+\(|^[.)\]]", t.rstrip("'’")) and _is_copy(t) and re.match(r"^[A-Z0-9“‘(*]", t):
                out.append((rel, i, t))
    html = _lines(root, "index.html")
    for i, raw in enumerate(html, 1):
        for m in re.finditer(r"<title>([^<]+)</title>|content=\"([^\"]+)\"", raw):
            s = m.group(1) or m.group(2)
            if _is_copy(s) and "width=" not in s:
                out.append(("index.html", i, s))
    seen, uniq = set(), []
    for item in out:
        if item not in seen:
            seen.add(item)
            uniq.append(item)
    return uniq


def build(root):
    roles = sv.load_json("assets/asset-roles.json", REPO)["roles"]
    text_files = _files(root, "src", (".jsx", ".js")) + ["index.html"] + [f for f in ("CLONE_SPEC.md", "ASSETS.md") if os.path.isfile(os.path.join(root, f))]

    # ---- brand variants (word-boundary, case-insensitive)
    brand = {}
    for rel in text_files:
        for i, raw in enumerate(_lines(root, rel), 1):
            for m in re.finditer(r"\bcharter(?:labs(?:\.io)?|[ -](?:labs|wallet|app|live|pay))?\b", raw, re.I):
                tok = sv.normalize_match(m.group(0))
                e = brand.setdefault(tok, {"pattern": tok, "occurrences": 0, "foundAt": []})
                e["occurrences"] += 1
                if len(e["foundAt"]) < 3:
                    e["foundAt"].append("%s:%d" % (rel, i))
    # ---- partner / customer names: the logo ticker's alt texts + legal entities named in copy
    partners = {}
    logo = "src/components/Logo.jsx"
    for i, raw in enumerate(_lines(root, logo), 1):
        m = re.search(r"\{\s*src:\s*'[^']+',\s*alt:\s*'([^']+)'", raw)
        if m:
            partners.setdefault(m.group(1), {"name": m.group(1), "match": "case-sensitive word", "foundAt": []})["foundAt"].append("%s:%d" % (logo, i))
    for rel, i, s in copy_strings(root):
        for m in re.finditer(r"\b[A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)* (?:LLC|Inc\.?|Ltd\.?|Financial)\b", s):
            if re.search(r"\bcharter", m.group(0), re.I):
                continue  # the source company itself is BRAND, not a partner
            e = partners.setdefault(m.group(0), {"name": m.group(0), "match": "case-insensitive phrase", "foundAt": []})
            if len(e["foundAt"]) < 3:
                e["foundAt"].append("%s:%d" % (rel, i))
    # ---- URLs and hosts (fingerprints only)
    urls, hosts = {}, {}
    for rel in text_files:
        for i, raw in enumerate(_lines(root, rel), 1):
            for u in re.findall(r"https?://[^\s'\"`\)\]<>,|]+", raw):
                u = u.rstrip(".;:")
                host = re.sub(r"^https?://", "", u).split("/")[0].lower()
                if host.endswith("w3.org"):
                    continue  # XML namespace, not a destination
                fu, fh = sv.url_fingerprint(u), sv.url_fingerprint(re.sub(r"^www\.", "", host))
                urls.setdefault(fu, []).append("%s:%d" % (rel, i))
                hosts.setdefault(fh, []).append("%s:%d" % (rel, i))
    # ---- source asset files
    by_file = {}
    for role_id, r in roles.items():
        for f in r.get("sourceFiles", []):
            if "inline" not in f:
                by_file[os.path.basename(f).lower()] = role_id
    assets = {}
    for rel in _files(root, "public", (".webp", ".png", ".svg", ".jpg", ".jpeg", ".gif", ".avif", ".woff2", ".ico")):
        b = os.path.basename(rel).lower()
        if b.endswith(".woff2"):
            continue  # Inter is OFL-1.1 and may be reused (asset-roles licensedResources)
        role_id = by_file.get(b)
        assets[b] = {"file": b, "foundAt": [rel], "role": role_id, "category": ROLE_CATEGORY.get(role_id, "ASSET")}
    for rel in _files(root, "src", (".jsx",)):
        for i, raw in enumerate(_lines(root, rel), 1):
            for m in re.findall(r"/(?:images|icons|social)/[A-Za-z0-9_./()-]+\.(?:webp|png|svg|jpg)", raw):
                b = os.path.basename(m).lower()
                if b in assets and len(assets[b]["foundAt"]) < 3:
                    assets[b]["foundAt"].append("%s:%d" % (rel, i))
    # ---- copy: hashed 5-word shingles + whole 3-4 word phrases; claims split out
    copy_sh, claim_sh, copy_ph, claim_ph, cev = set(), set(), set(), set(), []
    for rel, i, s in copy_strings(root):
        toks = sv.match_tokens(s)
        claim = bool(CLAIM_RX.search(sv.normalize_match(s)))
        sh = sv.shingles(toks)
        if sh:
            (claim_sh if claim else copy_sh).update(sh)
        elif len(toks) >= 3:
            (claim_ph if claim else copy_ph).add(sv.phrase_hash(toks))
        else:
            continue
        cev.append({"at": "%s:%d" % (rel, i), "tokens": len(toks), "category": "CLAIM" if claim else "COPY"})
    return {
        "version": "2.0.0",
        "$description": "GENERATED by extraction/build_leakage_patterns.py from the real source project. Used by the GENERATION_MODE_* rules in schema/semantic_validate.py (mode = generation only; clone mode may reuse source content). Copy is hashed (5-word shingles), URLs/hosts are fingerprinted; no source copy or source URL is stored as text. Detection is string-based: paraphrase is not caught. No human has reviewed these patterns.",
        "normalisation": "semantic_validate.normalize_match: NFKC, zero-width + soft hyphen removed, curly quotes straightened, unicode dashes -> '-', whitespace collapsed, lower-case; tokens [a-z0-9]+('[a-z0-9]+)*",
        "shingleSize": sv.SHINGLE,
        "categories": {
            "BRAND": {"rule": "GENERATION_MODE_BRAND", "match": "word boundary, case-insensitive, on normalised text; also any brand.* asset role and the brand's asset files",
                      "patterns": sorted(brand.values(), key=lambda e: e["pattern"])},
            "CUSTOMER": {"rule": "GENERATION_MODE_CUSTOMER", "match": "single names: case-sensitive word on normalised text (they are also common words); entities: case-insensitive phrase; any case inside a partner.logo slot",
                         "patterns": sorted(partners.values(), key=lambda e: e["name"])},
            "PERSON": {"rule": "GENERATION_MODE_PERSON", "match": "asset basenames of real people's photos (and their derived renders) + the person roles; the source names no individual",
                       "files": sorted(b for b, a in assets.items() if a["category"] == "PERSON")},
            "SCREENSHOT": {"rule": "GENERATION_MODE_SCREENSHOT", "match": "asset basenames of the source app's real UI screens / share image",
                           "files": sorted(b for b, a in assets.items() if a["category"] == "SCREENSHOT")},
            "ASSET": {"rule": "GENERATION_MODE_ASSET", "match": "basename of any other source asset file (case-insensitive)",
                      "files": sorted(b for b, a in assets.items() if a["category"] in ("ASSET", "BRAND", "CUSTOMER"))},
            "COPY": {"rule": "GENERATION_MODE_COPY", "match": "any 5-token window of a PageSpec string whose sha256 is listed, or a whole 3-4 token string",
                     "shingleSha256": sorted(copy_sh), "phraseSha256": sorted(copy_ph)},
            "CLAIM": {"rule": "GENERATION_MODE_CLAIM", "match": "as COPY, for source strings carrying a number, time, fee or speed claim",
                      "shingleSha256": sorted(claim_sh), "phraseSha256": sorted(claim_ph)},
            "URL": {"rule": "GENERATION_MODE_URL", "match": "full-URL or host fingerprint of a source URL; and in generation mode every absolute URL must be on a reserved .example or .invalid host",
                    "urlSha256": {k: v[:3] for k, v in sorted(urls.items())}, "hostSha256": {k: v[:3] for k, v in sorted(hosts.items())}},
        },
        "assetFiles": {k: assets[k] for k in sorted(assets)},
        "copyEvidence": cev,
        "notApplicable": {
            "EMBED": "The source has no iframe/video/third-party embed (grep of src/ and index.html); any embed URL in a generation PageSpec is still rejected by GENERATION_MODE_URL.",
            "STORE": "The source has no App Store / TestFlight / Play link or badge; a store URL in a generation PageSpec is rejected by GENERATION_MODE_URL (non-placeholder host).",
            "RATING": "The source shows no reviews or ratings.",
        },
    }


def main(argv):
    root = argv[argv.index("--source-root") + 1] if "--source-root" in argv else (os.environ.get("DESIGN_REPO_SOURCE_ROOT") or os.path.dirname(REPO))
    if not os.path.isdir(os.path.join(root, "src")):
        print("source project not found at the source root; cannot (re)derive leakage patterns")
        return 2
    want = build(root)
    p = os.path.join(REPO, OUT)
    if "--check" in argv:
        have = json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else None
        if have != want:
            print("source-leakage-patterns.json differs from what the source derives; run build_leakage_patterns.py")
            return 1
        print("source-leakage-patterns.json matches the source")
        return 0
    with open(p, "w", encoding="utf-8") as f:
        json.dump(want, f, indent=2, ensure_ascii=False)
        f.write("\n")
    c = want["categories"]
    print("wrote %s: brand %d, customer %d, person %d, screenshot %d, asset %d, copy %d+%d, claim %d+%d, url %d/%d hosts, %d copy strings" % (
        OUT, len(c["BRAND"]["patterns"]), len(c["CUSTOMER"]["patterns"]), len(c["PERSON"]["files"]), len(c["SCREENSHOT"]["files"]), len(c["ASSET"]["files"]),
        len(c["COPY"]["shingleSha256"]), len(c["COPY"]["phraseSha256"]), len(c["CLAIM"]["shingleSha256"]), len(c["CLAIM"]["phraseSha256"]),
        len(c["URL"]["urlSha256"]), len(c["URL"]["hostSha256"]), len(want["copyEvidence"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
