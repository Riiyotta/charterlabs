# Changelog

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
