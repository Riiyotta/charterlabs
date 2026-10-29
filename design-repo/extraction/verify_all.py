#!/usr/bin/env python3
"""One-shot verification for this design-repo. Prints PASS / WARN / FAIL per check.
Exit 1 if any check FAILs. WARN never fails the run.

Checks
  json-parse            every *.json file parses
  schema-draft7         pagespec.schema.json is valid Draft-07; example has 0 schema errors
  semantic-example      semantic validator: example has 0 errors
  allowlist-parity      allowlist ids <-> contract files (no phantom, no orphan); settable
                        node/content props <-> schema; assetRoles <-> schema <-> asset-roles.json
  allowlist-version     manifest.allowlistVersion == component-allowlist.json version (machine-checked)
  pagespec-version      manifest.pageSpecVersion == schema const (machine-checked)
  manifest-counts       manifest.counts recomputed from disk
  readme-counts         README.md counts block recomputed from disk
  entry-points          every entryPoint exists INSIDE design-repo (no ../, no absolute paths)
  no-local-paths        no absolute machine paths anywhere in the repo
  evidence-ids          every evidence id used anywhere resolves in measured-values.json
  citations             every {path, lines, anchor} resolves against the source project: file
                        exists, range within file length, anchor inside the range. WARNs (does
                        not fail) when no source tree is present (standalone copy / zip).
  asset-roles           closed enum parity + PINNED policies for compliance-critical roles
  graph-validator       compatibility/graph.json rule ids == semantic_validate.RULES
  template-contracts    template nodes agree with section contracts; IA parity when ia.json is beside the repo
  protected-content     no repo file contains verbatim source copy, the live form endpoint or
                        the real social URLs (checked by fingerprint)
  token-refs            themes/semantic/component refs resolve; policy categories == catalog keys
  adversarial           schema/tests/adversarial_test.py exits 0

Usage: python3 extraction/verify_all.py [--source-root DIR] [--quick]
  --source-root  project root holding the cited evidence (default: env
                 DESIGN_REPO_SOURCE_ROOT, else the folder containing design-repo/)
  --quick        skip the adversarial suite (used by prove_drift.py)
Drift-proofing of these checks: extraction/prove_drift.py.
"""
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "schema"))
sys.path.insert(0, os.path.join(REPO, "extraction"))
import semantic_validate as sv  # noqa: E402

# Second, independent source for the compliance-critical asset-role policies
# (a membership-in-enum check alone cannot catch a swap to another valid value).
PINNED = {
    "brand.mark": "project-supplied-only",
    "brand.wordmark": "project-supplied-only",
    "social.og-image": "project-supplied-only",
    "partner.logo": "fictional-placeholder-only",
    "photo.portrait": "generate-non-identifiable-or-licensed-stock",
    "device.screen": "generate-original-fictional-ui",
    "photo.product-in-hand": "generate-original-fictional-ui",
}

# Availability pin: an INDEPENDENT copy of semantic_validate.PINNED_AVAILABILITY.
# asset-roles check fails unless this, the validator's copy and the registry agree.
PINNED_AVAILABILITY = {
    "brand.mark": "clone-only",
    "brand.wordmark": "clone-only",
    "social.og-image": "clone-only",
    "nav.card-image": "clone-only",
    "nav.ring": "clone-only",
    "device.screen": "clone-only",
    "device.screen-reflection": "clone-only",
    "partner.logo": "blocked-for-generation",
    "texture.backdrop": "clone-only",
    "photo.lifestyle": "clone-only",
    "photo.product-in-hand": "clone-only",
    "photo.portrait": "blocked-for-generation",
    "photo.portrait-ascii": "blocked-for-generation",
    "photo.reflection": "blocked-for-generation",
    "placeholder.brand-mark": "generation-safe",
    "user.supplied-asset": "generation-safe",
    "generated.illustration": "generation-safe",
    "placeholder.screenshot": "generation-safe",
    "fictional.person": "generation-safe",
    "placeholder.company-logo": "generation-safe",
    "generated.derived-render": "generation-safe",
    "placeholder.url": "generation-safe",
    "original.copy": "generation-safe",
}
# Retrieval pin (R8): independent copy of semantic_validate.RETRIEVAL_INELIGIBLE (ids only).
RETRIEVAL_INELIGIBLE = {"component.nav-menu-panel", "component.smooth-scroll"}
# Wrapper-gate thresholds (R9): must equal extraction/wrapper_gate.py's constants.
WRAPPER_THRESHOLDS = {"HERO_WARN_PX": 1800, "HERO_ERROR_PX": 3000, "SHARE_WARN": 0.50, "SHARE_ERROR": 0.60, "MIN_INFLOW_SECTIONS": 3, "VIEWPORT_WIDTH": 1440}
# Built from fragments so this file does not match its own scan.
LOCAL_PATH_PATTERNS = ["/" + "Users/", "/" + "private/", "/" + "tmp/", "C:" + "\\\\", "/" + "home/", "/" + "var/folders"]

RESULTS = []


def res(name, status, detail=""):
    RESULTS.append((name, status, detail))
    print("%-20s %-4s %s" % (name, status, detail))


def J(rel):
    return sv.load_json(rel, REPO)


def all_files():
    for d, dirs, files in os.walk(REPO):
        dirs[:] = [x for x in dirs if x not in ("__pycache__", ".git")]
        for f in files:
            if f == ".DS_Store" or f.endswith(".pyc"):
                continue
            yield os.path.join(d, f)


def rel(p):
    return os.path.relpath(p, REPO)


def contract_files():
    out = {}
    for d in ("primitives", "components", "sections"):
        for f in sorted(os.listdir(os.path.join(REPO, d))):
            if f.endswith(".json"):
                out["%s/%s" % (d, f)] = J("%s/%s" % (d, f))
    return out


# --------------------------------------------------------------------------
def c_json():
    bad = []
    for p in all_files():
        if p.endswith(".json"):
            try:
                json.load(open(p, encoding="utf-8"))
            except Exception as e:  # noqa: BLE001
                bad.append("%s: %s" % (rel(p), e))
    res("json-parse", "FAIL" if bad else "PASS", "; ".join(bad) or "all JSON parses")


def c_schema():
    from jsonschema import Draft7Validator
    s = J("schema/pagespec.schema.json")
    try:
        Draft7Validator.check_schema(s)
    except Exception as e:  # noqa: BLE001
        return res("schema-draft7", "FAIL", "schema invalid: %s" % e)
    out, bad = [], 0
    for p in sv.example_paths(REPO):
        n = len(list(Draft7Validator(s).iter_errors(json.load(open(p, encoding="utf-8")))))
        bad += n
        out.append("%s: %d" % (os.path.basename(p), n))
    if not out:
        return res("schema-draft7", "FAIL", "no examples in schema/examples/")
    res("schema-draft7", "FAIL" if bad else "PASS", "Draft-07 errors per example: " + ", ".join(out))


def c_semantic():
    out, bad = [], 0
    for p in sv.example_paths(REPO):
        spec = json.load(open(p, encoding="utf-8"))
        errs, warns = sv.validate(spec)
        bad += len(errs)
        out.append("%s [%s]: %d error(s), %d warning(s)" % (os.path.basename(p), spec.get("mode"), len(errs), len(warns)))
    res("semantic-example", "FAIL" if bad or not out else "PASS", "; ".join(out) or "no examples")


def c_allowlist():
    al = J("tokens/llm/component-allowlist.json")
    schema = J("schema/pagespec.schema.json")
    roles = J("assets/asset-roles.json")
    probs = []
    files = contract_files()
    ids_on_disk = {c["id"]: f for f, c in files.items()}
    ids_listed = {e["id"]: e for e in al["entries"]}
    for i in sorted(set(ids_listed) - set(ids_on_disk)):
        probs.append("phantom allowlist entry %s (no contract file)" % i)
    for i in sorted(set(ids_on_disk) - set(ids_listed)):
        probs.append("orphan contract %s (%s) not in allowlist" % (i, ids_on_disk[i]))
    for i, e in ids_listed.items():
        if i in ids_on_disk and e["file"] != ids_on_disk[i]:
            probs.append("%s: allowlist file %s != %s" % (i, e["file"], ids_on_disk[i]))
        if e["kind"] == "section":
            key = "content_" + i.replace(".", "_").replace("-", "_")
            sp = list(schema["definitions"].get(key, {}).get("properties", {}).keys())
            if sorted(sp) != sorted(e["settableContentFields"]):
                probs.append("%s: settableContentFields %s != schema %s" % (i, e["settableContentFields"], sp))
            if sorted(e["settableNodeProperties"]) != sorted(schema["definitions"]["node"]["properties"].keys()):
                probs.append("%s: settableNodeProperties drift from schema node" % i)
    enum = schema["definitions"]["assetRole"]["enum"]
    if not (sorted(enum) == sorted(al["assetRoles"]) == sorted(k for k, v in roles["roles"].items() if v.get("kind") == "media")):
        probs.append("assetRole enum drift: schema/allowlist/asset-roles disagree")
    if sorted(al["pageSpecTopLevel"]) != sorted(schema["properties"].keys()):
        probs.append("pageSpecTopLevel drift from schema")
    sections_in_schema = schema["definitions"]["node"]["properties"]["section"]["enum"]
    if sorted(sections_in_schema) != sorted(i for i, e in ids_listed.items() if e["kind"] == "section"):
        probs.append("schema section enum != allowlisted sections")
    res("allowlist-parity", "FAIL" if probs else "PASS", "; ".join(probs) or "%d entries <-> %d contract files; roles/props in parity" % (len(ids_listed), len(files)))


def c_versions():
    m = J("registry.manifest.json")
    al = J("tokens/llm/component-allowlist.json")
    ok = m["allowlistVersion"] == al["version"]
    res("allowlist-version", "PASS" if ok else "FAIL", "manifest %s vs allowlist %s" % (m["allowlistVersion"], al["version"]))
    sc = J("schema/pagespec.schema.json")["properties"]["pageSpecVersion"]["const"]
    exs = sorted({json.load(open(p, encoding="utf-8")).get("pageSpecVersion") for p in sv.example_paths(REPO)})
    ex = ",".join(str(x) for x in exs)
    ok = len(exs) == 1 and m["pageSpecVersion"] == sc == exs[0]
    res("pagespec-version", "PASS" if ok else "FAIL", "manifest %s / schema const %s / example %s" % (m["pageSpecVersion"], sc, ex))


def count_leaves(o):
    if isinstance(o, dict):
        if "$value" in o:
            return 1
        return sum(count_leaves(v) for v in o.values())
    return 0


def recount():
    t = 0
    for d in ("00-foundation", "10-semantic", "20-component", "30-layout"):
        for f in sorted(os.listdir(os.path.join(REPO, "tokens", d))):
            if f.endswith(".json"):
                t += count_leaves(J("tokens/%s/%s" % (d, f)))
    files = contract_files()
    kinds = [c["kind"] for c in files.values()]
    tpl = J("templates/templates.json")["templates"]
    routes = J("templates/routes.json")
    graph = J("compatibility/graph.json")
    return {"tokens": t, "primitives": kinds.count("primitive"), "components": kinds.count("component"), "sections": kinds.count("section"),
            "templates": len(tpl), "routes": len(routes["routes"]), "linkedUnbuiltRoutes": len(routes["linkedUnbuiltRoutes"]),
            "assetRoles": len(J("assets/asset-roles.json")["roles"]), "graphRules": len(graph["rules"]),
            "citations": len(J("extraction/measured-values.json")["citations"]),
            "copyFingerprints": len(J("schema/protected-content.json")["copyFingerprints"]["sha256"]),
            "examples": len(sv.example_paths(REPO)),
            "generationSafeRoles": sum(1 for r in J("assets/asset-roles.json")["roles"].values() if r.get("availability") == "generation-safe")}


def c_counts():
    m = J("registry.manifest.json")["counts"]
    real = recount()
    diff = ["%s: manifest %s != disk %s" % (k, m.get(k), v) for k, v in real.items() if m.get(k) != v]
    diff += ["%s: in manifest but not recomputed" % k for k in m if k not in real]
    res("manifest-counts", "FAIL" if diff else "PASS", "; ".join(diff) or json.dumps(real))


def c_readme_counts():
    txt = open(os.path.join(REPO, "README.md"), encoding="utf-8").read()
    m = re.search(r"<!-- counts:start -->(.*?)<!-- counts:end -->", txt, re.S)
    if not m:
        return res("readme-counts", "FAIL", "README.md has no counts block")
    stated = {k: int(v) for k, v in re.findall(r"^\|\s*`?([A-Za-z]+)`?\s*\|\s*(\d+)\s*\|", m.group(1), re.M)}
    real = recount()
    diff = ["%s: README %s != disk %s" % (k, stated.get(k), v) for k, v in real.items() if stated.get(k) != v]
    res("readme-counts", "FAIL" if diff else "PASS", "; ".join(diff) or "README counts match disk")


def c_entry():
    m = J("registry.manifest.json")
    probs = []
    for name, p in m["entryPoints"].items():
        if p.startswith("/") or ".." in p.split("/") or re.match(r"^[A-Za-z]:", p):
            probs.append("%s -> %s points outside the package" % (name, p))
        elif not os.path.isfile(os.path.join(REPO, p)):
            probs.append("%s -> %s missing" % (name, p))
    res("entry-points", "FAIL" if probs else "PASS", "; ".join(probs) or "%d entry points, all inside design-repo/" % len(m["entryPoints"]))


def c_paths():
    hits = []
    for p in all_files():
        try:
            txt = open(p, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        for pat in LOCAL_PATH_PATTERNS:
            if pat in txt:
                hits.append("%s contains %r" % (rel(p), pat))
    res("no-local-paths", "FAIL" if hits else "PASS", "; ".join(hits) or "no absolute machine paths")


def _evidence_ids(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("evidence", "motionEvidence") and isinstance(v, list):
                out.update(x for x in v if isinstance(x, str))
            else:
                _evidence_ids(v, out)
    elif isinstance(o, list):
        for v in o:
            _evidence_ids(v, out)


def c_evidence():
    mv = J("extraction/measured-values.json")
    known = set(mv["citations"])
    used = set()
    for p in all_files():
        if p.endswith(".json") and not p.endswith("measured-values.json"):
            _evidence_ids(json.load(open(p, encoding="utf-8")), used)
    for q in mv["qaCorrections"]:
        used.add(q)
    missing = sorted(used - known)
    res("evidence-ids", "FAIL" if missing else "PASS", ("unresolved: %s" % missing[:10]) if missing else "%d evidence ids used, all resolve" % len(used))


def c_citations(src_root):
    cits = J("extraction/measured-values.json")["citations"]
    present = [c for c in cits.values() if os.path.isfile(os.path.join(src_root, c["path"]))]
    if not present:
        return res("citations", "WARN", "no source project found at the source root: %d citations not resolvable here (standalone copy). Not a failure." % len(cits))
    probs = []
    lens = {}
    for cid, c in cits.items():
        fp = os.path.join(src_root, c["path"])
        if not os.path.isfile(fp):
            probs.append("%s: %s missing" % (cid, c["path"]))
            continue
        if c["path"] not in lens:
            ls = open(fp, encoding="utf-8").read().split("\n")
            if ls and ls[-1] == "":
                ls = ls[:-1]
            lens[c["path"]] = ls
        ls = lens[c["path"]]
        m = re.match(r"^(\d+)-(\d+)$", c["lines"])
        if not m:
            probs.append("%s: bad range %s" % (cid, c["lines"]))
            continue
        a, b = int(m.group(1)), int(m.group(2))
        if a < 1 or b < a or b > len(ls):
            probs.append("%s: %s:%s exceeds file length %d" % (cid, c["path"], c["lines"], len(ls)))
            continue
        if c["anchor"] not in "\n".join(ls[a - 1:b]):
            probs.append("%s: anchor %r not inside %s:%s (in-range but wrong lines / source drifted)" % (cid, c["anchor"][:40], c["path"], c["lines"]))
    res("citations", "FAIL" if probs else "PASS", "; ".join(probs[:8]) + (" (+%d more)" % (len(probs) - 8) if len(probs) > 8 else "") if probs
        else "%d citations resolve (range + anchor) against the source project" % len(cits))


def c_roles():
    roles = J("assets/asset-roles.json")
    probs = []
    pol = set(roles["generationPolicies"])
    av_vals = set(roles["availabilityValues"])
    if av_vals != {"clone-only", "blocked-for-generation", "generation-safe"}:
        probs.append("availabilityValues must be exactly clone-only|blocked-for-generation|generation-safe")
    for r, d in roles["roles"].items():
        if d["generationPolicy"] not in pol:
            probs.append("%s: policy %s not in closed set" % (r, d["generationPolicy"]))
        if d.get("availability") not in av_vals:
            probs.append("%s: availability %r not closed" % (r, d.get("availability")))
        if (d.get("sourceFileReuse") or {}).get("generation") != "forbidden":
            probs.append("%s: sourceFileReuse.generation must be 'forbidden'" % r)
        if not d.get("generatedModeGuidance"):
            probs.append("%s: generatedModeGuidance missing" % r)
        if d.get("availability") != "generation-safe":
            subs = d.get("generationSafeSubstitutes") or []
            if not subs:
                probs.append("%s: non-generation-safe role needs generationSafeSubstitutes" % r)
            for x in subs:
                if roles["roles"].get(x, {}).get("availability") != "generation-safe":
                    probs.append("%s: substitute %s is not generation-safe" % (r, x))
        if d.get("generationPolicy") == "must-reuse-exact" and r.startswith("brand."):
            probs.append("%s: a real logo/wordmark is never must-reuse-exact" % r)
    for r in ("brand.mark", "brand.wordmark"):
        if PINNED_AVAILABILITY.get(r) == "generation-safe":
            probs.append("%s may never be generation-safe" % r)
    for r, want in PINNED.items():
        got = roles["roles"].get(r, {}).get("generationPolicy")
        if got != want:
            probs.append("PINNED %s must be %s, got %s" % (r, want, got))
    if roles.get("pinnedPolicies") != PINNED:
        probs.append("asset-roles.pinnedPolicies disagrees with verify_all PINNED")
    # availability: three independent sources must agree (this file, the validator, the registry)
    if PINNED_AVAILABILITY != sv.PINNED_AVAILABILITY:
        probs.append("PINNED_AVAILABILITY in verify_all and semantic_validate disagree: %s" % sorted(set(PINNED_AVAILABILITY.items()) ^ set(sv.PINNED_AVAILABILITY.items())))
    reg = {k: v.get("availability") for k, v in roles["roles"].items()}
    if reg != PINNED_AVAILABILITY:
        probs.append("registry availability != PINNED_AVAILABILITY: %s" % sorted(set(reg.items()) ^ set(PINNED_AVAILABILITY.items())))
    if roles.get("pinnedAvailability") != PINNED_AVAILABILITY:
        probs.append("asset-roles.pinnedAvailability disagrees with the code pin")
    # sections: generatedAssetRoles == generation-safe roles of their media slots
    for c in (x for x in contract_files().values() if x["kind"] == "section"):
        got = set()

        def walk(fields):
            for fs in fields.values():
                if fs.get("type") == "media":
                    got.update(x for x in fs["roles"] if PINNED_AVAILABILITY.get(x) == "generation-safe")
                    if not any(PINNED_AVAILABILITY.get(x) == "generation-safe" for x in fs["roles"]):
                        probs.append("%s: a media slot offers no generation-safe role" % c["id"])
                elif fs.get("type") == "object":
                    walk(fs["fields"])
                elif fs.get("type") == "list":
                    walk({"_": fs["item"]} if "type" in fs["item"] else fs["item"])
        walk(c["content"])
        if sorted(got) != sorted(c.get("generatedAssetRoles", [])):
            probs.append("%s: generatedAssetRoles %s != slot generation-safe roles %s" % (c["id"], c.get("generatedAssetRoles"), sorted(got)))
    res("asset-roles", "FAIL" if probs else "PASS", "; ".join(probs[:6]) or "%d roles (%d generation-safe), availability pinned in verify_all + semantic_validate + registry, %d pinned policies hold" % (
        len(roles["roles"]), sum(1 for v in reg.values() if v == "generation-safe"), len(PINNED)))


def c_graph():
    g = {r["id"] for r in J("compatibility/graph.json")["rules"]}
    v = set(sv.RULES)
    probs = ["graph rule %s has no validator implementation" % x for x in sorted(g - v)] + ["validator rule %s missing from graph" % x for x in sorted(v - g)]
    res("graph-validator", "FAIL" if probs else "PASS", "; ".join(probs) or "%d rules agree" % len(g))


def c_templates(src_root):
    tpl = J("templates/templates.json")["templates"]
    secs = {c["id"]: c for c in contract_files().values() if c["kind"] == "section"}
    probs = []
    for tid, t in tpl.items():
        for n in t["nodes"]:
            c = secs.get(n["section"])
            if not c:
                probs.append("%s: no contract for %s" % (tid, n["section"]))
                continue
            for k_t, k_c in (("tone", "tone"), ("anchorId", "anchorId"), ("region", "region")):
                if n[k_t] != c[k_c]:
                    probs.append("%s.%s: %s %r != contract %r" % (tid, n["section"], k_t, n[k_t], c[k_c]))
            if n["allowedVariants"] != c["variants"] or n["handoffAllowed"] != c["handoff"]["allowed"] or n["handoffObserved"] != c["handoff"]["observed"]:
                probs.append("%s.%s: variants/handoff drift" % (tid, n["section"]))
    routes = J("templates/routes.json")
    mapped = [r["path"] for r in routes["routes"]]
    for tid, t in tpl.items():
        for r in t["routes"]:
            if mapped.count(r) != 1:
                probs.append("route %s not mapped exactly once" % r)
    ia_note = ""
    iap = os.path.join(src_root, "ia.json")
    if os.path.isfile(iap):
        ia = json.load(open(iap, encoding="utf-8"))
        for it in ia.get("templates", []):
            if it["id"] in tpl and it["sections"] != [n["section"] for n in tpl[it["id"]]["nodes"]]:
                probs.append("IA drift: ia.json %s order differs from templates.json" % it["id"])
        ia_note = "; ia.json parity OK"
        status = "FAIL" if probs else "PASS"
    else:
        status = "FAIL" if probs else "WARN"
        ia_note = "; ia.json not beside the repo (IA parity skipped)"
    res("template-contracts", status, "; ".join(probs) or "templates agree with %d section contracts, routes 1:1%s" % (len(secs), ia_note))


def _strings(o, out):
    if isinstance(o, str):
        out.append(o)
    elif isinstance(o, dict):
        for v in o.values():
            _strings(v, out)
    elif isinstance(o, list):
        for v in o:
            _strings(v, out)


def c_protected():
    pc = J("schema/protected-content.json")
    fps = set(pc["copyFingerprints"]["sha256"])
    ufps = set(pc["urlFingerprints"]["waitlistEndpoint"]) | set(pc["urlFingerprints"]["social"])
    lpc = J("schema/source-leakage-patterns.json")["categories"]
    shs = set(lpc["COPY"]["shingleSha256"]) | set(lpc["CLAIM"]["shingleSha256"])
    # leakage URL fingerprints are not scanned here: the manifest records which site was cloned
    hits = []
    for p in all_files():
        try:
            txt = open(p, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        cands = []
        if p.endswith(".json"):
            _strings(json.loads(txt), cands)
        # sentences / quoted fragments in any text file (md, py, json)
        cands += re.findall(r"[\"“']([^\"”'\n]{8,300})[\"”']", txt)
        cands += [x.strip() for x in re.split(r"(?<=[.?!])\s+|\n", txt) if len(x.split()) >= 3]
        for s in cands:
            if len(s.split()) >= 3 and sv.fingerprint(s) in fps:
                hits.append("%s: verbatim source copy %r..." % (rel(p), s[:24]))
            elif sv.shingles(sv.match_tokens(s)) & shs:
                hits.append("%s: a 5-word run of source copy in %r..." % (rel(p), s[:24]))
        for u in re.findall(r"https?://[^\s'\"`\)\]<>,]+", txt):
            if sv.url_fingerprint(u) in ufps:
                hits.append("%s: protected URL present" % rel(p))
    res("protected-content", "FAIL" if hits else "PASS", "; ".join(sorted(set(hits))[:6]) or "no source copy, endpoint or social URL in the repo (%d copy fingerprints)" % len(fps))


def c_tokens():
    probs = []
    flat = set()
    for f in sorted(os.listdir(os.path.join(REPO, "tokens/00-foundation"))):
        d = J("tokens/00-foundation/" + f)

        def walk(o, path):
            if isinstance(o, dict):
                if "$value" in o:
                    flat.add(path)
                    return
                for k, v in o.items():
                    if not k.startswith("$"):
                        walk(v, (path + "." + k) if path else k)
        walk(d, "")
    cat = J("tokens/llm/token-catalog.json")
    pol = J("tokens/llm/token-policy.json")
    for k, ids in cat["categories"].items():
        for i in ids:
            if i not in flat:
                probs.append("catalog id %s not a foundation token" % i)
    if sorted(pol["rawValueRestrictions"]) != sorted(cat["categories"]):
        probs.append("token-policy categories != catalog keys")
    for th in ("light", "inverse"):
        for role, ref in J("tokens/themes/%s.json" % th)["resolve"].items():
            if ref.strip("{}") not in flat:
                probs.append("theme %s %s -> %s unresolved" % (th, role, ref))
    sem = J("tokens/10-semantic/semantic.json")["tone"]
    for th in ("light", "inverse"):
        if sorted(J("tokens/themes/%s.json" % th)["resolve"]) != sorted(sem):
            probs.append("theme %s roles != semantic roles" % th)
    comp_refs = re.findall(r"\{([a-zA-Z0-9.]+)\}", open(os.path.join(REPO, "tokens/20-component/component.json"), encoding="utf-8").read())
    roles = {"tone." + k for k in sem} | {"status.error"}
    for r in comp_refs:
        if r not in flat and r not in roles:
            probs.append("component ref {%s} unresolved" % r)
    res("token-refs", "FAIL" if probs else "PASS", "; ".join(probs[:6]) or "%d foundation tokens; themes, catalog, policy and component refs resolve" % len(flat))


def c_modes():
    sc = J("schema/pagespec.schema.json")
    probs = []
    if sc["properties"].get("mode", {}).get("enum") != ["clone", "generation"] or "mode" not in sc.get("required", []):
        probs.append("schema mode must be a required closed enum [clone, generation]")
    fam = {}
    for p in sv.example_paths(REPO):
        e = json.load(open(p, encoding="utf-8"))
        fam.setdefault(e.get("template"), set()).add(e.get("mode"))
    for tid in J("templates/templates.json")["templates"]:
        for m in ("clone", "generation"):
            if m not in fam.get(tid, set()):
                probs.append("template family %s has no mode=%s example" % (tid, m))
    res("modes", "FAIL" if probs else "PASS", "; ".join(probs) or "mode required+closed; every template family has a clone and a generation example")


def c_section_schema():
    from jsonschema import Draft7Validator
    v = Draft7Validator(J("schema/section-contract.schema.json"))
    probs = []
    for f, c in contract_files().items():
        if c["kind"] == "section":
            probs += ["%s: %s" % (f, e.message[:100]) for e in v.iter_errors(c)]
    res("section-contracts", "FAIL" if probs else "PASS", "; ".join(probs[:5]) or "every section contract validates against the closed schema/section-contract.schema.json")


def c_source_semantic(src_root):
    probs, checked = [], 0
    for f, c in contract_files().items():
        if c["kind"] != "section":
            continue
        so, se = c.get("source"), c.get("semantic")
        if not isinstance(so, dict) or not isinstance(se, dict):
            probs.append("%s: source/semantic objects missing" % c["id"])
            continue
        if se.get("id") != c["id"] or se.get("category") != c.get("category"):
            probs.append("%s: semantic {id, category} must equal the contract id/category" % c["id"])
        if so.get("id") == c["id"] or so.get("file") != c.get("implementedBy"):
            probs.append("%s: source.id must differ from the contract id and source.file == implementedBy" % c["id"])
        fp = os.path.join(src_root, so.get("file", ""))
        if not os.path.isfile(fp):
            continue
        ls = open(fp, encoding="utf-8").read().split("\n")
        a, b = (int(x) for x in so["lines"].split("-"))
        if not (1 <= a < b <= len(ls)):
            probs.append("%s: %s:%s out of range" % (c["id"], so["file"], so["lines"]))
            continue
        if not re.match(r"^\s*<%s\b" % so["tag"], ls[a - 1]) or "</%s>" % so["tag"] not in ls[b - 1]:
            probs.append("%s: <%s> not at %s:%s (source drifted)" % (c["id"], so["tag"], so["file"], so["lines"]))
        checked += 1
    status = "FAIL" if probs else ("PASS" if checked else "WARN")
    res("source-semantic", status, "; ".join(probs[:5]) or ("%d source ranges re-read from the real files (tag at start, closing tag at end)" % checked if checked else "source project absent: ranges not re-read"))


def c_retrieval():
    probs = []
    if set(sv.RETRIEVAL_INELIGIBLE) != RETRIEVAL_INELIGIBLE:
        probs.append("RETRIEVAL_INELIGIBLE differs between verify_all and semantic_validate")
    al = {e["id"]: e for e in J("tokens/llm/component-allowlist.json")["entries"]}
    for f, c in contract_files().items():
        v = c.get("retrievalEligible")
        if not isinstance(v, bool):
            probs.append("%s: retrievalEligible must be a boolean" % c["id"])
            continue
        if v is (c["id"] in RETRIEVAL_INELIGIBLE):
            probs.append("%s: retrievalEligible=%r contradicts the code pin" % (c["id"], v))
        if v is False and len(c.get("retrievalIneligibleReason", "")) < 30:
            probs.append("%s: ineligible needs a reason >= 30 chars" % c["id"])
        if sv.RUNTIME_UI_RX.search(c["id"] + " " + c.get("title", "")) and c["id"] not in RETRIEVAL_INELIGIBLE:
            probs.append("%s looks like runtime UI but is not in the retrieval pin" % c["id"])
        if al.get(c["id"], {}).get("retrievalEligible") is not v:
            probs.append("%s: allowlist retrievalEligible disagrees with the contract" % c["id"])
    res("retrieval-eligible", "FAIL" if probs else "PASS", "; ".join(probs[:5]) or "%d contracts, %d ineligible (pinned in verify_all + semantic_validate), allowlist in parity" % (len(contract_files()), len(RETRIEVAL_INELIGIBLE)))


def c_wrapper():
    import wrapper_gate as wg
    probs = ["%s %s != pinned %s" % (k, getattr(wg, k), v) for k, v in WRAPPER_THRESHOLDS.items() if getattr(wg, k) != v]
    errs, warns = wg.run(REPO)
    probs += errs
    res("wrapper-gate", "FAIL" if probs else ("WARN" if warns else "PASS"), "; ".join(probs[:5] + warns[:3]) or "measured at 1440: no HERO > 1800px, no in-flow section > 50%%; %s" % wg.summary(REPO))


def c_token_catalog():
    import build_token_catalog as btc
    probs = []
    have = J("tokens/llm/token-catalog.json")
    if have != btc.build():
        probs.append("token-catalog.json differs from what the token files derive (run extraction/build_token_catalog.py)")
    n = recount()["tokens"]
    if have.get("tokenCount") != n:
        probs.append("catalog tokenCount %s != %d leaf tokens on disk" % (have.get("tokenCount"), n))
    pol = J("tokens/llm/token-policy.json")
    for k, slot in pol["pageSpecSlots"].items():
        for cat in slot.get("categories", []):
            if cat not in have["categories"]:
                probs.append("policy slot %s category %s not in catalog" % (k, cat))
    if sorted(pol["rules"]) != sorted(r for r in sv.RULES if r.startswith("TOKEN_")):
        probs.append("token-policy rules != validator TOKEN_* rules")
    sc = J("schema/pagespec.schema.json")["definitions"]["styleTokens"]["properties"]
    if sorted(sc) != sorted(pol["pageSpecSlots"]):
        probs.append("schema styleTokens keys != token-policy pageSpecSlots")
    res("token-catalog", "FAIL" if probs else "PASS", "; ".join(probs) or "catalog == derived from token files (%d tokens); policy slots/rules match schema + validator" % n)


def c_leakage(src_root):
    import build_leakage_patterns as blp
    lp = J("schema/source-leakage-patterns.json")
    probs = ["category %s -> rule %s not in validator" % (k, v["rule"]) for k, v in lp["categories"].items() if v["rule"] not in sv.RULES]
    if os.path.isdir(os.path.join(src_root, "src")):
        if blp.build(src_root) != lp:
            probs.append("source-leakage-patterns.json differs from what the real source derives (run extraction/build_leakage_patterns.py)")
        status = "FAIL" if probs else "PASS"
    else:
        status = "FAIL" if probs else "WARN"
    c = lp["categories"]
    res("leakage-patterns", status, "; ".join(probs) or "%s; %d brand, %d partner patterns, %d copy + %d claim shingles, %d URL fingerprints" % (
        "re-derived from the source and equal" if status == "PASS" else "source absent: not re-derived", len(c["BRAND"]["patterns"]), len(c["CUSTOMER"]["patterns"]),
        len(c["COPY"]["shingleSha256"]), len(c["CLAIM"]["shingleSha256"]), len(c["URL"]["urlSha256"])))


def c_policy():
    import policy_hash
    m = J("registry.manifest.json")
    dp = m.get("designPolicy") or {}
    probs = []
    if not m.get("category"):
        probs.append("manifest.category missing")
    for k in ("ref", "policyId", "policyVersion", "commonIrVersion", "enforcementMode", "contentHash"):
        if not dp.get(k):
            probs.append("designPolicy.%s missing" % k)
    p = os.path.join(REPO, dp.get("ref", "-"))
    if not os.path.isfile(p):
        return res("design-policy", "FAIL", "; ".join(probs + ["policy file %s missing" % dp.get("ref")]))
    pol = json.load(open(p, encoding="utf-8"))
    if pol.get("policyId") != dp.get("policyId") or pol.get("policyVersion") != dp.get("policyVersion"):
        probs.append("manifest designPolicy id/version != policy file")
    if dp.get("commonIrVersion") != "0.5" or pol.get("commonIrVersion") != "0.5":
        probs.append("commonIrVersion must be 0.5")
    if dp.get("enforcementMode") != "hard-and-soft":
        probs.append("enforcementMode must be hard-and-soft")
    saas = "n0-saas-design-constraints-common"
    if pol.get("classification", {}).get("isSaaS") is False:
        if dp.get("policyId") == saas or saas not in pol.get("notBoundTo", {}):
            probs.append("a non-SaaS repo must not bind %s and must record why in notBoundTo" % saas)
        if m.get("category") != pol["classification"].get("productCategory"):
            probs.append("manifest.category != policy productCategory")
    for f in pol.get("enforcedBy", []):
        if not os.path.isfile(os.path.join(REPO, f)):
            probs.append("enforcedBy %s missing" % f)
    if not probs and dp.get("contentHash") != policy_hash.compute(REPO):
        probs.append("designPolicy.contentHash != recomputed %s" % policy_hash.compute(REPO))
    res("design-policy", "FAIL" if probs else "PASS", "; ".join(probs) or "%s bound to %s %s (common IR 0.5, hard-and-soft), not bound to %s, contentHash matches" % (
        m["category"], dp["policyId"], dp["policyVersion"], saas))


def c_adversarial():
    r = subprocess.run([sys.executable, os.path.join(REPO, "schema/tests/adversarial_test.py")], capture_output=True, text=True)
    last = [l for l in r.stdout.splitlines() if l.startswith("SUMMARY")]
    res("adversarial", "PASS" if r.returncode == 0 else "FAIL", last[0] if last else r.stderr[-300:])


def main(argv):
    src_root = os.environ.get("DESIGN_REPO_SOURCE_ROOT") or os.path.dirname(REPO)
    quick = "--quick" in argv
    if "--source-root" in argv:
        src_root = argv[argv.index("--source-root") + 1]
    print("design-repo: %s   source root: %s" % (os.path.basename(REPO), "(given)" if "--source-root" in argv else "(parent of design-repo)"))
    c_json(); c_schema(); c_semantic(); c_allowlist(); c_versions(); c_counts(); c_readme_counts(); c_entry(); c_paths()
    c_evidence(); c_citations(src_root); c_roles(); c_graph(); c_templates(src_root); c_protected(); c_tokens()
    c_modes(); c_section_schema(); c_source_semantic(src_root); c_retrieval(); c_wrapper(); c_token_catalog(); c_leakage(src_root); c_policy()
    if not quick:
        c_adversarial()
    f = [n for n, s, _ in RESULTS if s == "FAIL"]
    w = [n for n, s, _ in RESULTS if s == "WARN"]
    print("\nRESULT: %s  (%d checks, %d FAIL, %d WARN)" % ("FAIL" if f else "PASS", len(RESULTS), len(f), len(w)))
    return 1 if f else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
