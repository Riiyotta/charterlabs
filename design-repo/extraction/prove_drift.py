#!/usr/bin/env python3
"""Prove verify_all.py's drift checks actually catch drift (MASTER-GUIDE 3.2/3.4/3.16/3.23).

For each case: copy design-repo/ to a fresh folder under --scratch, inject one
defect, run verify_all.py --quick against it, and require (a) exit code 1 and
(b) the named check reporting FAIL. Then confirm the unmodified repo passes.

Usage: python3 extraction/prove_drift.py --scratch DIR [--source-root DIR]
  --scratch      empty-able working folder for the scratch copies (required;
                 nothing is written inside design-repo/)
  --source-root  project root with the cited evidence (default: parent of design-repo/)
"""
import json
import os
import re
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "schema"))
import semantic_validate as sv  # noqa: E402


def jload(p):
    return json.load(open(p, encoding="utf-8"))


def jsave(p, o):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(o, f, indent=2, ensure_ascii=False)


def edit_json(rel, fn):
    def f(root):
        p = os.path.join(root, rel)
        o = jload(p)
        fn(o)
        jsave(p, o)
    return f


def append_text(rel, text):
    def f(root):
        with open(os.path.join(root, rel), "a", encoding="utf-8") as fh:
            fh.write(text)
    return f


def replace_text(rel, a, b):
    def f(root):
        p = os.path.join(root, rel)
        txt = open(p, encoding="utf-8").read()
        assert a in txt, "replace target missing: %r" % a
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(txt.replace(a, b))
    return f


def source_line_value(src_root, cid, rx):
    c = jload(os.path.join(REPO, "extraction/measured-values.json"))["citations"][cid]
    a, b = (int(x) for x in c["lines"].split("-"))
    lines = open(os.path.join(src_root, c["path"]), encoding="utf-8").read().split("\n")[a - 1:b]
    for line in lines:
        for m in re.findall(rx, line):
            yield m


def cases(src_root):
    fps = set(jload(os.path.join(REPO, "schema/protected-content.json"))["copyFingerprints"]["sha256"])
    sentence = next((q for q in source_line_value(src_root, "spec.2.1-hero", r'"([^"]+)"') if sv.fingerprint(q) in fps), None)
    endpoint = next(source_line_value(src_root, "protected.waitlist-endpoint", r"https://[^\s'`\"\)]+"), None)
    return [
        ("phantom allowlist entry", "allowlist-parity", edit_json("tokens/llm/component-allowlist.json", lambda o: o["entries"].append(
            {"id": "component.divider", "kind": "component", "file": "components/divider.json", "instantiableInPageSpec": False}))),
        ("orphan contract file", "allowlist-parity", lambda r: jsave(os.path.join(r, "primitives/badge.json"), {"id": "primitive.badge", "kind": "primitive"})),
        ("out-of-range citation", "citations", edit_json("extraction/measured-values.json", lambda o: o["citations"]["spec.2.3-logo"].update(lines="9990-9999"))),
        ("in-range citation at the wrong lines", "citations", edit_json("extraction/measured-values.json", lambda o: o["citations"]["src.earn.toggle"].update(
            lines="%d-%d" % (int(o["citations"]["src.earn.toggle"]["lines"].split("-")[0]) + 40, int(o["citations"]["src.earn.toggle"]["lines"].split("-")[0]) + 42)))),
        ("manifest count drift", "manifest-counts", edit_json("registry.manifest.json", lambda o: o["counts"].update(sections=13))),
        ("README count drift", "readme-counts", replace_text("README.md", "| sections | 12 |", "| sections | 11 |")),
        ("allowlistVersion drift", "allowlist-version", edit_json("registry.manifest.json", lambda o: o.update(allowlistVersion="1.1.0"))),
        ("pinned asset policy swapped to another VALID value", "asset-roles", edit_json("assets/asset-roles.json", lambda o: o["roles"]["partner.logo"].update(generationPolicy="generate-original"))),
        ("graph rule with no validator implementation", "graph-validator", edit_json("compatibility/graph.json", lambda o: o["rules"].append(
            {"id": "ONE_CTA_PER_SECTION", "severity": "error", "description": "x", "enforcedBy": "schema/semantic_validate.py"}))),
        ("entry point outside the package", "entry-points", edit_json("registry.manifest.json", lambda o: o["entryPoints"].update(spec="../CLONE_SPEC.md"))),
        ("absolute local path in README", "no-local-paths", append_text("README.md", "\nsee " + "/" + "Users/someone/project\n")),
        ("template node drifts from its section contract", "template-contracts", edit_json("templates/templates.json", lambda o: o["templates"]["template.home"]["nodes"][6].update(tone="light"))),
        ("unresolved evidence id", "evidence-ids", edit_json("sections/proof-logo-ticker.json", lambda o: o["evidence"].append("spec.9.9-nonexistent"))),
        ("verbatim source copy pasted into docs", "protected-content", append_text("docs/generation-guide.md", "\nExample heading: \"%s\"\n" % sentence)),
        ("live form endpoint pasted into docs", "protected-content", append_text("README.md", "\nendpoint: %s\n" % endpoint)),
        ("token policy category not in catalog", "token-refs", edit_json("tokens/llm/token-policy.json", lambda o: o["rawValueRestrictions"].update(typography="reference-only"))),
        # R3 availability pins
        ("registry availability loosened (partner.logo -> generation-safe)", "asset-roles", edit_json("assets/asset-roles.json", lambda o: (
            o["roles"]["partner.logo"].update(availability="generation-safe"), o["pinnedAvailability"].update({"partner.logo": "generation-safe"})))),
        ("pin removed from semantic_validate.PINNED_AVAILABILITY", "asset-roles", replace_text("schema/semantic_validate.py", '    "photo.portrait": "blocked-for-generation",\n', "")),
        ("pin removed from verify_all.PINNED_AVAILABILITY", "asset-roles", replace_text("extraction/verify_all.py", '    "brand.wordmark": "clone-only",\n', "")),
        ("registry + validator pin loosened together (verify_all copy still holds)", "asset-roles", lambda r: (
            edit_json("assets/asset-roles.json", lambda o: (o["roles"]["brand.mark"].update(availability="generation-safe"), o["pinnedAvailability"].update({"brand.mark": "generation-safe"})))(r),
            replace_text("schema/semantic_validate.py", '    "brand.mark": "clone-only",', '    "brand.mark": "generation-safe",')(r))),
        ("section generatedAssetRoles drifts from its slots", "asset-roles", edit_json("sections/features-security-ascii.json", lambda o: o["generatedAssetRoles"].append("placeholder.company-logo"))),
        # R8 retrieval
        ("runtime UI flipped eligible in contract + allowlist together", "retrieval-eligible", lambda r: (
            edit_json("components/nav-menu-panel.json", lambda o: o.update(retrievalEligible=True))(r),
            edit_json("tokens/llm/component-allowlist.json", lambda o: [e.update(retrievalEligible=True) for e in o["entries"] if e["id"] == "component.nav-menu-panel"])(r))),
        ("content section marked ineligible in contract + allowlist", "retrieval-eligible", lambda r: (
            edit_json("sections/features-wallet-intro.json", lambda o: o.update(retrievalEligible=False, retrievalIneligibleReason="x" * 40))(r),
            edit_json("tokens/llm/component-allowlist.json", lambda o: [e.update(retrievalEligible=False) for e in o["entries"] if e["id"] == "features.wallet-intro"])(r))),
        ("retrieval pin removed from semantic_validate", "retrieval-eligible", replace_text("schema/semantic_validate.py", '    "component.smooth-scroll": "Runtime scroll', '    "component.smooth-scrollX": "Runtime scroll')),
        # R7 source / semantic
        ("source range shifted by 3 lines", "source-semantic", edit_json("sections/features-earn-collapse.json", lambda o: o["source"].update(lines="%d-%d" % tuple(int(x) + 3 for x in o["source"]["lines"].split("-"))))),
        ("semantic.id no longer the contract id", "source-semantic", edit_json("sections/proof-logo-ticker.json", lambda o: o["semantic"].update(id="proof.logos"))),
        ("unknown field in a section contract (closed schema)", "section-contracts", edit_json("sections/proof-logo-ticker.json", lambda o: o.update(heroClass="x"))),
        # R9 wrapper gate
        ("measured HERO raised to 3100px", "wrapper-gate", edit_json("extraction/measured-values.json", lambda o: o["sectionHeights"]["pages"]["template.home"]["sections"]["hero.waitlist-hero"].update(heightPx=3100))),
        ("measurement removed for one section", "wrapper-gate", edit_json("extraction/measured-values.json", lambda o: o["sectionHeights"]["pages"]["template.home"]["sections"].pop("features.payroll-rise"))),
        ("gate threshold loosened in wrapper_gate.py", "wrapper-gate", replace_text("extraction/wrapper_gate.py", "HERO_ERROR_PX = 3000", "HERO_ERROR_PX = 9000")),
        # R10 tokens
        ("catalog edited by hand (token removed)", "token-catalog", edit_json("tokens/llm/token-catalog.json", lambda o: o["categories"]["spacing"].pop())),
        ("token file changed without regenerating the catalog", "token-catalog", edit_json("tokens/00-foundation/radius.json", lambda o: o["radius"].update(huge={"$type": "dimension", "$value": 999, "evidence": ["spec.0.7-radii-shadows"]}))),
        ("token-policy rule list drifts from the validator", "token-catalog", edit_json("tokens/llm/token-policy.json", lambda o: o["rules"].pop("TOKEN_UNSUPPORTED_FONT"))),
        # R2 leakage patterns
        ("brand pattern deleted from the leakage registry", "leakage-patterns", edit_json("schema/source-leakage-patterns.json", lambda o: o["categories"]["BRAND"]["patterns"].pop(0))),
        ("copy shingles truncated", "leakage-patterns", edit_json("schema/source-leakage-patterns.json", lambda o: o["categories"]["COPY"]["shingleSha256"].__delitem__(slice(0, 50)))),
        # R1 / R4 modes + examples
        ("generation example deleted", "modes", lambda r: os.remove(os.path.join(r, "schema/examples/generated-home.pagespec.json"))),
        ("mode removed from an example", "schema-draft7", edit_json("schema/examples/clone-home.pagespec.json", lambda o: o.pop("mode"))),
        ("source copy pasted into the generation example", "semantic-example", edit_json("schema/examples/generated-home.pagespec.json", lambda o: o["nodes"][1]["content"].update(heading=sentence))),
        # requirement 10: policy binding
        ("enforcing validator edited without re-hashing the policy", "design-policy", append_text("schema/semantic_validate.py", "\n# drift\n")),
        ("non-SaaS repo bound to the SaaS common policy", "design-policy", edit_json("registry.manifest.json", lambda o: o["designPolicy"].update(policyId="n0-saas-design-constraints-common", policyVersion="0.1.0"))),
        ("policy file removed", "design-policy", lambda r: os.remove(os.path.join(r, "policy/design-policy.json"))),
    ]


def run_verify(repo_copy, src_root):
    r = subprocess.run([sys.executable, os.path.join(repo_copy, "extraction/verify_all.py"), "--quick", "--source-root", src_root], capture_output=True, text=True)
    return r.returncode, r.stdout


def main(argv):
    if "--scratch" not in argv:
        print(__doc__)
        return 2
    scratch = os.path.abspath(argv[argv.index("--scratch") + 1])
    src_root = argv[argv.index("--source-root") + 1] if "--source-root" in argv else os.path.dirname(REPO)
    if not os.path.isfile(os.path.join(src_root, "CLONE_SPEC.md")):
        print("source project not found; citation/protected-content drift needs it. Pass --source-root.")
        return 2
    os.makedirs(scratch, exist_ok=True)
    fails = 0
    for i, (name, check, inject) in enumerate(cases(src_root)):
        dst = os.path.join(scratch, "drift-%02d" % i, "design-repo")
        if os.path.exists(os.path.dirname(dst)):
            shutil.rmtree(os.path.dirname(dst))
        shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
        inject(dst)
        code, out = run_verify(dst, src_root)
        line = next((l for l in out.splitlines() if l.startswith(check + " ")), "")
        caught = code == 1 and " FAIL " in (line + " ")
        fails += not caught
        print("%s  %-50s -> %s" % ("CAUGHT" if caught else "MISSED", name, re.sub(r"\s+", " ", line)[:150]))
    code, out = run_verify(REPO, src_root)
    print("%s  unmodified repo -> %s" % ("PASS  " if code == 0 else "FAIL  ", out.strip().splitlines()[-1]))
    fails += code != 0
    print("\nDRIFT PROOF: %s" % ("all injected defects caught, real repo passes" if not fails else "%d problem(s)" % fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
