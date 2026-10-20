#!/usr/bin/env python3
"""Adversarial suite: every rule must reject a mutated instance, and the controls
must pass with zero errors (a validator that rejects everything is as broken as
one that rejects nothing).

Controls are synthesised generically per template from templates.json (one per
template, using the example's node bodies), plus targeted valid variations.
Each mutation asserts that a SPECIFIC rule code fires ("SCHEMA" = Draft-07 layer).

Usage: python3 schema/tests/adversarial_test.py   (exit 1 on any failure)
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "schema"))
import semantic_validate as sv  # noqa: E402

EXAMPLE = sv.load_json("schema/example.pagespec.json")
TEMPLATES = sv.load_json("templates/templates.json")["templates"]


def node(spec, section):
    for n in spec["nodes"]:
        if n["section"] == section:
            return n
    raise KeyError(section)


def drop(spec, *sections):
    spec["nodes"] = [n for n in spec["nodes"] if n["section"] not in sections]


def links_to(spec, anchor):
    """remove links that would point at a dropped anchor (keeps controls honest)"""
    def fix(o):
        if isinstance(o, dict):
            if o.get("href") == "/#" + anchor:
                o["href"] = "/#hero-section"
            for v in o.values():
                fix(v)
        elif isinstance(o, list):
            for v in o:
                fix(v)
    fix(spec)


# ---------------------------------------------------------------- controls
def synth_control(tid):
    t = TEMPLATES[tid]
    bodies = {n["section"]: n for n in EXAMPLE["nodes"]}
    s = copy.deepcopy(EXAMPLE)
    s["template"], s["route"] = tid, t["routes"][0]
    s["nodes"] = []
    for tn in t["nodes"]:
        b = copy.deepcopy(bodies[tn["section"]])
        b.update(variant=tn["allowedVariants"][0], tone=tn["tone"], handoff=tn["handoffObserved"], anchorId=tn["anchorId"])
        s["nodes"].append(b)
    return s


def control_required_only():
    s = copy.deepcopy(EXAMPLE)
    req = {n["section"] for n in TEMPLATES["template.home"]["nodes"] if n["required"]}
    for n in list(s["nodes"]):
        if n["section"] not in req and n.get("anchorId"):
            links_to(s, n["anchorId"])
    s["nodes"] = [n for n in s["nodes"] if n["section"] in req]
    return s


def control_drop_handoff():
    s = copy.deepcopy(EXAMPLE)
    node(s, "hero.waitlist-hero")["handoff"] = None
    return s


def control_no_faq_security_unwrapped():
    s = copy.deepcopy(EXAMPLE)
    drop(s, "support.faq-accordion")
    links_to(s, "faq-section")
    node(s, "features.security-ascii")["handoff"] = None
    return s


CONTROLS = [("example.pagespec.json", lambda: copy.deepcopy(EXAMPLE))]
CONTROLS += [("synthesised control for %s" % tid, (lambda tid=tid: synth_control(tid))) for tid in TEMPLATES]
CONTROLS += [("required-nodes-only composition (warns, no errors)", control_required_only),
             ("hero Handoff dropped (allowed: drop, never add)", control_drop_handoff),
             ("FAQ omitted + Security unwrapped", control_no_faq_security_unwrapped)]


# --------------------------------------------------------------- mutations
def M(fn):
    s = copy.deepcopy(EXAMPLE)
    fn(s)
    return s


def swap(s, a, b):
    i = [n["section"] for n in s["nodes"]].index(a)
    j = [n["section"] for n in s["nodes"]].index(b)
    s["nodes"][i], s["nodes"][j] = s["nodes"][j], s["nodes"][i]


def set_(path_fn, value):
    def f(s):
        obj, key = path_fn(s)
        obj[key] = value
    return f


H, HERO, INTRO, LOGO, SEND, DARK, OVW, EARN, PAY, SEC, FAQ, FOOT = [n["section"] for n in TEMPLATES["template.home"]["nodes"]]
LONG = "word " * 30

MUTATIONS = [
    # template / node-list cross-reference
    ("template/node mismatch: two nodes swapped", lambda s: swap(s, INTRO, LOGO), "TEMPLATE_NODE_ORDER"),
    ("template/node mismatch: hero moved after send", lambda s: swap(s, HERO, SEND), "TEMPLATE_NODE_ORDER"),
    ("template/node mismatch: duplicate hero", lambda s: s["nodes"].insert(2, copy.deepcopy(node(s, HERO))), "NO_REPEAT"),
    ("template/node mismatch: required header removed", lambda s: drop(s, H), "TEMPLATE_REQUIRED_NODES"),
    ("template/node mismatch: required dark transition removed", lambda s: drop(s, DARK), "TEMPLATE_REQUIRED_NODES"),
    ("unknown template id", set_(lambda s: (s, "template"), "template.landing"), "SCHEMA"),
    ("unknown section type", set_(lambda s: (s["nodes"][1], "section"), "hero.split"), "SCHEMA"),
    ("variant not allowed by template", set_(lambda s: (node(s, HERO), "variant"), "split-image-left"), "VARIANT_ALLOWED"),
    ("anchorId changed", set_(lambda s: (node(s, EARN), "anchorId"), "savings"), "ANCHOR_ID_MATCH"),
    ("route not in template", set_(lambda s: (s, "route"), "/contact"), "ROUTE_MATCHES_TEMPLATE"),
    # tone
    ("tone order: light section after the dark transition", set_(lambda s: (node(s, OVW), "tone"), "light"), "TONE_SEQUENCE"),
    ("tone order: inverse section before the dark transition", set_(lambda s: (node(s, SEND), "tone"), "inverse"), "TONE_SEQUENCE"),
    ("tone order: inverse header", set_(lambda s: (node(s, H), "tone"), "inverse"), "TONE_SEQUENCE"),
    # handoff
    ("Handoff misuse: added where never observed (earn)", lambda s: node(s, EARN).update(handoff="inverse"), "HANDOFF_ALLOWED_VALUE"),
    ("Handoff misuse: retoned (hero inverse)", set_(lambda s: (node(s, HERO), "handoff"), "inverse"), "HANDOFF_TONE_MATCH"),
    ("Handoff misuse: on the footer", set_(lambda s: (node(s, FOOT), "handoff"), "inverse"), "HANDOFF_NEEDS_MAIN_FOLLOWER"),
    ("Handoff misuse: security wrapped with nothing after it in main", lambda s: (drop(s, FAQ), links_to(s, "faq-section")), "HANDOFF_NEEDS_MAIN_FOLLOWER"),
    # dependency
    ("send without its logo-hosted scroll trigger", lambda s: (drop(s, LOGO), links_to(s, "logo-section")), "SEND_REQUIRES_LOGO_TRIGGER"),
    # assets
    ("unknown assetRole", set_(lambda s: (node(s, HERO)["content"]["device"], "assetRole"), "stock.photo"), "SCHEMA"),
    ("assetRole valid but wrong for slot (validator layer)", lambda s: None, "ASSET_ROLE_ALLOWED_FOR_SLOT"),  # patched below (schema bypass)
    ("assetRef reuses a source-site file", set_(lambda s: (node(s, HERO)["content"]["device"], "assetRef"), "img/hero-phone.2560.webp"), "ASSET_REF_NOT_SOURCE_FILE"),
    ("partner logo alt names a real partner", set_(lambda s: (node(s, LOGO)["content"]["partners"][0]["logo"], "alt"), "Circle"), "NO_SOURCE_BRAND_NAME"),
    # motion
    ("extra motion field", lambda s: node(s, HERO)["motion"].update(parallaxBoost=2), "SCHEMA"),
    ("extra field inside a reveal entry", lambda s: node(s, INTRO)["motion"]["reveal"][0].update(blur=5), "SCHEMA"),
    ("ticker hover slowdown re-introduced (qa.01)", lambda s: node(s, LOGO)["motion"]["ticker"].update(hoverPlaybackRate=0.5), "SCHEMA"),
    ("reveal delay swapped between slots (validator layer)", lambda s: node(s, INTRO)["motion"]["reveal"][1].update(delay=0.1), "MOTION_MATCHES_CONTRACT"),
    ("hero reveal on mount amount (validator layer, qa.03)", lambda s: node(s, HERO)["motion"]["reveal"][0].update(amount=0), "MOTION_MATCHES_CONTRACT"),
    ("missing reducedMotionFallback", lambda s: node(s, FAQ)["motion"].pop("reducedMotionFallback"), "SCHEMA"),
    ("wrong reducedMotionFallback (validator layer)", lambda s: None, "REDUCED_MOTION_FALLBACK_PINNED"),  # patched below
    # copy
    ("copy over budget: chars", set_(lambda s: (node(s, HERO)["content"], "heading"), "Money that moves at your pace, wherever you are."), "SCHEMA"),
    ("copy over budget: words within char limit", set_(lambda s: (node(s, HERO)["content"], "heading"), "a b c d e f g h i j k l"), "COPY_BUDGET"),
    ("copy over budget: 6 slides", lambda s: node(s, SEND)["content"]["slides"].append(copy.deepcopy(node(s, SEND)["content"]["slides"][0])), "SCHEMA"),
    ("copy over budget: footer column link count", lambda s: node(s, FOOT)["content"]["columns"][3]["links"].append({"label": "Terms", "href": "/terms"}), "COPY_BUDGET"),
    ("copy over budget: statement 3 lines", lambda s: node(s, PAY)["content"]["statementLines"].append("Again."), "SCHEMA"),
    ("extra content field", lambda s: node(s, DARK)["content"].update(subline="x"), "SCHEMA"),
    ("verbatim source copy reused (read from source at runtime)", lambda s: None, "NO_VERBATIM_SOURCE_COPY"),  # patched below
    ("source brand name in copy", set_(lambda s: (node(s, INTRO)["content"], "eyebrow"), "Introducing Charter Pay"), "NO_SOURCE_BRAND_NAME"),
    ("source brand as brand.name", set_(lambda s: (s["brand"], "name"), "Charter"), "NO_SOURCE_BRAND_NAME"),
    # waitlist + links
    ("missing waitlist endpoint", lambda s: s["config"].pop("waitlistEndpoint"), "SCHEMA"),
    ("waitlist endpoint not https", set_(lambda s: (s["config"], "waitlistEndpoint"), "http://forms.example.com/x"), "SCHEMA"),
    ("waitlist endpoint = source company's live endpoint", lambda s: None, "WAITLIST_ENDPOINT_PROJECT_SUPPLIED"),  # patched below
    ("real social profile reused", lambda s: None, "EXTERNAL_LINK_NOT_PROTECTED"),  # patched below
    ("internal link to an anchor not on the page", lambda s: (drop(s, PAY),), "INTERNAL_ANCHOR_RESOLVES"),
]


def _bypass(spec, mutate, rule_id):
    """Some rules duplicate a schema guard on purpose; prove the validator layer
    alone also rejects by running it with the schema layer switched off."""
    mutate(spec)
    errs, _ = sv.validate(spec, with_schema=False)
    return errs


SPECIAL = {
    "assetRole valid but wrong for slot (validator layer)": lambda s: node(s, HERO)["content"]["device"].update(assetRole="partner.logo"),
    "wrong reducedMotionFallback (validator layer)": lambda s: node(s, EARN)["motion"].update(reducedMotionFallback="text-shown"),
}


def protected_url_mutation(kind):
    """The real URLs are NOT stored in this repo. These cases only run when the
    source project is beside the repo (they read the URL from it); otherwise
    they are reported as skipped, never as passed."""
    root = os.environ.get("DESIGN_REPO_SOURCE_ROOT") or os.path.dirname(REPO)
    mv = sv.load_json("extraction/measured-values.json")["citations"]
    c = mv["protected.waitlist-endpoint" if kind == "endpoint" else "protected.social-x"]
    p = os.path.join(root, c["path"])
    if not os.path.isfile(p):
        return None
    import re
    a, _b = (int(x) for x in c["lines"].split("-"))
    line = open(p, encoding="utf-8").read().split("\n")[a - 1]
    return re.search(r"https://[^\s'`\"\)]+", line).group(0)


def source_sentence():
    """A real source sentence, read from the sibling CLONE_SPEC hero block at run
    time (the repo itself never stores source copy). None if the source is absent."""
    root = os.environ.get("DESIGN_REPO_SOURCE_ROOT") or os.path.dirname(REPO)
    c = sv.load_json("extraction/measured-values.json")["citations"]["spec.2.1-hero"]
    p = os.path.join(root, c["path"])
    if not os.path.isfile(p):
        return None
    import re
    a, b = (int(x) for x in c["lines"].split("-"))
    fps = set(sv.load_json("schema/protected-content.json")["copyFingerprints"]["sha256"])
    for line in open(p, encoding="utf-8").read().split("\n")[a - 1:b]:
        for q in re.findall(r'"([^"]+)"', line):
            if sv.fingerprint(q) in fps and len(q) <= 36:
                return q
    return None


def run():
    fails = 0
    skipped = 0
    print("== controls (must produce 0 errors)")
    for name, mk in CONTROLS:
        errs, warns = sv.validate(mk())
        ok = not errs
        fails += not ok
        print("  %s  %s  (%d errors, %d warnings%s)" % ("PASS" if ok else "FAIL", name, len(errs), len(warns),
                                                        ", warns: " + ",".join(sorted({w["rule"] for w in warns})) if warns else ""))
        for e in errs[:5]:
            print("        ", e["rule"], e["path"], e["message"][:120])
    print("== mutations (each must be rejected by the named rule)")
    for name, mut, want in MUTATIONS:
        s = copy.deepcopy(EXAMPLE)
        if name in SPECIAL:
            errs = _bypass(s, SPECIAL[name], want)
        elif want == "NO_VERBATIM_SOURCE_COPY":
            q = source_sentence()
            if q is None:
                skipped += 1
                print("  SKIP  %s  (source project not present; source copy is deliberately not stored)" % name)
                continue
            node(s, HERO)["content"]["heading"] = q
            errs, _ = sv.validate(s)
        elif want == "WAITLIST_ENDPOINT_PROJECT_SUPPLIED" or want == "EXTERNAL_LINK_NOT_PROTECTED":
            url = protected_url_mutation("endpoint" if want.startswith("WAITLIST") else "social")
            if url is None:
                skipped += 1
                print("  SKIP  %s  (source project not present; real URL is deliberately not stored)" % name)
                continue
            if want.startswith("WAITLIST"):
                s["config"]["waitlistEndpoint"] = url
            else:
                node(s, H)["content"]["menuCompany"]["socialLinks"][0]["link"]["href"] = url
            errs, _ = sv.validate(s)
        else:
            mut(s)
            errs, _ = sv.validate(s)
        codes = sorted({e["rule"] for e in errs})
        ok = want in codes
        fails += not ok
        print("  %s  %-62s -> %s" % ("REJECTED" if ok else "MISSED  ", name, ",".join(codes) or "(no errors)"))
    print("\nSUMMARY: %d controls, %d mutations (%d skipped), failures: %d" % (len(CONTROLS), len(MUTATIONS), skipped, fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())
