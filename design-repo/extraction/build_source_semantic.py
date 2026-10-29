#!/usr/bin/env python3
"""Generate each section contract's closed `source` (provenance) and `semantic`
(AI-facing taxonomy) objects (R7) from the real implementing file.

source   {id, tag, file, lines}: the root element the section's component renders,
         found in its implementedBy file (first <section|header|footer|div ...> after
         `export default function`, through its matching closing tag at the same indent).
semantic {id, category}: id == the contract id, category == the contract category.
source.id is a provenance id ("src:<Component>/<tag>") and never equals semantic.id.

    python3 extraction/build_source_semantic.py [--source-root DIR]           # write into sections/*.json
    python3 extraction/build_source_semantic.py [--source-root DIR] --check   # exit 1 on drift
verify_all.py (check source-semantic) re-reads every range from the real files.
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def locate(root, rel):
    lines = open(os.path.join(root, rel), encoding="utf-8").read().split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("export default function"))
    for i in range(start, len(lines)):
        m = re.match(r"^(\s*)<(section|header|footer|div|main|nav)\b", lines[i])
        if m:
            ind, tag = m.group(1), m.group(2)
            for j in range(i + 1, len(lines)):
                if lines[j].startswith(ind + "</%s>" % tag):
                    return tag, i + 1, j + 1
    raise ValueError("no root element found in %s" % rel)


def derive(root, c):
    rel = c["implementedBy"]
    tag, a, b = locate(root, rel)
    comp = os.path.splitext(os.path.basename(rel))[0]
    return ({"id": "src:%s/%s" % (comp, tag), "tag": tag, "file": rel, "lines": "%d-%d" % (a, b)},
            {"id": c["id"], "category": c["category"]})


def main(argv):
    root = argv[argv.index("--source-root") + 1] if "--source-root" in argv else (os.environ.get("DESIGN_REPO_SOURCE_ROOT") or os.path.dirname(REPO))
    if not os.path.isdir(os.path.join(root, "src")):
        print("source project not found")
        return 2
    bad = 0
    for fn in sorted(os.listdir(os.path.join(REPO, "sections"))):
        p = os.path.join(REPO, "sections", fn)
        c = json.load(open(p, encoding="utf-8"))
        src, sem = derive(root, c)
        if "--check" in argv:
            if c.get("source") != src or c.get("semantic") != sem:
                print("drift: %s" % fn)
                bad += 1
            continue
        out = {}
        for k, v in c.items():
            if k in ("source", "semantic"):
                continue
            out[k] = v
            if k == "category":
                out["source"], out["semantic"] = src, sem
        with open(p, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("%-38s %s %s:%s" % (c["id"], src["tag"], src["file"], src["lines"]))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
