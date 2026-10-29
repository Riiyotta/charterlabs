#!/usr/bin/env python3
"""Adversarial suite: every rule must reject a mutated instance, and the controls
must pass with zero errors (a validator that rejects everything is as broken as
one that rejects nothing).

Base instance for mutations: schema/examples/generated-home.pagespec.json
(mode=generation, fictional brand). Controls: both examples, one synthesised
control per template (generically from templates.json), targeted valid
variations, and a CLONE control that carries REAL source content (read from the
sibling source at run time - the repo never stores it) and must pass in clone
mode; the same spec flipped to generation must be rejected.
Each mutation asserts that a SPECIFIC rule code fires ("SCHEMA" = Draft-07 layer).
Wrapper-gate cases (R9) run extraction/wrapper_gate.py on a scratch copy.

Usage: python3 schema/tests/adversarial_test.py   (exit 1 on any failure)
"""
import copy
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "schema"))
sys.path.insert(0, os.path.join(REPO, "extraction"))
import semantic_validate as sv  # noqa: E402
import wrapper_gate as wg  # noqa: E402

EXAMPLE = sv.load_json("schema/examples/generated-home.pagespec.json")
CLONE = sv.load_json("schema/examples/clone-home.pagespec.json")
TEMPLATES = sv.load_json("templates/templates.json")["templates"]
SRC_ROOT = os.environ.get("DESIGN_REPO_SOURCE_ROOT") or os.path.dirname(REPO)
HAVE_SRC = os.path.isdir(os.path.join(SRC_ROOT, "src"))


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


# ------------------------------------------------- real source (run time only)
def source_strings():
    if not HAVE_SRC:
        return []
    import build_leakage_patterns as blp
    return blp.copy_strings(SRC_ROOT)


def source_at(file_suffix, line):
    for rel, i, s in source_strings():
        if rel.endswith(file_suffix) and i == line:
            return s
    return None


def source_copy_run(claim):
    """5 consecutive words of a real source string (COPY or CLAIM)."""
    lp = sv.load_json("schema/source-leakage-patterns.json")
    want = "CLAIM" if claim else "COPY"
    ats = {e["at"] for e in lp["copyEvidence"] if e["category"] == want and e["tokens"] >= 8}
    for rel, i, s in source_strings():
        if "%s:%d" % (rel, i) in ats and not re.search(r"charter|circle|hifi", s, re.I):
            w = s.split()
            return " ".join(w[1:6])
    return None


def protected_url(kind):
    if not HAVE_SRC:
        return None
    mv = sv.load_json("extraction/measured-values.json")["citations"]
    c = mv["protected.waitlist-endpoint" if kind == "endpoint" else "protected.social-x"]
    a, _b = (int(x) for x in c["lines"].split("-"))
    line = open(os.path.join(SRC_ROOT, c["path"]), encoding="utf-8").read().split("\n")[a - 1]
    return re.search(r"https://[^\s'`\"\)]+", line).group(0)


def clone_with_real_content():
    """Clone example + real hero copy, real social URL (brand, partner names and
    source asset files are already real in the committed clone example)."""
    s = copy.deepcopy(CLONE)
    h1, body, x = source_at("Hero.jsx", 55), source_at("Hero.jsx", 58), protected_url("social")
    if not (h1 and body and x):
        return None
    node(s, "hero.waitlist-hero")["content"].update(heading=h1, body=body)
    node(s, "chrome.header")["content"]["menuCompany"]["socialLinks"][0]["link"]["href"] = x
    return s


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


def control_tokens_valid():
    s = copy.deepcopy(EXAMPLE)
    node(s, "features.finances-overview")["styleTokens"] = {"surface": "color.gray.1000", "text": "tone.text.secondary", "border": "color.alphaWhite.8",
                                                            "sectionPaddingY": "spacing.scale.96", "headingStyle": "typeStyle.h2", "radius": "radius.card"}
    return s


def control_retrieval_explicit():
    s = copy.deepcopy(EXAMPLE)
    node(s, "support.faq-accordion")["retrievalEligible"] = True
    return s


CONTROLS = [("generated-home.pagespec.json (mode=generation)", lambda: copy.deepcopy(EXAMPLE)),
            ("clone-home.pagespec.json (mode=clone, real brand/partners/source files)", lambda: copy.deepcopy(CLONE))]
CONTROLS += [("synthesised control for %s" % tid, (lambda tid=tid: synth_control(tid))) for tid in TEMPLATES]
CONTROLS += [("required-nodes-only composition (warns, no errors)", control_required_only),
             ("hero Handoff dropped (allowed: drop, never add)", control_drop_handoff),
             ("FAQ omitted + Security unwrapped", control_no_faq_security_unwrapped),
             ("valid styleTokens on an inverse node", control_tokens_valid),
             ("explicit retrievalEligible=true on a content node", control_retrieval_explicit),
             ("clone mode with REAL source copy + real social URL (needs source)", clone_with_real_content)]


# --------------------------------------------------------------- mutations
def set_(path_fn, value):
    def f(s):
        obj, key = path_fn(s)
        obj[key] = value
    return f


def swap(s, a, b):
    i = [n["section"] for n in s["nodes"]].index(a)
    j = [n["section"] for n in s["nodes"]].index(b)
    s["nodes"][i], s["nodes"][j] = s["nodes"][j], s["nodes"][i]


def tok(section, **kv):
    return lambda s: node(s, section).setdefault("styleTokens", {}).update(kv)


H, HERO, INTRO, LOGO, SEND, DARK, OVW, EARN, PAY, SEC, FAQ, FOOT = [n["section"] for n in TEMPLATES["template.home"]["nodes"]]


def hero_media(s):
    return node(s, HERO)["content"]["device"]


def faq_answer(s):
    return node(s, FAQ)["content"]["items"][0]["answer"]


def portrait(s):
    return node(s, SEC)["content"]["portrait"]


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
    ("send without its logo-hosted scroll trigger", lambda s: (drop(s, LOGO), links_to(s, "logo-section")), "SEND_REQUIRES_LOGO_TRIGGER"),
    # assets (slot level)
    ("unknown assetRole", set_(lambda s: (hero_media(s), "assetRole"), "stock.photo"), "SCHEMA"),
    ("assetRole valid but wrong for slot (validator layer)", "SPECIAL", "ASSET_ROLE_ALLOWED_FOR_SLOT"),
    # motion
    ("extra motion field", lambda s: node(s, HERO)["motion"].update(parallaxBoost=2), "SCHEMA"),
    ("extra field inside a reveal entry", lambda s: node(s, INTRO)["motion"]["reveal"][0].update(blur=5), "SCHEMA"),
    ("ticker hover slowdown re-introduced (qa.01)", lambda s: node(s, LOGO)["motion"]["ticker"].update(hoverPlaybackRate=0.5), "SCHEMA"),
    ("reveal delay swapped between slots (validator layer)", lambda s: node(s, INTRO)["motion"]["reveal"][1].update(delay=0.1), "MOTION_MATCHES_CONTRACT"),
    ("hero reveal on mount amount (validator layer, qa.03)", lambda s: node(s, HERO)["motion"]["reveal"][0].update(amount=0), "MOTION_MATCHES_CONTRACT"),
    ("missing reducedMotionFallback", lambda s: node(s, FAQ)["motion"].pop("reducedMotionFallback"), "SCHEMA"),
    ("wrong reducedMotionFallback (validator layer)", "SPECIAL", "REDUCED_MOTION_FALLBACK_PINNED"),
    # copy budgets
    ("copy over budget: chars", set_(lambda s: (node(s, HERO)["content"], "heading"), "Money that moves at your pace, wherever you are."), "SCHEMA"),
    ("copy over budget: words within char limit", set_(lambda s: (node(s, HERO)["content"], "heading"), "a b c d e f g h i j k l"), "COPY_BUDGET"),
    ("copy over budget: 6 slides", lambda s: node(s, SEND)["content"]["slides"].append(copy.deepcopy(node(s, SEND)["content"]["slides"][0])), "SCHEMA"),
    ("copy over budget: footer column link count", lambda s: node(s, FOOT)["content"]["columns"][3]["links"].append({"label": "Terms", "href": "/terms"}), "COPY_BUDGET"),
    ("copy over budget: statement 3 lines", lambda s: node(s, PAY)["content"]["statementLines"].append("Again."), "SCHEMA"),
    ("extra content field", lambda s: node(s, DARK)["content"].update(subline="x"), "SCHEMA"),
    # mode
    ("mode missing", lambda s: s.pop("mode"), "SCHEMA"),
    ("mode not in the closed enum ('reference')", set_(lambda s: (s, "mode"), "reference"), "SCHEMA"),
    ("mode missing is checked as generation (validator layer, fail closed)", "SPECIAL", "GENERATION_MODE_BRAND"),
    # generation mode: brand
    ("GEN brand: source brand in copy", set_(lambda s: (node(s, INTRO)["content"], "eyebrow"), "Introducing Charter Pay"), "GENERATION_MODE_BRAND"),
    ("GEN brand: source brand as brand.name", set_(lambda s: (s["brand"], "name"), "Charter"), "GENERATION_MODE_BRAND"),
    ("GEN brand: zero-width-split brand name", set_(lambda s: (node(s, INTRO)["content"], "eyebrow"), "Meet Char​ter today"), "GENERATION_MODE_BRAND"),
    ("GEN brand: legal entity in footer legal line", set_(lambda s: (node(s, FOOT)["content"], "legalLine"), "(c) 2026 Charter Labs Inc"), "GENERATION_MODE_BRAND"),
    ("GEN brand: source domain in text", lambda s: faq_answer(s).__setitem__(0, "Visit charterlabs.io to learn more."), "GENERATION_MODE_BRAND"),
    ("GEN brand: real brand.mark role (logo leakage)", set_(lambda s: (node(s, H)["content"]["brandMark"], "assetRole"), "brand.mark"), "GENERATION_MODE_BRAND"),
    ("GEN brand: source favicon file", set_(lambda s: (s["meta"]["favicon"], "assetRef"), "assets/icon-light.svg"), "GENERATION_MODE_BRAND"),
    # generation mode: partners / customers
    ("GEN customer: partner logo alt names a real partner", set_(lambda s: (node(s, LOGO)["content"]["partners"][0]["logo"], "alt"), "Circle"), "GENERATION_MODE_CUSTOMER"),
    ("GEN customer: partner name lower-case in a logo slot", set_(lambda s: (node(s, LOGO)["content"]["partners"][1]["logo"], "alt"), "rhinestone mark"), "GENERATION_MODE_CUSTOMER"),
    ("GEN customer: issuer entity in FAQ copy", lambda s: faq_answer(s).__setitem__(0, "Our partner is Circle Internet Financial, see?"), "GENERATION_MODE_CUSTOMER"),
    ("GEN customer: real partner.logo role", set_(lambda s: (node(s, LOGO)["content"]["partners"][0]["logo"], "assetRole"), "partner.logo"), "GENERATION_MODE_CUSTOMER"),
    ("GEN customer: real partner logo file", set_(lambda s: (node(s, LOGO)["content"]["partners"][0]["logo"], "assetRef"), "logos/hifi.2560.webp"), "GENERATION_MODE_CUSTOMER"),
    # generation mode: people
    ("GEN person: real portrait role", set_(lambda s: (portrait(s), "assetRole"), "photo.portrait"), "GENERATION_MODE_PERSON"),
    ("GEN person: real portrait file under a fictional.person role", set_(lambda s: (portrait(s), "assetRef"), "img/security-portrait.webp"), "GENERATION_MODE_PERSON"),
    ("GEN person: ASCII render of a real person", set_(lambda s: (node(s, SEC)["content"]["portraitAscii"], "assetRef"), "portrait-ascii.2560.webp"), "GENERATION_MODE_PERSON"),
    # generation mode: screenshots / media
    ("GEN screenshot: real device.screen role", set_(lambda s: (hero_media(s), "assetRole"), "device.screen"), "GENERATION_MODE_SCREENSHOT"),
    ("GEN screenshot: source app screen file (proprietary media)", set_(lambda s: (hero_media(s), "assetRef"), "img/hero-phone.2560.webp"), "GENERATION_MODE_SCREENSHOT"),
    ("GEN screenshot: source share image", set_(lambda s: (s["meta"]["socialImage"], "assetRef"), "social/CHARTER-WALLET.png"), "GENERATION_MODE_SCREENSHOT"),
    ("GEN asset: clone-only texture role", set_(lambda s: (node(s, EARN)["content"]["backdrop"], "assetRole"), "texture.backdrop"), "GENERATION_MODE_ASSET"),
    ("GEN asset: source backdrop file", set_(lambda s: (node(s, EARN)["content"]["backdrop"], "assetRef"), "a/backdrop.2560.webp"), "GENERATION_MODE_ASSET"),
    # generation mode: copy / claims (real source read at run time)
    ("GEN copy: 5-word run of real source copy inside an original sentence", "SOURCE", "GENERATION_MODE_COPY"),
    ("GEN copy: same run with curly quotes / NBSP / zero-width noise", "SOURCE", "GENERATION_MODE_COPY"),
    ("GEN claim: a real source speed/fee/number claim", "SOURCE", "GENERATION_MODE_CLAIM"),
    ("GEN copy: real hero heading verbatim", "SOURCE", "GENERATION_MODE_COPY"),
    # generation mode: URLs
    ("GEN url: real social profile", "SOURCE", "GENERATION_MODE_URL"),
    ("GEN url: app store link (store mark/URL leakage)", set_(lambda s: (node(s, H)["content"]["menuCompany"]["socialLinks"][0]["link"], "href"), "https://apps.apple.com/app/id000000"), "GENERATION_MODE_URL"),
    ("GEN url: non-reserved example.com host", set_(lambda s: (node(s, H)["content"]["menuCompany"]["socialLinks"][1]["link"], "href"), "https://example.com/acme"), "GENERATION_MODE_URL"),
    ("GEN url: waitlist endpoint on a real host", set_(lambda s: (s["config"], "waitlistEndpoint"), "https://forms.acme-wallet.com/join"), "GENERATION_MODE_URL"),
    ("GEN url: source domain URL in copy", lambda s: faq_answer(s).__setitem__(0, "See https://www.charterlabs.io/legal for details."), "GENERATION_MODE_URL"),
    # both modes
    ("waitlist endpoint missing", lambda s: s["config"].pop("waitlistEndpoint"), "SCHEMA"),
    ("waitlist endpoint not https", set_(lambda s: (s["config"], "waitlistEndpoint"), "http://forms.fernway.example/x"), "SCHEMA"),
    ("waitlist endpoint = source company's live endpoint (generation)", "SOURCE", "WAITLIST_ENDPOINT_PROJECT_SUPPLIED"),
    ("waitlist endpoint = live endpoint is rejected in CLONE mode too", "SOURCE", "WAITLIST_ENDPOINT_PROJECT_SUPPLIED"),
    ("external link http (validator layer)", "SPECIAL", "EXTERNAL_LINK_HTTPS"),
    ("internal link to an anchor not on the page", lambda s: (drop(s, PAY),), "INTERNAL_ANCHOR_RESOLVES"),
    ("REAL-content clone spec flipped to mode=generation", "SOURCE", "GENERATION_MODE_COPY"),
    # retrieval (R8)
    ("content section marked retrieval-ineligible at node level", set_(lambda s: (node(s, FAQ), "retrievalEligible"), False), "RETRIEVAL_ELIGIBILITY_MATCH"),
    ("retrievalEligible not a boolean", set_(lambda s: (node(s, FAQ), "retrievalEligible"), "yes"), "SCHEMA"),
    # tokens (R10)
    ("token: raw hex colour", tok(HERO, surface="#ffffff"), "TOKEN_RAW_VALUE"),
    ("token: raw rgb() colour", tok(OVW, text="rgb(255, 255, 255)"), "TOKEN_RAW_VALUE"),
    ("token: arbitrary spacing in px", tok(HERO, sectionPaddingY="120px"), "TOKEN_ARBITRARY_SPACING"),
    ("token: spacing step not on the measured scale", tok(HERO, sectionPaddingY="spacing.scale.20"), "TOKEN_ARBITRARY_SPACING"),
    ("token: unsupported font", tok(HERO, fontFamily="Helvetica Neue"), "TOKEN_UNSUPPORTED_FONT"),
    ("token: unknown colour token", tok(HERO, surface="color.brand.green"), "TOKEN_UNKNOWN"),
    ("token: real token of the wrong category", tok(HERO, headingStyle="radius.md"), "TOKEN_UNKNOWN"),
    ("token: text role in the surface slot", tok(HERO, surface="tone.text.primary"), "TOKEN_UNKNOWN"),
    ("token: light-theme text colour on an inverse node", tok(OVW, text="color.gray.1000"), "TOKEN_THEME_MISMATCH"),
    ("token: inverse surface on a light node", tok(INTRO, surface="color.gray.1000"), "TOKEN_THEME_MISMATCH"),
    ("token: unknown styleTokens slot", tok(HERO, shadow="shadow.waitlistPill"), "SCHEMA"),
]


def _bypass(spec, mutate):
    """Some rules duplicate a schema guard on purpose; prove the validator layer
    alone also rejects by running it with the schema layer switched off."""
    mutate(spec)
    errs, _ = sv.validate(spec, with_schema=False)
    return errs


SPECIAL = {
    "assetRole valid but wrong for slot (validator layer)": lambda s: hero_media(s).update(assetRole="placeholder.company-logo"),
    "wrong reducedMotionFallback (validator layer)": lambda s: node(s, EARN)["motion"].update(reducedMotionFallback="text-shown"),
    "mode missing is checked as generation (validator layer, fail closed)": lambda s: (s.pop("mode"), s["brand"].update(name="Charter")),
    "external link http (validator layer)": lambda s: node(s, H)["content"]["menuCompany"]["socialLinks"][0]["link"].update(href="http://x.fernway.example/a"),
}


def source_mutation(name, s):
    """Returns the mutated spec, or None when the source project is absent."""
    if name.startswith("GEN copy: 5-word"):
        run_ = source_copy_run(False)
        if not run_:
            return None
        faq_answer(s)[0] = "Plainly put, %s, we think." % run_
    elif name.startswith("GEN copy: same run"):
        run_ = source_copy_run(False)
        if not run_:
            return None
        w = run_.split()
        w[1] = w[1][:1] + "​" + w[1][1:]
        faq_answer(s)[0] = "“Plainly” — %s." % " ".join(w)
    elif name.startswith("GEN claim"):
        run_ = source_copy_run(True)
        if not run_:
            return None
        faq_answer(s)[0] = "Good news: %s." % run_
    elif name.startswith("GEN copy: real hero heading"):
        h1 = source_at("Hero.jsx", 55)
        if not h1:
            return None
        node(s, HERO)["content"]["heading"] = h1
    elif name.startswith("GEN url: real social"):
        u = protected_url("social")
        if not u:
            return None
        node(s, H)["content"]["menuCompany"]["socialLinks"][0]["link"]["href"] = u
    elif name.startswith("waitlist endpoint = source"):
        u = protected_url("endpoint")
        if not u:
            return None
        s["config"]["waitlistEndpoint"] = u
    elif name.startswith("waitlist endpoint = live endpoint is rejected in CLONE"):
        u = protected_url("endpoint")
        if not u:
            return None
        s = copy.deepcopy(CLONE)
        s["config"]["waitlistEndpoint"] = u
    elif name.startswith("REAL-content clone"):
        s = clone_with_real_content()
        if s is None:
            return None
        s["mode"] = "generation"
    return s


# ----------------------------------------------------- wrapper gate (R9)
def gate_cases():
    def heights(fn):
        def f(root):
            p = os.path.join(root, "extraction/measured-values.json")
            mv = json.load(open(p, encoding="utf-8"))
            fn(mv["sectionHeights"]["pages"]["template.home"]["sections"], mv)
            json.dump(mv, open(p, "w", encoding="utf-8"))
        return f

    def wl(entry):
        def f(root):
            p = os.path.join(root, "extraction/wrapper-gate-whitelist.json")
            w = json.load(open(p, encoding="utf-8"))
            w["entries"].append(entry)
            json.dump(w, open(p, "w", encoding="utf-8"))
        return f

    def both(*fs):
        return lambda root: [f(root) for f in fs]

    hero = "hero.waitlist-hero"
    good = {"template": "template.home", "section": hero, "maxHeightPx": 3200, "reviewedBy": "design-repo agent (agent attestation, not a human sign-off)",
            "justification": "synthetic test entry: hero intentionally tall in this scratch copy"}
    return [
        ("HERO 1900px warns (not an error)", heights(lambda s, mv: s[hero].update(heightPx=1900)), "warn"),
        ("HERO 3100px errors", heights(lambda s, mv: s[hero].update(heightPx=3100)), "error"),
        ("HERO 3100px whitelisted: passes but still warns", both(heights(lambda s, mv: s[hero].update(heightPx=3100)), wl(good)), "warn"),
        ("whitelist without justification", both(heights(lambda s, mv: s[hero].update(heightPx=3100)), wl(dict(good, justification="too short"))), "error"),
        ("whitelist by an agent without the attestation wording", both(heights(lambda s, mv: s[hero].update(heightPx=3100)), wl(dict(good, reviewedBy="review agent"))), "error"),
        ("whitelist maxHeightPx below the measured height", both(heights(lambda s, mv: s[hero].update(heightPx=3100)), wl(dict(good, maxHeightPx=3000))), "error"),
        ("stale whitelist entry (measurement no longer needs it)", wl(good), "error"),
        ("one section holds a majority of the page (> 60%)", heights(lambda s, mv: s["features.send-slideshow"].update(heightPx=20000)), "error"),
        ("one section holds 55% of the page (warn)", heights(lambda s, mv: s["features.send-slideshow"].update(heightPx=12000)), "warn"),
        ("missing measurement", heights(lambda s, mv: s.pop("features.earn-collapse")), "error"),
        ("measured at the wrong viewport", heights(lambda s, mv: mv["sectionHeights"]["viewport"].update(width=1280)), "error"),
    ]


def run_gate_cases():
    fails = 0
    tmp = tempfile.mkdtemp(prefix="wrapper-gate-")
    try:
        for i, (name, inject, want) in enumerate(gate_cases()):
            root = os.path.join(tmp, "c%02d" % i)
            shutil.copytree(REPO, root, ignore=shutil.ignore_patterns("__pycache__"))
            inject(root)
            errs, warns = wg.run(root)
            got = "error" if errs else ("warn" if warns else "pass")
            ok = got == want
            fails += not ok
            print("  %s  %-62s -> %s" % ("CAUGHT  " if ok else "MISSED  ", name, got))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return fails, len(gate_cases())


def run():
    fails = 0
    skipped = 0
    print("== controls (must produce 0 errors)")
    for name, mk in CONTROLS:
        spec = mk()
        if spec is None:
            skipped += 1
            print("  SKIP  %s  (source project not present; real content is deliberately not stored)" % name)
            continue
        errs, warns = sv.validate(spec)
        ok = not errs
        fails += not ok
        print("  %s  %s  (%d errors, %d warnings%s)" % ("PASS" if ok else "FAIL", name, len(errs), len(warns),
                                                        ", warns: " + ",".join(sorted({w["rule"] for w in warns})) if warns else ""))
        for e in errs[:5]:
            print("        ", e["rule"], e["path"], e["message"][:120])
    print("== mutations (each must be rejected by the named rule)")
    for name, mut, want in MUTATIONS:
        s = copy.deepcopy(EXAMPLE)
        if mut == "SPECIAL":
            errs = _bypass(s, SPECIAL[name])
        elif mut == "SOURCE":
            s = source_mutation(name, s)
            if s is None:
                skipped += 1
                print("  SKIP  %s  (source project not present)" % name)
                continue
            errs, _ = sv.validate(s)
        else:
            mut(s)
            errs, _ = sv.validate(s)
        codes = sorted({e["rule"] for e in errs})
        ok = want in codes
        fails += not ok
        print("  %s  %-62s -> %s" % ("REJECTED" if ok else "MISSED  ", name, ",".join(codes) or "(no errors)"))
    print("== wrapper gate (R9) on scratch copies")
    gf, gn = run_gate_cases()
    fails += gf
    print("\nSUMMARY: %d controls, %d mutations, %d gate cases (%d skipped), failures: %d" % (len(CONTROLS), len(MUTATIONS), gn, skipped, fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())
