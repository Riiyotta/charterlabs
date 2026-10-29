# Changelog

## 2.0.0 — 2026-10-29 (baseline revision: R1-R4, R7-R10, common-policy binding)

Baseline audit before: 7 pass / 14 fail. After: all pass (see README for the commands).

- **Mode (R1):** PageSpec `mode: "clone" | "generation"` is required and closed;
  `pageSpecVersion` 1.0.0 -> 2.0.0 (breaking: a required field). The former single
  example was a fictional (Fernway) page, so it became the **generation** example
  (`schema/examples/generated-home.pagespec.json`) rather than a clone example; a new
  `schema/examples/clone-home.pagespec.json` carries the real brand, partner names and
  source asset files (copy is stand-in text: the repo still never stores source copy).
- **Generation-mode leakage rules (R2):** eight GENERATION_MODE_* rules replace
  NO_VERBATIM_SOURCE_COPY, NO_SOURCE_BRAND_NAME, ASSET_REF_NOT_SOURCE_FILE and
  EXTERNAL_LINK_NOT_PROTECTED (which applied in every mode and so blocked clone
  fidelity). EXTERNAL_LINK_HTTPS keeps the https check in both modes; the live
  waitlist endpoint stays rejected in both modes. Patterns are derived by
  `extraction/build_leakage_patterns.py` from the real source with file:line
  evidence (9 brand variants, 6 partner/entity names, 36 source asset files,
  457 copy + 194 claim shingle hashes, 14 URL / 4 host fingerprints).
  - The new shingle check found that the old Fernway example still contained three
    close paraphrases of source copy (5-word runs) that the old full-string
    fingerprints missed; they were rewritten. It also found two citation anchors in
    `extraction/measured-values.json` that quoted source alt text; they were shortened.
- **Asset availability (R3):** every role has a closed availability, substitutes and
  generated-mode guidance; 9 generation-safe roles added (23 roles). Pinned in code in
  `verify_all.py` and `semantic_validate.py` and cross-checked with the registry.
  `reuseOfSourceFiles` became `sourceFileReuse {clone, generation}`. Section contracts
  list `generatedAssetRoles`; every media slot offers a generation-safe role.
- **R7:** closed `source {id, tag, file, lines}` / `semantic {id, category}` generated
  by `extraction/build_source_semantic.py`; `verify_all` re-reads every range.
  Closed `schema/section-contract.schema.json`.
- **R8:** `retrievalEligible` on every contract and allowlist entry; the two runtime
  utilities (nav menu panel, smooth scroll) are ineligible, pinned in both validators.
  No section contract is runtime UI.
- **R9:** `extraction/wrapper_gate.py` (thresholds pinned) wired into `verify_all`;
  `sectionHeights` measured at 1440 from the built clone. No section needed
  decomposition or a whitelist (hero 1059px; largest share 17.6%).
- **Tokens (R10):** catalog regenerated from all 152 leaves of the four token layers +
  themes; new optional `nodes[].styleTokens` with five TOKEN_* rules (policy lists them).
- **Common policy:** `category: consumer-app`, `policy/design-policy.json`
  (non-SaaS, evidence recorded), `designPolicy.contentHash` checked by `verify_all`.
  Agent attestation, not a human sign-off.
- Adversarial suite: 9 controls, 85 mutations, 11 wrapper-gate cases. `prove_drift.py`:
  41 injected defects. 26 `verify_all` checks.
- Honest limits: detection is string-based (paraphrase not caught); nobody reviewed
  the pinned patterns by hand; visual parity was not measured; heights only at 1440.

## 1.0.0 — 2026-10-20 (initial build, from scratch)

- Built every layer from evidence: CLONE_SPEC.md, ASSETS.md, the clone's src/, tailwind.config.js, index.html and ia.json.
- Counts:
  - 152 tokens (foundation, semantic, component, layout) and 2 themes (light, inverse).
  - 8 primitives, 11 components and 12 sections.
  - 1 template (`template.home`, 12 structured nodes) and 1 route.
  - 2 linked-but-unbuilt routes, documented and not invented: `/contact` and `/legal/privacy-policy`.
  - 24 graph rules (23 error, 1 warn) and 14 asset roles (7 pinned).
  - 155 citations, each with a `{path, lines, anchor}` check.
- Applied the 10 QA corrections measured on the live site after the spec (`qa.01`–`qa.10`) as overrides of CLONE_SPEC.
- Follow-up the same day: the clone's `Logo.jsx` now drops the ticker hover slowdown, so `qa.01` is implemented. Logo.jsx citations were re-anchored after the line shift, and the clone's motion README Handoff note was corrected (`qa.05`).
- Real-company protection:
  - Copy is encoded as budgets plus 77 sha256 fingerprints. No source text ships.
  - The live form endpoint and the social URLs are fingerprinted only.
  - `config.waitlistEndpoint` is required and project-supplied.
  - Brand-token and partner-name rejection; source asset files are banned by basename.
- Adopted the section ids of the concurrent `ia.json` (created during this build).
  - verify_all checks IA parity whenever ia.json sits next to the repo.
- Re-cited the waitlist hazard after the clone replaced its live POST with a local `fakeSubmit()` no-op during this build.
- Fixed a validator bug the adversarial suite caught during the build: object-typed content fields (the header menus and waitlist labels) were not walked, so a real social URL in the header was missed.
