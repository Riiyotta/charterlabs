#!/usr/bin/env python3
"""Whole-page-wrapper quality gate (R9). Called by verify_all.py (check wrapper-gate).

Reads the MEASURED section heights (extraction/measured-values.json -> sectionHeights,
recorded from the built clone at 1440px by extraction/measure_sections.mjs) and:
  * HERO > 1800px warns; HERO > 3000px errors unless whitelisted
  * one in-flow section > 50% of its page's in-flow height warns; > 60% errors
    unless whitelisted (skipped when a page has < 3 in-flow sections; SHELL /
    CHROME sections and fixed/absolute/sticky elements are excluded)
  * a template node with no measurement errors; a viewport other than 1440 errors
  * whitelist entries need reviewedBy (an agent must say "agent attestation, not a
    human sign-off"), a justification >= 30 chars and a maxHeightPx above the
    measured height; stale (no longer needed / unknown section) or over-cap
    entries error. A whitelisted hit still warns.
Thresholds are pinned here in code; the JSON cannot change them.

    python3 extraction/wrapper_gate.py      # prints findings, exit 1 on any error
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERO_WARN_PX = 1800
HERO_ERROR_PX = 3000
SHARE_WARN = 0.50
SHARE_ERROR = 0.60
MIN_INFLOW_SECTIONS = 3
VIEWPORT_WIDTH = 1440
EXCLUDED_CATEGORIES = {"CHROME", "SHELL"}
OUT_OF_FLOW = {"fixed", "absolute", "sticky"}
AGENT_ATTESTATION = "agent attestation, not a human sign-off"


def _load(rel, repo):
    with open(os.path.join(repo, rel), encoding="utf-8") as f:
        return json.load(f)


def run(repo=REPO):
    errors, warns = [], []
    mv = _load("extraction/measured-values.json", repo)
    sh = mv.get("sectionHeights")
    wl = _load("extraction/wrapper-gate-whitelist.json", repo).get("entries", [])
    templates = _load("templates/templates.json", repo)["templates"]
    cats = {}
    for fn in os.listdir(os.path.join(repo, "sections")):
        if fn.endswith(".json"):
            c = _load("sections/" + fn, repo)
            cats[c["id"]] = c["semantic"]["category"] if isinstance(c.get("semantic"), dict) else c.get("category")
    if not sh:
        return ["no sectionHeights in extraction/measured-values.json"], warns
    if (sh.get("viewport") or {}).get("width") != VIEWPORT_WIDTH:
        errors.append("sectionHeights measured at width %r, must be %d" % ((sh.get("viewport") or {}).get("width"), VIEWPORT_WIDTH))
    wmap = {}
    for e in wl:
        key = (e.get("template"), e.get("section"))
        wmap[key] = e
        rb = str(e.get("reviewedBy", ""))
        if not rb:
            errors.append("whitelist %s: reviewedBy missing" % (key,))
        elif "agent" in rb.lower() and AGENT_ATTESTATION not in rb:
            errors.append("whitelist %s: an agent reviewer must say '%s'" % (key, AGENT_ATTESTATION))
        if len(str(e.get("justification", ""))) < 30:
            errors.append("whitelist %s: justification must be >= 30 chars" % (key,))
    used = set()
    for tid, t in templates.items():
        page = (sh.get("pages") or {}).get(tid)
        if not page:
            errors.append("%s: no measurement" % tid)
            continue
        secs = page.get("sections") or {}
        inflow = {}
        for n in t["nodes"]:
            m = secs.get(n["section"])
            if not isinstance(m, dict) or not isinstance(m.get("heightPx"), (int, float)):
                errors.append("%s.%s: missing measurement" % (tid, n["section"]))
                continue
            if cats.get(n["section"]) in EXCLUDED_CATEGORIES or m.get("position") in OUT_OF_FLOW:
                continue
            inflow[n["section"]] = m["heightPx"]
        total = sum(inflow.values())
        for sid, h in inflow.items():
            key = (tid, sid)
            w = wmap.get(key)
            hits = []
            if cats.get(sid) == "HERO" and h > HERO_WARN_PX:
                hits.append(("hero", h > HERO_ERROR_PX, "HERO %s is %.0fpx (> %d warn / > %d error)" % (sid, h, HERO_WARN_PX, HERO_ERROR_PX)))
            if len(inflow) >= MIN_INFLOW_SECTIONS and total and h / total > SHARE_WARN:
                hits.append(("share", h / total > SHARE_ERROR, "%s holds %.0f%% of the in-flow page (> %d%% warn / > %d%% error)" % (sid, 100 * h / total, 100 * SHARE_WARN, 100 * SHARE_ERROR)))
            for _kind, is_err, msg in hits:
                if is_err and not w:
                    errors.append("%s: %s" % (tid, msg))
                else:
                    warns.append("%s: %s%s" % (tid, msg, " (whitelisted)" if w else ""))
            if w:
                used.add(key)
                if not hits or not any(e for _k, e, _m in hits):
                    errors.append("whitelist %s is stale: the measurement no longer needs it" % (key,))
                if not isinstance(w.get("maxHeightPx"), (int, float)) or w["maxHeightPx"] <= h:
                    errors.append("whitelist %s: maxHeightPx %r must be above the measured %.0fpx" % (key, w.get("maxHeightPx"), h))
    for key in wmap:
        if key not in used and not any(key == k for k in used):
            if key[0] not in templates or key[1] not in {n["section"] for n in templates.get(key[0], {"nodes": []})["nodes"]}:
                errors.append("whitelist %s names no measured template section" % (key,))
            elif key not in used:
                errors.append("whitelist %s is stale" % (key,))
    return errors, warns


def summary(repo=REPO):
    sh = _load("extraction/measured-values.json", repo).get("sectionHeights") or {}
    out = []
    for tid, p in (sh.get("pages") or {}).items():
        s = p.get("sections") or {}
        hero = max([v["heightPx"] for k, v in s.items() if v and k.startswith("hero.")] or [0])
        out.append("%s page %spx, hero %.0fpx" % (tid, p.get("pageHeightPx"), hero))
    return "; ".join(out)


if __name__ == "__main__":
    e, w = run()
    for x in w:
        print("WARN ", x)
    for x in e:
        print("ERROR", x)
    print("wrapper gate: %d error(s), %d warning(s); %s" % (len(e), len(w), summary()))
    sys.exit(1 if e else 0)
