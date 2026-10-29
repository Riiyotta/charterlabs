#!/usr/bin/env python3
"""contentHash of the design-policy binding (requirement 10).

sha256 over policy/design-policy.json followed by every file it lists in
enforcedBy (in that order), each as "<path>\\n<bytes>\\n". verify_all (check
design-policy) recomputes it and fails on mismatch.

    python3 extraction/policy_hash.py           # print
    python3 extraction/policy_hash.py --write   # store in registry.manifest.json designPolicy.contentHash
"""
import hashlib
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLICY = "policy/design-policy.json"


def compute(repo=REPO):
    pol = json.load(open(os.path.join(repo, POLICY), encoding="utf-8"))
    h = hashlib.sha256()
    for rel in [POLICY] + list(pol["enforcedBy"]):
        h.update(rel.encode("utf-8") + b"\n")
        with open(os.path.join(repo, rel), "rb") as f:
            h.update(f.read())
        h.update(b"\n")
    return "sha256:" + h.hexdigest()


if __name__ == "__main__":
    v = compute()
    if "--write" in sys.argv:
        p = os.path.join(REPO, "registry.manifest.json")
        m = json.load(open(p, encoding="utf-8"))
        m["designPolicy"]["contentHash"] = v
        with open(p, "w", encoding="utf-8") as f:
            json.dump(m, f, indent=2, ensure_ascii=False)
            f.write("\n")
    print(v)
