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
    errs = list(Draft7Validator(s).iter_errors(J("schema/example.pagespec.json")))
    res("schema-draft7", "FAIL" if errs else "PASS", "example: %d Draft-07 error(s)" % len(errs))


def c_semantic():
    errs, warns = sv.validate(J("schema/example.pagespec.json"))
    res("semantic-example", "FAIL" if errs else "PASS", "example: %d error(s), %d warning(s)" % (len(errs), len(warns)))


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
    if not (sorted(enum) == sorted(al["assetRoles"]) == sorted(roles["roles"].keys())):
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
    ex = J("schema/example.pagespec.json")["pageSpecVersion"]
    ok = m["pageSpecVersion"] == sc == ex
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
            "copyFingerprints": len(J("schema/protected-content.json")["copyFingerprints"]["sha256"])}


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
    for r, d in roles["roles"].items():
        if d["generationPolicy"] not in pol:
            probs.append("%s: policy %s not in closed set" % (r, d["generationPolicy"]))
        if d.get("reuseOfSourceFiles") != "forbidden":
            probs.append("%s: reuseOfSourceFiles must be 'forbidden' (real company assets)" % r)
    for r, want in PINNED.items():
        got = roles["roles"].get(r, {}).get("generationPolicy")
        if got != want:
            probs.append("PINNED %s must be %s, got %s" % (r, want, got))
    if roles.get("pinnedPolicies") != PINNED:
        probs.append("asset-roles.pinnedPolicies disagrees with verify_all PINNED")
    res("asset-roles", "FAIL" if probs else "PASS", "; ".join(probs) or "%d roles, %d pinned policies hold" % (len(roles["roles"]), len(PINNED)))


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
    if not quick:
        c_adversarial()
    f = [n for n, s, _ in RESULTS if s == "FAIL"]
    w = [n for n, s, _ in RESULTS if s == "WARN"]
    print("\nRESULT: %s  (%d checks, %d FAIL, %d WARN)" % ("FAIL" if f else "PASS", len(RESULTS), len(f), len(w)))
    return 1 if f else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
