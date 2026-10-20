# Charter homepage design-repo (AI-ready PageSpec system)

A machine-validated design system extracted from a clone of the **Charter** homepage
(charterlabs.io, single route `/`). An LLM uses it to compose *new, original* pages
in the same visual language: it may only instantiate allowlisted sections, in the
template's order, with measured copy budgets, closed motion fields and closed asset
roles. It never reuses the source company's brand, copy, people or partners.

**Status:** `design-review-pending` · `productionApproved: false` · see `registry.manifest.json`.

> **Real company.** The source is a real, live company. Read
> [`docs/sensitivity-and-licensing.md`](docs/sensitivity-and-licensing.md) before using
> anything here. Do not publish this repo or make it public.

## Counts (recomputed from disk by `extraction/verify_all.py`, check `readme-counts`)

<!-- counts:start -->
| item | count |
|---|---|
| tokens | 152 |
| primitives | 8 |
| components | 11 |
| sections | 12 |
| templates | 1 |
| routes | 1 |
| linkedUnbuiltRoutes | 2 |
| assetRoles | 14 |
| graphRules | 24 |
| citations | 155 |
| copyFingerprints | 77 |
<!-- counts:end -->

## Layout

```
registry.manifest.json      ids, versions (which are machine-checked), counts, entry points
tokens/00-foundation/       color, typography, spacing, radius, breakpoint, elevation, gradient, motion
tokens/10-semantic/         tone roles (text/surface/border) swapped by data-tone
tokens/20-component/        mirror, waitlist, nav, slideshow, faq, card, footer
tokens/30-layout/           page grid, named spans, section padding/heights
tokens/themes/              light.json, inverse.json (resolve every role to a foundation token)
tokens/llm/                 component-allowlist, token-catalog, token-policy
primitives/ components/     8 primitives, 11 components (content-agnostic contracts)
sections/                   12 section contracts: content model + copy budgets, motion, responsive, tone, handoff
templates/                  templates.json (template.home, 12 structured nodes), routes.json
compatibility/graph.json    24 rules with severity, tone model, cross-section dependency, adjacency
assets/asset-roles.json     closed assetRole enum + generation/licensing policy per role
schema/                     pagespec.schema.json (Draft-07), example.pagespec.json, semantic_validate.py,
                            protected-content.json (hashes only), page-meta.contract.json, tests/
extraction/                 measured-values.json (external citation ledger), verify_all.py, prove_drift.py
docs/                       sensitivity-and-licensing.md, generation-guide.md
```

## How a page is validated

1. **Draft-07 schema** (`schema/pagespec.schema.json`) checks shape. Everything is
   `additionalProperties: false`, including the motion blocks. Every text field has
   `maxLength` set to its measured character budget, and every media field is
   `{assetRole, assetRef, alt}` with a closed role enum.
2. **Semantic validator** (`schema/semantic_validate.py`) checks what the schema cannot.
   - It cross-references the declared template's real node list: order,
     required and optional nodes, repeats, variants and anchor ids.
   - It enforces the **tone sequence**: light up to and including
     `transition.light-to-dark`, then inverse, with no light section after it.
   - It enforces the **Handoff rules**: a Handoff may be dropped but never added or
     retoned, its tone must match the section, and another `<main>` section must
     follow it.
   - It checks the Send/Logo scroll-trigger dependency and exact motion contracts.
   - It checks word budgets and list counts.
   - It enforces real-company protection: verbatim-copy fingerprints, brand tokens,
     source asset files, the live endpoint and the real social URLs.

   Every rule id exists in `compatibility/graph.json` with a severity, and
   `verify_all.py` fails if the two drift.

```bash
python3 schema/semantic_validate.py path/to/page.json   # exit 1 on error
python3 schema/tests/adversarial_test.py                # 5 controls + 43 mutations
python3 extraction/verify_all.py                        # every check, incl. citations
python3 extraction/prove_drift.py --scratch <empty dir> # proves the drift checks fail on bad input
```

Requires Python 3.9+ and `jsonschema`.

## Evidence and provenance

The evidence comes from:
- **CLONE_SPEC.md**, measured with Playwright on the live site at 1440, 1280 and 390;
- **ASSETS.md**;
- the clone's `src/`, `tailwind.config.js` and `index.html`;
- **ia.json**, written by a concurrent ia-builder run during this build. Its section ids were adopted.

Each contract cites evidence ids that resolve in `extraction/measured-values.json`.
Each id is `{path, lines, anchor}`, with the path relative to the project root.
`verify_all.py` checks three things: the file exists, the range is within the file,
and the anchor text is *inside* the range. That last check catches in-range-but-wrong
citations. When the source project is not beside the repo, as in a zip or a standalone
copy, the check **warns instead of failing**.

### QA corrections (override CLONE_SPEC; ids `qa.01`–`qa.10` in measured-values.json)

These were measured on the live site after the spec was written, and the repo encodes them.

| id | correction | clone source status |
|---|---|---|
| qa.01 | Logo ticker has **no** hover slowdown (`hoverPlaybackRate: 1`). | Implemented: `Logo.jsx` `Ticker` has no pointer handlers (fixed after the first build). |
| qa.02 | Nav highlight (and the phone tab highlight) renders one spring frame, then snaps. | Implemented (`Header.jsx` `useGlide(..., { snap: true })`). |
| qa.03 | Hero h1/paragraph Reveal fire in view at amount 0.5; the image and CTA run on mount. | Implemented (`Hero.jsx`). |
| qa.04 | nav-drop starts ~1.77s after navigation start: 1s expo-out from −100px. | Implemented (`index.css` `.nav-drop`, `Header.jsx`). |
| qa.05 | Under reduced motion the Handoff overlay stays 0 and the drift is 0. | Implemented (`Handoff.jsx`). The clone's own `motion/README.md` still says the overlay dims. |
| qa.06 | `text-wrap-style: balance` for headings and `pretty` for p/li/dt/dd. | Implemented (`index.css` base layer). |
| qa.07 | Footer at rest (scale 1): columns at 496/728/960/1192, logo at x 32, at 1440. | Implemented (`Footer.jsx` grid columns 5/7/9/11). |
| qa.08 | Phone intro-phone Appear observes `#intro-section` at amount 0.5. | Implemented (`Intro.jsx` `useInView`). |
| qa.09 | Partner logo ratios come from the 160px-wide files (160×41, 160×56, 160×43, 160×36). | Implemented (`Logo.jsx` `LOGOS`). |
| qa.10 | Reveal starts ~1 frame (~16ms) after the threshold is crossed. | Implemented (`Reveal.jsx` `requestAnimationFrame`). |

## Structural notes (documented, not normalised away)

- **One route, no router.** `src/main.jsx` renders `App` directly.
- **Two linked-but-unbuilt routes:** `/contact` (header, phone sheet, footer) and
  `/legal/privacy-policy` (footer). They are listed in `templates/routes.json`.
  They are *not* templates and must not be invented: a PageSpec gives them as
  project-route hrefs that the target project supplies.
- **The dark transition has no id.** It hosts `#overview-screen-trigger` and
  `#overview-dark-trigger`, and is the only light→inverse handoff.
- **`#send-scroll-trigger` lives in the Logo section**, so Send depends on Logo
  directly preceding it (`SEND_REQUIRES_LOGO_TRIGGER`).
- **Waitlist form:** the original site posts `{email}` to the company's own hosted
  form service. The clone now ships a no-op (`Waitlist.jsx` `fakeSubmit()` resolves
  after 600ms with no request). This repo never contains the live URL, only its
  fingerprint. `config.waitlistEndpoint` is **required and project-supplied**.
- **External links** (the company's X and LinkedIn profiles) are instance data that
  a generated page must replace. Both URLs are fingerprinted and rejected.
- **Composition policy:** header, hero, dark transition and footer are required.
  The other eight sections may be omitted (warning `OPTIONAL_NODE_OMITTED`) but
  never added, repeated or reordered. Only the full 12-section composition was measured.
- **Unmeasured:** the tablet range (810–1199) comes from CSS only. Hero timings
  depend on load speed. `darkOverlayFade` and `meetCaptionFade` run at every width in
  the clone, but were not measured on phone.

## Versions

`allowlistVersion` and `pageSpecVersion` are machine-checked by `verify_all.py`.
`repositoryVersion` is documentation-only. See `versionFieldNote` in the manifest.

## Packaging

`design-repo.zip` sits next to this folder. It is built with the CLI `zip` (no
`__MACOSX`/`.DS_Store`), regenerated last after verification, and never committed
alongside this folder (see `.gitignore`).
