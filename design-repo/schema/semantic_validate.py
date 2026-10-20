#!/usr/bin/env python3
"""Semantic validator for PageSpecs built against this design-repo.

JSON Schema (pagespec.schema.json) checks shape. This script checks everything
the schema cannot express, and every check is a named rule that also appears in
compatibility/graph.json with a severity ("error" fails, "warn" reports).
extraction/verify_all.py fails if the graph's rule ids and RULES below drift.

What it enforces (see graph.json for the prose of each rule):
  * the declared template's REAL node list: order, required/optional nodes,
    repeatability, allowed variants, anchor ids (not nodes[] in isolation)
  * the route belongs to the declared template
  * tone: each node's tone matches its template node, and the page has exactly
    one light -> inverse handoff, at transition.light-to-dark (no light main
    section after it)
  * Handoff wrapping: only where the template observed it, same tone as the
    section, and only when another <main> section follows to scroll over it
  * cross-section scroll-trigger dependency (Send reads #send-scroll-trigger,
    which lives in the Logo section)
  * motion: each node's motion block equals its section contract exactly, and
    the reducedMotionFallback is the pinned value
  * copy budgets (chars / words / line items / list counts) from the section
    contracts, which were measured from the real layout
  * media: assetRole allowed for the slot; assetRef must not reuse a source file
  * real-company protection: no verbatim source copy (sha256 fingerprints, the
    repo never stores the text), no source brand name, no source endpoint or
    social profile URLs, a project-supplied https waitlist endpoint
  * internal "/#anchor" links resolve to a node present on the page

Usage:  python3 schema/semantic_validate.py [pagespec.json ...]
        (defaults to schema/example.pagespec.json). Exit 1 on any error.
"""
import hashlib
import json
import os
import re
import sys
import unicodedata

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --------------------------------------------------------------------------
# helpers shared with the build (fingerprints are produced with these exact
# functions, so normalisation can never drift between build and check)
# --------------------------------------------------------------------------
_QUOTES = {"‘": "'", "’": "'", "“": '"', "”": '"', " ": " "}


def normalize_copy(s):
    s = unicodedata.normalize("NFKC", s)
    for k, v in _QUOTES.items():
        s = s.replace(k, v)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s.rstrip(".?!")


def fingerprint(s):
    return hashlib.sha256(normalize_copy(s).encode("utf-8")).hexdigest()


def normalize_url(u):
    return u.strip().lower().rstrip("/")


def url_fingerprint(u):
    return hashlib.sha256(normalize_url(u).encode("utf-8")).hexdigest()


def word_count(s):
    return len(s.split())


def load_json(rel, repo=REPO):
    with open(os.path.join(repo, rel), encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------
# rule registry
# --------------------------------------------------------------------------
RULES = {}


def rule(rule_id):
    def deco(fn):
        RULES[rule_id] = fn
        return fn
    return deco


class Ctx:
    def __init__(self, repo):
        self.repo = repo
        self.graph = load_json("compatibility/graph.json", repo)
        self.severity = {r["id"]: r["severity"] for r in self.graph["rules"]}
        self.templates = load_json("templates/templates.json", repo)["templates"]
        self.routes = load_json("templates/routes.json", repo)
        self.roles = load_json("assets/asset-roles.json", repo)
        self.protected = load_json("schema/protected-content.json", repo)
        self.sections = {}
        sdir = os.path.join(repo, "sections")
        for fn in sorted(os.listdir(sdir)):
            if fn.endswith(".json"):
                c = load_json(os.path.join("sections", fn), repo)
                self.sections[c["id"]] = c
        self.errors = []
        self.warnings = []

    def report(self, rule_id, where, msg):
        sev = self.severity.get(rule_id, "error")
        item = {"rule": rule_id, "severity": sev, "path": where, "message": msg}
        (self.errors if sev == "error" else self.warnings).append(item)


# ------------------------------- structure --------------------------------
def _template(ctx, spec):
    return ctx.templates.get(spec.get("template"))


@rule("ROUTE_MATCHES_TEMPLATE")
def r_route(ctx, spec):
    t = _template(ctx, spec)
    if t is None:
        ctx.report("ROUTE_MATCHES_TEMPLATE", "template", "unknown template %r" % spec.get("template"))
        return
    if spec.get("route") not in t["routes"]:
        ctx.report("ROUTE_MATCHES_TEMPLATE", "route",
                   "route %r is not a route of %s (allowed: %s)" % (spec.get("route"), t["id"], t["routes"]))


def _node_index(t):
    return {n["section"]: i for i, n in enumerate(t["nodes"])}


@rule("TEMPLATE_UNKNOWN_NODE")
def r_unknown(ctx, spec):
    t = _template(ctx, spec)
    if not t:
        return
    idx = _node_index(t)
    for i, n in enumerate(spec.get("nodes", [])):
        if n.get("section") not in idx:
            ctx.report("TEMPLATE_UNKNOWN_NODE", "nodes[%d]" % i,
                       "section %r is not a node of template %s" % (n.get("section"), t["id"]))


@rule("NO_REPEAT")
def r_repeat(ctx, spec):
    t = _template(ctx, spec)
    if not t:
        return
    rep = {n["section"]: n["repeatable"] for n in t["nodes"]}
    seen = {}
    for i, n in enumerate(spec.get("nodes", [])):
        key = (n.get("section"), n.get("variant"))
        s = n.get("section")
        if s in seen and not rep.get(s, False):
            ctx.report("NO_REPEAT", "nodes[%d]" % i,
                       "section %r (variant %r) repeats nodes[%d]; template marks it non-repeatable" % (s, key[1], seen[s]))
        seen.setdefault(s, i)


@rule("TEMPLATE_NODE_ORDER")
def r_order(ctx, spec):
    t = _template(ctx, spec)
    if not t:
        return
    idx = _node_index(t)
    last = -1
    for i, n in enumerate(spec.get("nodes", [])):
        j = idx.get(n.get("section"))
        if j is None:
            continue
        if j < last:
            ctx.report("TEMPLATE_NODE_ORDER", "nodes[%d]" % i,
                       "section %r is out of the template's order (template position %d after %d)" % (n.get("section"), j, last))
        last = max(last, j)


@rule("TEMPLATE_REQUIRED_NODES")
def r_required(ctx, spec):
    t = _template(ctx, spec)
    if not t:
        return
    present = {n.get("section") for n in spec.get("nodes", [])}
    for tn in t["nodes"]:
        if tn["required"] and tn["section"] not in present:
            ctx.report("TEMPLATE_REQUIRED_NODES", "nodes", "required node %r of %s is missing" % (tn["section"], t["id"]))


@rule("OPTIONAL_NODE_OMITTED")
def r_optional(ctx, spec):
    t = _template(ctx, spec)
    if not t:
        return
    present = {n.get("section") for n in spec.get("nodes", [])}
    for tn in t["nodes"]:
        if not tn["required"] and tn["section"] not in present:
            ctx.report("OPTIONAL_NODE_OMITTED", "nodes",
                       "optional node %r omitted: valid, but the only measured composition contains it, so this rhythm is unmeasured" % tn["section"])


@rule("VARIANT_ALLOWED")
def r_variant(ctx, spec):
    t = _template(ctx, spec)
    if not t:
        return
    tn = {n["section"]: n for n in t["nodes"]}
    for i, n in enumerate(spec.get("nodes", [])):
        x = tn.get(n.get("section"))
        if x and n.get("variant") not in x["allowedVariants"]:
            ctx.report("VARIANT_ALLOWED", "nodes[%d].variant" % i,
                       "variant %r not allowed for %s in %s (allowed %s)" % (n.get("variant"), n.get("section"), t["id"], x["allowedVariants"]))


@rule("ANCHOR_ID_MATCH")
def r_anchor(ctx, spec):
    t = _template(ctx, spec)
    if not t:
        return
    tn = {n["section"]: n for n in t["nodes"]}
    for i, n in enumerate(spec.get("nodes", [])):
        x = tn.get(n.get("section"))
        if x and n.get("anchorId") != x["anchorId"]:
            ctx.report("ANCHOR_ID_MATCH", "nodes[%d].anchorId" % i,
                       "anchorId %r must be %r for %s" % (n.get("anchorId"), x["anchorId"], n.get("section")))


# --------------------------------- tone -----------------------------------
@rule("TONE_MATCHES_TEMPLATE")
def r_tone_template(ctx, spec):
    t = _template(ctx, spec)
    if not t:
        return
    tn = {n["section"]: n for n in t["nodes"]}
    for i, n in enumerate(spec.get("nodes", [])):
        x = tn.get(n.get("section"))
        if x and n.get("tone") != x["tone"]:
            ctx.report("TONE_MATCHES_TEMPLATE", "nodes[%d].tone" % i,
                       "%s is %r in the template, got %r" % (n.get("section"), x["tone"], n.get("tone")))


@rule("TONE_SEQUENCE")
def r_tone_sequence(ctx, spec):
    nodes = spec.get("nodes", [])
    t = _template(ctx, spec)
    if not t:
        return
    region = {n["section"]: n["region"] for n in t["nodes"]}
    trans = ctx.graph["toneModel"]["handoffSection"]
    tidx = [i for i, n in enumerate(nodes) if n.get("section") == trans]
    if not tidx:
        ctx.report("TONE_SEQUENCE", "nodes", "no %s node: the light->inverse handoff has nowhere to happen" % trans)
        return
    k = tidx[0]
    for i, n in enumerate(nodes):
        reg = region.get(n.get("section"))
        tone = n.get("tone")
        if reg == "header" and tone != "light":
            ctx.report("TONE_SEQUENCE", "nodes[%d].tone" % i, "header must be light (it sits over the light hero)")
        elif reg == "footer" and tone != "inverse":
            ctx.report("TONE_SEQUENCE", "nodes[%d].tone" % i, "footer must be inverse (it follows the inverse run)")
        elif reg == "main":
            if i <= k and tone != "light":
                ctx.report("TONE_SEQUENCE", "nodes[%d].tone" % i,
                           "%s is before/at the dark transition and must be light" % n.get("section"))
            if i > k and tone != "inverse":
                ctx.report("TONE_SEQUENCE", "nodes[%d].tone" % i,
                           "light section %s after the dark transition: the page may only go light->inverse once" % n.get("section"))


# -------------------------------- handoff ---------------------------------
@rule("HANDOFF_ALLOWED_VALUE")
def r_handoff_allowed(ctx, spec):
    t = _template(ctx, spec)
    if not t:
        return
    tn = {n["section"]: n for n in t["nodes"]}
    for i, n in enumerate(spec.get("nodes", [])):
        x = tn.get(n.get("section"))
        if x and n.get("handoff") not in x["handoffAllowed"]:
            ctx.report("HANDOFF_ALLOWED_VALUE", "nodes[%d].handoff" % i,
                       "handoff %r not allowed on %s (allowed %s)" % (n.get("handoff"), n.get("section"), x["handoffAllowed"]))


@rule("HANDOFF_TONE_MATCH")
def r_handoff_tone(ctx, spec):
    for i, n in enumerate(spec.get("nodes", [])):
        h = n.get("handoff")
        if h is not None and h != n.get("tone"):
            ctx.report("HANDOFF_TONE_MATCH", "nodes[%d].handoff" % i,
                       "Handoff tone %r must equal the wrapped section's tone %r (overlay .12 light / .6 inverse)" % (h, n.get("tone")))


@rule("HANDOFF_NEEDS_MAIN_FOLLOWER")
def r_handoff_follower(ctx, spec):
    t = _template(ctx, spec)
    if not t:
        return
    region = {n["section"]: n["region"] for n in t["nodes"]}
    nodes = spec.get("nodes", [])
    for i, n in enumerate(nodes):
        if n.get("handoff") is None:
            continue
        if region.get(n.get("section")) != "main":
            ctx.report("HANDOFF_NEEDS_MAIN_FOLLOWER", "nodes[%d].handoff" % i, "Handoff only wraps sections inside <main>")
            continue
        nxt = nodes[i + 1] if i + 1 < len(nodes) else None
        if nxt is None or region.get(nxt.get("section")) != "main":
            ctx.report("HANDOFF_NEEDS_MAIN_FOLLOWER", "nodes[%d].handoff" % i,
                       "%s is Handoff-wrapped but no <main> section follows to scroll over it" % n.get("section"))


# ----------------------------- dependencies -------------------------------
@rule("SEND_REQUIRES_LOGO_TRIGGER")
def r_send_logo(ctx, spec):
    dep = ctx.graph["dependencies"]["SEND_REQUIRES_LOGO_TRIGGER"]
    secs = [n.get("section") for n in spec.get("nodes", [])]
    if dep["dependent"] in secs:
        i = secs.index(dep["dependent"])
        if i == 0 or secs[i - 1] != dep["host"]:
            ctx.report("SEND_REQUIRES_LOGO_TRIGGER", "nodes[%d]" % i,
                       "%s reads #%s, which lives in %s; that section must directly precede it" % (dep["dependent"], dep["triggerId"], dep["host"]))


# -------------------------------- motion ----------------------------------
def _close(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) < 1e-9
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_close(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_close(x, y) for x, y in zip(a, b))
    return a == b


@rule("REDUCED_MOTION_FALLBACK_PINNED")
def r_rm(ctx, spec):
    for i, n in enumerate(spec.get("nodes", [])):
        c = ctx.sections.get(n.get("section"))
        m = n.get("motion") or {}
        if c and m.get("reducedMotionFallback") != c["motion"]["reducedMotionFallback"]:
            ctx.report("REDUCED_MOTION_FALLBACK_PINNED", "nodes[%d].motion.reducedMotionFallback" % i,
                       "must be %r" % c["motion"]["reducedMotionFallback"])


@rule("MOTION_MATCHES_CONTRACT")
def r_motion(ctx, spec):
    for i, n in enumerate(spec.get("nodes", [])):
        c = ctx.sections.get(n.get("section"))
        m = n.get("motion")
        if not c or not isinstance(m, dict):
            continue
        want = c["motion"]
        for k in sorted(set(want) | set(m)):
            if k == "reducedMotionFallback":
                continue
            if k not in m:
                ctx.report("MOTION_MATCHES_CONTRACT", "nodes[%d].motion.%s" % (i, k), "missing (contract declares it)")
            elif k not in want:
                ctx.report("MOTION_MATCHES_CONTRACT", "nodes[%d].motion.%s" % (i, k), "not part of this section's motion contract")
            elif not _close(m[k], want[k]):
                ctx.report("MOTION_MATCHES_CONTRACT", "nodes[%d].motion.%s" % (i, k),
                           "differs from the evidence-grounded contract value")


# ------------------------------ copy + media ------------------------------
def _walk(fields, value, path, out, parent_index=None):
    """Yield (path, spec, value) for every leaf field per the section content model."""
    for name, fs in fields.items():
        if name not in value:
            continue
        v = value[name]
        p = "%s.%s" % (path, name)
        t = fs["type"]
        if t == "object":
            out.append((p, fs, v, parent_index))
            if isinstance(v, dict):
                _walk(fs["fields"], v, p, out, parent_index)
            continue
        if t == "list":
            out.append((p, fs, v, parent_index))
            if isinstance(v, list):
                for k, item in enumerate(v):
                    ip = "%s[%d]" % (p, k)
                    if "type" in fs["item"]:  # list of a single field (e.g. links)
                        out.append((ip, fs["item"], item, k))
                    elif isinstance(item, dict):
                        _walk(fs["item"], item, ip, out, k)
        else:
            out.append((p, fs, v, parent_index))


def _leaves(ctx, spec):
    out = []
    for i, n in enumerate(spec.get("nodes", [])):
        c = ctx.sections.get(n.get("section"))
        if c and isinstance(n.get("content"), dict):
            _walk(c["content"], n["content"], "nodes[%d].content" % i, out)
    meta_fields = load_json("schema/page-meta.contract.json", ctx.repo)["content"]
    if isinstance(spec.get("meta"), dict):
        _walk(meta_fields, spec["meta"], "meta", out)
    return out


def _check_text(ctx, p, budget, s):
    if not isinstance(s, str):
        return
    if len(s) > budget["maxChars"]:
        ctx.report("COPY_BUDGET", p, "%d chars > budget %d" % (len(s), budget["maxChars"]))
    if word_count(s) > budget["maxWords"]:
        ctx.report("COPY_BUDGET", p, "%d words > budget %d" % (word_count(s), budget["maxWords"]))


@rule("COPY_BUDGET")
def r_copy(ctx, spec):
    for p, fs, v, pidx in _leaves(ctx, spec):
        t = fs["type"]
        if t == "text":
            _check_text(ctx, p, fs, v)
        elif t == "lines" and isinstance(v, list):
            if len(v) != fs["count"]:
                ctx.report("COPY_BUDGET", p, "%d explicit lines, contract pins %d" % (len(v), fs["count"]))
            for k, s in enumerate(v):
                _check_text(ctx, "%s[%d]" % (p, k), {"maxChars": fs["maxCharsPerLine"], "maxWords": fs["maxWordsPerLine"]}, s)
        elif t == "paragraphs" and isinstance(v, list):
            if not fs["minItems"] <= len(v) <= fs["maxItems"]:
                ctx.report("COPY_BUDGET", p, "%d paragraphs, contract allows %d-%d" % (len(v), fs["minItems"], fs["maxItems"]))
            for k, s in enumerate(v):
                _check_text(ctx, "%s[%d]" % (p, k), fs, s)
        elif t == "link" and isinstance(v, dict):
            _check_text(ctx, p + ".label", fs["label"], v.get("label"))
        elif t == "list" and isinstance(v, list):
            want = fs.get("count")
            if fs.get("countByParentIndex") is not None and pidx is not None:
                want = fs["countByParentIndex"][pidx] if pidx < len(fs["countByParentIndex"]) else None
            if want is not None and len(v) != want:
                ctx.report("COPY_BUDGET", p, "%d items, the measured layout has exactly %d" % (len(v), want))
        elif t == "media" and isinstance(v, dict) and fs["alt"] != "decorative":
            _check_text(ctx, p + ".alt", fs["alt"], v.get("alt"))


@rule("ASSET_ROLE_ALLOWED_FOR_SLOT")
def r_asset_role(ctx, spec):
    known = set(ctx.roles["roles"].keys())
    for p, fs, v, _ in _leaves(ctx, spec):
        if fs["type"] != "media" or not isinstance(v, dict):
            continue
        role = v.get("assetRole")
        if role not in known:
            ctx.report("ASSET_ROLE_ALLOWED_FOR_SLOT", p + ".assetRole", "unknown assetRole %r" % role)
        elif role not in fs["roles"]:
            ctx.report("ASSET_ROLE_ALLOWED_FOR_SLOT", p + ".assetRole",
                       "assetRole %r not allowed in this slot (allowed %s)" % (role, fs["roles"]))


@rule("ASSET_REF_NOT_SOURCE_FILE")
def r_asset_ref(ctx, spec):
    banned = set()
    for r in ctx.roles["roles"].values():
        banned.update(os.path.basename(f).lower() for f in r["sourceFiles"])
    for p, fs, v, _ in _leaves(ctx, spec):
        if fs["type"] == "media" and isinstance(v, dict) and isinstance(v.get("assetRef"), str):
            if os.path.basename(v["assetRef"]).lower() in banned:
                ctx.report("ASSET_REF_NOT_SOURCE_FILE", p + ".assetRef",
                           "%r is a file from the source site; supply an original/licensed asset" % v["assetRef"])


# --------------------------- real-company protection ----------------------
def _all_strings(ctx, spec):
    out = []
    for p, fs, v, _ in _leaves(ctx, spec):
        t = fs["type"]
        if t == "text" and isinstance(v, str):
            out.append((p, v))
        elif t in ("lines", "paragraphs") and isinstance(v, list):
            out += [("%s[%d]" % (p, k), s) for k, s in enumerate(v) if isinstance(s, str)]
        elif t == "link" and isinstance(v, dict):
            out += [(p + "." + k, v[k]) for k in ("label", "href") if isinstance(v.get(k), str)]
        elif t == "media" and isinstance(v, dict):
            out += [(p + "." + k, v[k]) for k in ("alt", "assetRef") if isinstance(v.get(k), str)]
    brand = spec.get("brand") or {}
    if isinstance(brand.get("name"), str):
        out.append(("brand.name", brand["name"]))
    return out


@rule("NO_VERBATIM_SOURCE_COPY")
def r_verbatim(ctx, spec):
    fps = set(ctx.protected["copyFingerprints"]["sha256"])
    for p, s in _all_strings(ctx, spec):
        if fingerprint(s) in fps:
            ctx.report("NO_VERBATIM_SOURCE_COPY", p, "verbatim copy from the source site (fingerprint match); write original copy")


@rule("NO_SOURCE_BRAND_NAME")
def r_brand(ctx, spec):
    toks = ctx.protected["brandTokens"]
    everywhere = [re.compile(r"\b%s\b" % re.escape(t), re.I) for t in toks["everywhere"]]
    partner = [re.compile(r"\b%s\b" % re.escape(t), re.I) for t in toks["partnerSlots"]]
    for p, s in _all_strings(ctx, spec):
        for rx in everywhere:
            if rx.search(s):
                ctx.report("NO_SOURCE_BRAND_NAME", p, "contains the source company's brand token %r" % rx.pattern)
    for p, fs, v, _ in _leaves(ctx, spec):
        if fs["type"] == "media" and "partner.logo" in fs["roles"] and isinstance(v, dict):
            for k in ("alt", "assetRef"):
                for rx in partner:
                    if isinstance(v.get(k), str) and rx.search(v[k]):
                        ctx.report("NO_SOURCE_BRAND_NAME", "%s.%s" % (p, k),
                                   "names a real partner company; partner logos must be fictional placeholders")


@rule("EXTERNAL_LINK_NOT_PROTECTED")
def r_external(ctx, spec):
    fps = set(ctx.protected["urlFingerprints"]["social"])
    for p, fs, v, _ in _leaves(ctx, spec):
        if fs["type"] == "link" and isinstance(v, dict) and isinstance(v.get("href"), str):
            h = v["href"]
            if h.startswith("http") and url_fingerprint(h) in fps:
                ctx.report("EXTERNAL_LINK_NOT_PROTECTED", p + ".href",
                           "this is the source company's real social profile; external links are instance data and must be the project's own")
            if h.startswith("http://"):
                ctx.report("EXTERNAL_LINK_NOT_PROTECTED", p + ".href", "external links must be https")


@rule("WAITLIST_ENDPOINT_PROJECT_SUPPLIED")
def r_endpoint(ctx, spec):
    present = {n.get("section") for n in spec.get("nodes", [])}
    if "hero.waitlist-hero" not in present:
        return
    ep = (spec.get("config") or {}).get("waitlistEndpoint")
    if not isinstance(ep, str) or not ep:
        ctx.report("WAITLIST_ENDPOINT_PROJECT_SUPPLIED", "config.waitlistEndpoint", "required: the waitlist form posts {email} here")
        return
    if not ep.startswith("https://"):
        ctx.report("WAITLIST_ENDPOINT_PROJECT_SUPPLIED", "config.waitlistEndpoint", "must be an https URL")
    if url_fingerprint(ep) in set(ctx.protected["urlFingerprints"]["waitlistEndpoint"]):
        ctx.report("WAITLIST_ENDPOINT_PROJECT_SUPPLIED", "config.waitlistEndpoint",
                   "this is the source company's live form endpoint; supply the project's own")


@rule("INTERNAL_ANCHOR_RESOLVES")
def r_anchors(ctx, spec):
    ids = {n.get("anchorId") for n in spec.get("nodes", []) if n.get("anchorId")}
    for p, fs, v, _ in _leaves(ctx, spec):
        if fs["type"] == "link" and isinstance(v, dict) and isinstance(v.get("href"), str):
            h = v["href"]
            m = re.match(r"^/?#([A-Za-z0-9_-]+)$", h)
            if m and m.group(1) not in ids:
                ctx.report("INTERNAL_ANCHOR_RESOLVES", p + ".href", "anchor #%s is not on this page" % m.group(1))


# --------------------------------------------------------------------------
def schema_errors(spec, repo=REPO):
    from jsonschema import Draft7Validator
    schema = load_json("schema/pagespec.schema.json", repo)
    v = Draft7Validator(schema)
    return [{"rule": "SCHEMA", "severity": "error", "path": "/".join(str(x) for x in e.absolute_path) or "(root)",
             "message": e.message[:300]} for e in sorted(v.iter_errors(spec), key=lambda e: list(e.absolute_path))]


def validate(spec, repo=REPO, with_schema=True):
    """Return (errors, warnings). Schema errors are reported as rule SCHEMA."""
    ctx = Ctx(repo)
    errors = schema_errors(spec, repo) if with_schema else []
    if not isinstance(spec, dict) or not isinstance(spec.get("nodes"), list):
        return errors + [{"rule": "SCHEMA", "severity": "error", "path": "nodes", "message": "nodes[] missing"}], []
    for rid, fn in RULES.items():
        try:
            fn(ctx, spec)
        except Exception as exc:  # malformed input that the schema already flagged
            ctx.report(rid, "(internal)", "could not evaluate: %s" % exc)
    return errors + ctx.errors, ctx.warnings


def main(argv):
    paths = argv[1:] or [os.path.join(REPO, "schema", "example.pagespec.json")]
    bad = 0
    for p in paths:
        with open(p, encoding="utf-8") as f:
            spec = json.load(f)
        errs, warns = validate(spec)
        print("%s: %d error(s), %d warning(s)" % (os.path.basename(p), len(errs), len(warns)))
        for e in errs:
            print("  ERROR [%s] %s: %s" % (e["rule"], e["path"], e["message"]))
        for w in warns:
            print("  warn  [%s] %s: %s" % (w["rule"], w["path"], w["message"]))
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
