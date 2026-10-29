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
    one light -> inverse handoff, at transition.light-to-dark
  * Handoff wrapping: only where the template observed it, same tone as the
    section, and only when another <main> section follows to scroll over it
  * cross-section scroll-trigger dependency (Send reads #send-scroll-trigger,
    which lives in the Logo section)
  * motion: each node's motion block equals its section contract exactly, and
    the reducedMotionFallback is the pinned value
  * copy budgets (chars / words / line items / list counts), measured
  * media: assetRole allowed for the slot
  * MODE (required, closed): clone | generation.
      clone      = private faithful reconstruction: real brand, copy, assets,
                   partner names and social URLs may be reused for fidelity.
      generation = a page for another brand: GENERATION_MODE_BRAND / _CUSTOMER /
                   _PERSON / _SCREENSHOT / _ASSET / _COPY / _CLAIM / _URL reject
                   every source identity/content category. Patterns come from
                   schema/source-leakage-patterns.json (derived from the real
                   source by extraction/build_leakage_patterns.py) and asset
                   availability is PINNED below (PINNED_AVAILABILITY).
    Both modes: the live waitlist endpoint is never allowed (the clone itself
    replaced it with a no-op), external links are https.
  * retrieval eligibility (RETRIEVAL_INELIGIBLE pin + node/contract parity)
  * token choices in nodes[].styleTokens against tokens/llm/token-catalog.json
    and token-policy.json (TOKEN_UNKNOWN / _RAW_VALUE / _ARBITRARY_SPACING /
    _UNSUPPORTED_FONT / _THEME_MISMATCH)
  * internal "/#anchor" links resolve to a node present on the page

Detection is string-based (normalised exact matches, hashed 5-word shingles):
a paraphrase is not caught. No human has reviewed the pinned patterns.

Usage:  python3 schema/semantic_validate.py [pagespec.json ...]
        (defaults to schema/examples/*.pagespec.json). Exit 1 on any error.
"""
import glob
import hashlib
import json
import os
import re
import sys
import unicodedata

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --------------------------------------------------------------------------
# PINS (independent of the registries: editing a JSON file alone cannot loosen
# them; extraction/verify_all.py cross-checks these against the registries and
# against its own copy).
# --------------------------------------------------------------------------
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
# which GENERATION_MODE_* rule a non-generation-safe role (or its source file) violates
PINNED_LEAK_CATEGORY = {
    "brand.mark": "BRAND", "brand.wordmark": "BRAND",
    "partner.logo": "CUSTOMER",
    "photo.portrait": "PERSON", "photo.portrait-ascii": "PERSON", "photo.reflection": "PERSON",
    "device.screen": "SCREENSHOT", "device.screen-reflection": "SCREENSHOT", "nav.card-image": "SCREENSHOT",
    "photo.product-in-hand": "SCREENSHOT", "social.og-image": "SCREENSHOT",
    "nav.ring": "ASSET", "texture.backdrop": "ASSET", "photo.lifestyle": "ASSET",
}
# runtime/utility UI that must never be retrieved as page content (R8)
RETRIEVAL_INELIGIBLE = {
    "component.nav-menu-panel": "Runtime overlay UI: the mega-menu drawer/panel and its page overlay only exist while a menu is open; it is navigation chrome, not page content to retrieve.",
    "component.smooth-scroll": "Runtime scroll utility (Lenis smooth scrolling) with no visual output of its own; nothing to retrieve or compose as content.",
}
RUNTIME_UI_RX = re.compile(r"cookie|consent|modal|dialog|drawer|popup|pop-up|overlay|preloader|loader|toast|cursor|menu-panel|smooth-scroll", re.I)
PLACEHOLDER_HOST_RX = re.compile(r"(^|\.)[a-z0-9-]+\.(example|invalid)$|^(example|invalid)$")
MODES = ("clone", "generation")
SHINGLE = 5

# --------------------------------------------------------------------------
# helpers shared with the build (fingerprints are produced with these exact
# functions, so normalisation can never drift between build and check)
# --------------------------------------------------------------------------
_QUOTES = {"‘": "'", "’": "'", "“": '"', "”": '"', " ": " "}
_ZERO_WIDTH = re.compile("[​‌‍⁠﻿­]")
_DASHES = re.compile("[‐‑‒–—―−]")


def normalize_copy(s):
    """Legacy full-string normaliser (schema/protected-content.json fingerprints)."""
    s = unicodedata.normalize("NFKC", s)
    for k, v in _QUOTES.items():
        s = s.replace(k, v)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s.rstrip(".?!")


def fingerprint(s):
    return hashlib.sha256(normalize_copy(_ZERO_WIDTH.sub("", s)).encode("utf-8")).hexdigest()


def normalize_match(s):
    """Matching normaliser: NFKC, zero-width removal, quotes, dashes, whitespace, case."""
    s = _ZERO_WIDTH.sub("", unicodedata.normalize("NFKC", s))
    for k, v in _QUOTES.items():
        s = s.replace(k, v)
    s = _DASHES.sub("-", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def normalize_case_kept(s):
    s = _ZERO_WIDTH.sub("", unicodedata.normalize("NFKC", s))
    for k, v in _QUOTES.items():
        s = s.replace(k, v)
    return re.sub(r"\s+", " ", _DASHES.sub("-", s)).strip()


def match_tokens(s):
    return re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)*", normalize_match(s))


def _h(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def shingles(tokens, n=SHINGLE):
    return {_h(" ".join(tokens[i:i + n])) for i in range(len(tokens) - n + 1)} if len(tokens) >= n else set()


def phrase_hash(tokens):
    return _h(" ".join(tokens))


def normalize_url(u):
    return u.strip().lower().rstrip("/")


def url_fingerprint(u):
    return hashlib.sha256(normalize_url(u).encode("utf-8")).hexdigest()


def url_host(u):
    h = re.sub(r"^[a-z][a-z0-9+.-]*://", "", normalize_match(u)).split("/")[0].split("?")[0].split("#")[0]
    return re.sub(r"^www\.", "", h.split("@")[-1].split(":")[0])


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
        self.leak = load_json("schema/source-leakage-patterns.json", repo)
        self.catalog = load_json("tokens/llm/token-catalog.json", repo)
        self.token_policy = load_json("tokens/llm/token-policy.json", repo)
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


def _mode(spec):
    """Fail closed: anything that is not exactly 'clone' is checked as generation."""
    return "clone" if spec.get("mode") == "clone" else "generation"


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




# ------------------------------ retrieval (R8) -----------------------------
@rule("RETRIEVAL_ELIGIBILITY_MATCH")
def r_retrieval(ctx, spec):
    for i, n in enumerate(spec.get("nodes", [])):
        c = ctx.sections.get(n.get("section"))
        if not c:
            continue
        want = n.get("section") not in RETRIEVAL_INELIGIBLE
        if c.get("retrievalEligible") is not want:
            ctx.report("RETRIEVAL_ELIGIBILITY_MATCH", "nodes[%d]" % i,
                       "section contract %s says retrievalEligible=%r but the code pin says %r" % (n.get("section"), c.get("retrievalEligible"), want))
        if "retrievalEligible" in n and n["retrievalEligible"] is not want:
            ctx.report("RETRIEVAL_ELIGIBILITY_MATCH", "nodes[%d].retrievalEligible" % i,
                       "%s is %s; a PageSpec may not change retrieval eligibility" % (n.get("section"), "retrieval-eligible content" if want else "runtime UI"))


# ------------------------------ tokens (R10) -------------------------------
_RAW_COLOR = re.compile(r"^#[0-9a-f]{3,8}$|^(rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch|color)\(|^(white|black|red|blue|green|transparent|currentcolor)$", re.I)
_RAW_DIM = re.compile(r"^-?\d+(\.\d+)?\s*(px|rem|em|%|vh|vw|svh|dvh|pt)?$", re.I)


def _all_catalog_ids(cat):
    out = set()
    for layer in cat["layers"].values():
        for ids in layer.values():
            out.update(ids)
    return out


@rule("TOKEN_RAW_VALUE")
def r_tok_raw(ctx, spec):
    slots = ctx.token_policy["pageSpecSlots"]
    for i, n in enumerate(spec.get("nodes", [])):
        for k, v in (n.get("styleTokens") or {}).items():
            if not isinstance(v, str):
                continue
            if _RAW_COLOR.search(v.strip()) or (_RAW_DIM.match(v.strip()) and slots.get(k, {}).get("kind") != "spacing"):
                ctx.report("TOKEN_RAW_VALUE", "nodes[%d].styleTokens.%s" % (i, k), "raw value %r: use a token id from tokens/llm/token-catalog.json" % v)


@rule("TOKEN_ARBITRARY_SPACING")
def r_tok_spacing(ctx, spec):
    slots = ctx.token_policy["pageSpecSlots"]
    scale = ctx.catalog["spacingScalePx"]
    for i, n in enumerate(spec.get("nodes", [])):
        for k, v in (n.get("styleTokens") or {}).items():
            if slots.get(k, {}).get("kind") == "spacing" and isinstance(v, str) and v not in scale:
                ctx.report("TOKEN_ARBITRARY_SPACING", "nodes[%d].styleTokens.%s" % (i, k),
                           "%r is not on the measured spacing scale (%s)" % (v, ", ".join(scale)))


@rule("TOKEN_UNSUPPORTED_FONT")
def r_tok_font(ctx, spec):
    slots = ctx.token_policy["pageSpecSlots"]
    fonts = ctx.catalog["supportedFonts"]
    for i, n in enumerate(spec.get("nodes", [])):
        for k, v in (n.get("styleTokens") or {}).items():
            if slots.get(k, {}).get("kind") == "font" and isinstance(v, str) and v not in fonts:
                ctx.report("TOKEN_UNSUPPORTED_FONT", "nodes[%d].styleTokens.%s" % (i, k),
                           "%r is not a supported font token (supported: %s)" % (v, ", ".join(fonts)))


@rule("TOKEN_UNKNOWN")
def r_tok_unknown(ctx, spec):
    slots = ctx.token_policy["pageSpecSlots"]
    ids = _all_catalog_ids(ctx.catalog)
    for i, n in enumerate(spec.get("nodes", [])):
        for k, v in (n.get("styleTokens") or {}).items():
            s = slots.get(k)
            if s is None or not isinstance(v, str) or s["kind"] in ("spacing", "font"):
                continue
            if _RAW_COLOR.search(v.strip()) or _RAW_DIM.match(v.strip()):
                continue  # TOKEN_RAW_VALUE
            p = "nodes[%d].styleTokens.%s" % (i, k)
            if v not in ids:
                ctx.report("TOKEN_UNKNOWN", p, "%r is not a token in tokens/llm/token-catalog.json" % v)
            elif s["kind"] == "color":
                ok = v.startswith("tone.%s." % s["roleGroup"]) or (v.startswith("color.") and v in ctx.catalog["categories"]["color"])
                if not ok:
                    ctx.report("TOKEN_UNKNOWN", p, "%r is a token, but not one the %s slot accepts (tone.%s.* or a color.* id)" % (v, k, s["roleGroup"]))
            elif not any(v in ctx.catalog["categories"].get(cat, []) for cat in s["categories"]):
                ctx.report("TOKEN_UNKNOWN", p, "%r is a token, but the %s slot only accepts %s tokens" % (v, k, "/".join(s["categories"])))


@rule("TOKEN_THEME_MISMATCH")
def r_tok_theme(ctx, spec):
    slots = ctx.token_policy["pageSpecSlots"]
    for i, n in enumerate(spec.get("nodes", [])):
        theme = ctx.catalog["themes"].get(n.get("tone"))
        for k, v in (n.get("styleTokens") or {}).items():
            s = slots.get(k)
            if not s or s["kind"] != "color" or not isinstance(v, str) or not v.startswith("color.") or theme is None:
                continue
            allowed = sorted({ref for role, ref in theme.items() if role.startswith("tone.%s." % s["roleGroup"])})
            if v in ctx.catalog["categories"]["color"] and v not in allowed:
                ctx.report("TOKEN_THEME_MISMATCH", "nodes[%d].styleTokens.%s" % (i, k),
                           "%r is not a %s color of the %s theme (allowed: %s, or a tone.%s.* role)" % (v, s["roleGroup"], n.get("tone"), ", ".join(allowed), s["roleGroup"]))


# ------------------- generation mode: source identity + content -------------
def _content_strings(spec):
    """(path, string) for every string under brand / config / meta / nodes[].content."""
    out = []

    def walk(o, p):
        if isinstance(o, str):
            out.append((p, o))
        elif isinstance(o, dict):
            for k, v in o.items():
                walk(v, "%s.%s" % (p, k) if p else k)
        elif isinstance(o, list):
            for k, v in enumerate(o):
                walk(v, "%s[%d]" % (p, k))
    for key in ("brand", "config", "meta"):
        if key in spec:
            walk(spec[key], key)
    for i, n in enumerate(spec.get("nodes", [])):
        if isinstance(n, dict) and "content" in n:
            walk(n["content"], "nodes[%d].content" % i)
    return out


def _media(ctx, spec):
    return [(p, fs, v) for p, fs, v, _ in _leaves(ctx, spec) if fs["type"] == "media" and isinstance(v, dict)]


def _gen(spec):
    return _mode(spec) == "generation"


def _asset_category_hits(ctx, spec, category):
    """media leaves whose role or source file belongs to a leak category."""
    files = ctx.leak["assetFiles"]
    for p, fs, v in _media(ctx, spec):
        role = v.get("assetRole")
        if role in PINNED_AVAILABILITY and PINNED_AVAILABILITY[role] != "generation-safe" and PINNED_LEAK_CATEGORY.get(role, "ASSET") == category:
            yield p + ".assetRole", "assetRole %r is %s (real source asset); use %s" % (role, PINNED_AVAILABILITY[role], ctx.roles["roles"].get(role, {}).get("generationSafeSubstitutes"))
        ref = v.get("assetRef")
        if isinstance(ref, str):
            b = os.path.basename(normalize_match(ref))
            if b in files and files[b]["category"] == category:
                yield p + ".assetRef", "%r is a source-site file (%s)" % (ref, files[b]["foundAt"][0])


@rule("GENERATION_MODE_BRAND")
def r_gen_brand(ctx, spec):
    if not _gen(spec):
        return
    pats = [re.compile(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(e["pattern"])) for e in ctx.leak["categories"]["BRAND"]["patterns"]]
    squash = [re.sub(r"[^a-z0-9]", "", e["pattern"]) for e in ctx.leak["categories"]["BRAND"]["patterns"] if len(re.sub(r"[^a-z0-9]", "", e["pattern"])) >= 10]
    for p, s in _content_strings(spec):
        ns = normalize_match(s)
        flat = re.sub(r"[^a-z0-9]", "", ns)
        if any(rx.search(ns) for rx in pats) or any(q in flat for q in squash):
            ctx.report("GENERATION_MODE_BRAND", p, "names the source brand (or a variant); a generation page uses its own fictional/operator brand")
    for p, msg in _asset_category_hits(ctx, spec, "BRAND"):
        ctx.report("GENERATION_MODE_BRAND", p, msg)


@rule("GENERATION_MODE_CUSTOMER")
def r_gen_customer(ctx, spec):
    if not _gen(spec):
        return
    pats = ctx.leak["categories"]["CUSTOMER"]["patterns"]
    for p, s in _content_strings(spec):
        cs, ns = normalize_case_kept(s), normalize_match(s)
        for e in pats:
            if e["match"].startswith("case-sensitive"):
                hit = re.search(r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % re.escape(e["name"]), cs)
            else:
                hit = re.search(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(normalize_match(e["name"])), ns)
            if hit:
                ctx.report("GENERATION_MODE_CUSTOMER", p, "names a real partner/customer of the source (%s); use placeholder.company-logo with an invented name" % e["foundAt"][0])
                break
    names = [normalize_match(e["name"]) for e in pats]
    for p, fs, v in _media(ctx, spec):
        if {"partner.logo", "placeholder.company-logo"} & set(fs["roles"]):
            for k in ("alt", "assetRef"):
                if isinstance(v.get(k), str) and any(re.search(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(nm), normalize_match(v[k])) for nm in names):
                    ctx.report("GENERATION_MODE_CUSTOMER", "%s.%s" % (p, k), "partner logo names a real company (any case)")
    for p, msg in _asset_category_hits(ctx, spec, "CUSTOMER"):
        ctx.report("GENERATION_MODE_CUSTOMER", p, msg)


@rule("GENERATION_MODE_PERSON")
def r_gen_person(ctx, spec):
    if _gen(spec):
        for p, msg in _asset_category_hits(ctx, spec, "PERSON"):
            ctx.report("GENERATION_MODE_PERSON", p, msg + " - a real person; use fictional.person")


@rule("GENERATION_MODE_SCREENSHOT")
def r_gen_screenshot(ctx, spec):
    if _gen(spec):
        for p, msg in _asset_category_hits(ctx, spec, "SCREENSHOT"):
            ctx.report("GENERATION_MODE_SCREENSHOT", p, msg + " - the source app's real UI; use placeholder.screenshot")


@rule("GENERATION_MODE_ASSET")
def r_gen_asset(ctx, spec):
    if not _gen(spec):
        return
    for p, msg in _asset_category_hits(ctx, spec, "ASSET"):
        ctx.report("GENERATION_MODE_ASSET", p, msg)
    for p, fs, v in _media(ctx, spec):
        role = v.get("assetRole")
        if role in ctx.roles["roles"] and role not in PINNED_AVAILABILITY:
            ctx.report("GENERATION_MODE_ASSET", p + ".assetRole", "assetRole %r has no pinned availability; treated as not generation-safe" % role)


def _copy_hits(ctx, spec, cat):
    c = ctx.leak["categories"][cat]
    sh, ph = set(c["shingleSha256"]), set(c["phraseSha256"])
    legacy = set(ctx.protected["copyFingerprints"]["sha256"]) if cat == "COPY" else set()
    for p, s in _content_strings(spec):
        if re.match(r"^[a-z][a-z0-9+.-]*://", s.strip(), re.I) or "/" in s and " " not in s.strip():
            continue  # URLs / paths are GENERATION_MODE_URL / _ASSET
        toks = match_tokens(s)
        if shingles(toks) & sh or (3 <= len(toks) < SHINGLE and phrase_hash(toks) in ph) or (len(toks) >= 3 and fingerprint(s) in legacy):
            yield p


@rule("GENERATION_MODE_COPY")
def r_gen_copy(ctx, spec):
    if _gen(spec):
        claims = set(_copy_hits(ctx, spec, "CLAIM"))
        for p in _copy_hits(ctx, spec, "COPY"):
            if p not in claims:
                ctx.report("GENERATION_MODE_COPY", p, "reproduces source copy (a 5-word run or whole phrase matches a source string); write original copy")


@rule("GENERATION_MODE_CLAIM")
def r_gen_claim(ctx, spec):
    if _gen(spec):
        for p in _copy_hits(ctx, spec, "CLAIM"):
            ctx.report("GENERATION_MODE_CLAIM", p, "reproduces a source claim (speed/fee/number statement); write and substantiate your own")


_URL_IN_TEXT = re.compile(r"(?:[a-z][a-z0-9+.-]*://|www\.)[^\s'\"<>]+", re.I)


@rule("GENERATION_MODE_URL")
def r_gen_url(ctx, spec):
    if not _gen(spec):
        return
    c = ctx.leak["categories"]["URL"]
    ufp, hfp = set(c["urlSha256"]), set(c["hostSha256"])
    for p, s in _content_strings(spec):
        for u in _URL_IN_TEXT.findall(s):
            u = u.rstrip(".,;:)")
            host = url_host(u)
            if url_fingerprint(u) in ufp or url_fingerprint(re.sub(r"^www\.", "", host)) in hfp:
                ctx.report("GENERATION_MODE_URL", p, "a source URL/domain (fingerprint match); use a reserved placeholder host (*.example / *.invalid)")
            elif not PLACEHOLDER_HOST_RX.search(host):
                ctx.report("GENERATION_MODE_URL", p, "host %r is not a reserved placeholder (*.example / *.invalid); generation pages use placeholder URLs only" % host)


# --------------------------- both modes ----------------------------------
@rule("EXTERNAL_LINK_HTTPS")
def r_external(ctx, spec):
    for p, fs, v, _ in _leaves(ctx, spec):
        if fs["type"] == "link" and isinstance(v, dict) and isinstance(v.get("href"), str) and v["href"].startswith("http://"):
            ctx.report("EXTERNAL_LINK_HTTPS", p + ".href", "external links must be https")


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
                   "this is the source company's live form endpoint (rejected in both modes: the clone itself replaced it with a no-op); supply the project's own")


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


def example_paths(repo=REPO):
    return sorted(glob.glob(os.path.join(repo, "schema", "examples", "*.pagespec.json")))


def main(argv):
    paths = argv[1:] or example_paths()
    bad = 0
    for p in paths:
        with open(p, encoding="utf-8") as f:
            spec = json.load(f)
        errs, warns = validate(spec)
        print("%s [mode=%s]: %d error(s), %d warning(s)" % (os.path.basename(p), spec.get("mode"), len(errs), len(warns)))
        for e in errs:
            print("  ERROR [%s] %s: %s" % (e["rule"], e["path"], e["message"]))
        for w in warns:
            print("  warn  [%s] %s: %s" % (w["rule"], w["path"], w["message"]))
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
