# Sensitivity, licensing and AI-generation rules

The source of this design-repo is a **real, live company's website** (Charter,
charterlabs.io). Its brand, logo mark, wordmark, marketing copy and product
screenshots are proprietary. The people in its photos are real. Its partner logos
(Circle, HiFi, Rhinestone, Turnkey) are third-party trademarks.

This repo captures **only the design language**: layout, tokens, motion, structure
and measured copy budgets. A generator using it must produce original content.

## Two modes (PageSpec `mode`, required)

- **`clone`**: a private, faithful reconstruction of the source for fidelity work.
  Real brand, copy, source asset files, partner names and social URLs may be reused.
  Roles marked `blocked-for-generation` (partner logos, real people) are for a
  private, unpublished fidelity build only. The live waitlist endpoint is still
  rejected (the clone itself replaced it with a no-op).
- **`generation`**: a new page for another brand. Everything below applies, and the
  semantic validator enforces it (rule ids in brackets). Patterns come from
  `schema/source-leakage-patterns.json`, which `extraction/build_leakage_patterns.py`
  derives from the real source (file:line evidence; copy hashed as 5-word shingles,
  URLs fingerprinted). Any spec whose `mode` is not exactly `clone` is checked as
  generation (fail closed).

## Hard rules in generation mode

1. **No source brand** (`GENERATION_MODE_BRAND`): the name and every variant found in
   the source (Charter, Charter Labs, Charter Wallet, Charter App, charterlabs, the
   domain), after NFKC / zero-width / quote / dash normalisation; no `brand.*` role;
   no source icon file. Use `placeholder.brand-mark` or `user.supplied-asset`.
2. **No real partners or customers** (`GENERATION_MODE_CUSTOMER`): the four ticker
   partners and the two legal entities named in the FAQ, anywhere; no `partner.logo`
   role or partner file. Use `placeholder.company-logo` with an invented name.
3. **No real people** (`GENERATION_MODE_PERSON`): no portrait role or portrait file
   (or its ASCII/reflection render). Use `fictional.person`.
4. **No real app screens** (`GENERATION_MODE_SCREENSHOT`): no `device.screen`,
   `nav.card-image`, `photo.product-in-hand`, `social.og-image` role or file. Use
   `placeholder.screenshot`.
5. **No other source asset** (`GENERATION_MODE_ASSET`): every media role must be
   `generation-safe` (pinned in code: `PINNED_AVAILABILITY` in both
   `schema/semantic_validate.py` and `extraction/verify_all.py`).
6. **No source copy or claims** (`GENERATION_MODE_COPY`, `GENERATION_MODE_CLAIM`): no
   5-word run of any source string, no whole 3-4 word source phrase, no legacy
   full-string fingerprint match. Speed, fee and yield claims are their own category.
7. **Placeholder URLs only** (`GENERATION_MODE_URL`): no source URL or host, and every
   absolute URL on a reserved `*.example` / `*.invalid` host. This also rejects app
   store, social and embed links (the source has none of those store/embed marks).
8. **Both modes:** `config.waitlistEndpoint` is a required project-supplied https URL
   and never the live endpoint (`WAITLIST_ENDPOINT_PROJECT_SUPPLIED`); external
   links are https (`EXTERNAL_LINK_HTTPS`).

Detection is string-based: normalised exact matches and hashed shingles. A
paraphrase is not caught; a human or model review of generated copy is still
needed. No human has reviewed the pinned patterns.

## Per-role generation and licensing guidance

| assetRole | availability | substitutes in generation | generated-mode guidance |
|---|---|---|---|
| `brand.mark` | clone-only | `placeholder.brand-mark`, `user.supplied-asset` | Generation mode: never the source ring mark or any trace of it. Use placeholder.brand-mark (a simple original mark for the fictional brand) or user.supplied-asset (the operator's own mark). |
| `brand.wordmark` | clone-only | `placeholder.brand-mark`, `user.supplied-asset` | Generation mode: never the source wordmark or name. Set the fictional brand name as placeholder.brand-mark, or use the operator's own wordmark (user.supplied-asset). |
| `social.og-image` | clone-only | `placeholder.screenshot`, `user.supplied-asset` | Generation mode: an original 1200x630 share image of the fictional product (placeholder.screenshot) or the operator's own (user.supplied-asset). |
| `nav.card-image` | clone-only | `placeholder.screenshot`, `user.supplied-asset` | Generation mode: an original fictional app card (placeholder.screenshot); no source UI, numbers or brand. |
| `nav.ring` | clone-only | `generated.illustration`, `user.supplied-asset` | Generation mode: an original abstract object render (generated.illustration); not the source ring. |
| `device.screen` | clone-only | `placeholder.screenshot`, `user.supplied-asset` | Generation mode: an original fictional app screen (placeholder.screenshot) at the slot's measured aspect; never a source screen, layout or figure. |
| `device.screen-reflection` | clone-only | `generated.derived-render` | Generation mode: derive from the slot's own placeholder.screenshot (generated.derived-render: downscale, same crop). |
| `partner.logo` | blocked-for-generation | `placeholder.company-logo` | Blocked for generation: real third-party trademarks. Use placeholder.company-logo (an invented mark and name) only. |
| `texture.backdrop` | clone-only | `generated.illustration`, `user.supplied-asset` | Generation mode: an original soft texture (generated.illustration). |
| `photo.lifestyle` | clone-only | `generated.illustration`, `user.supplied-asset` | Generation mode: an original generated landscape with no identifiable person (generated.illustration), or the operator's licensed photo (user.supplied-asset). |
| `photo.product-in-hand` | clone-only | `placeholder.screenshot`, `generated.illustration`, `user.supplied-asset` | Generation mode: a generated hand + phone with a fictional lock screen (placeholder.screenshot / generated.illustration). |
| `photo.portrait` | blocked-for-generation | `fictional.person` | Blocked for generation: these are real people. Use fictional.person (generated, non-identifiable) only. |
| `photo.portrait-ascii` | blocked-for-generation | `generated.derived-render` | Blocked for generation: an ASCII render of a real person. Derive from the slot's own fictional.person (generated.derived-render). |
| `photo.reflection` | blocked-for-generation | `generated.derived-render` | Blocked for generation: a reflection of a real person/product photo. Derive from the slot's own generation-safe parent (generated.derived-render). |
| `placeholder.brand-mark` | generation-safe | - | A simple original mark and/or the fictional brand name set in the type scale. Must not resemble the source ring mark or wordmark. |
| `user.supplied-asset` | generation-safe | - | An asset the operator/user supplies with rights recorded (their own logo, photo or screen). The generator does not draw it; it only references it. |
| `generated.illustration` | generation-safe | - | An original generated image, object render or texture with no source resemblance and no identifiable person or brand. |
| `placeholder.screenshot` | generation-safe | - | An original fictional app UI for the fictional brand (invented numbers, names and layout). Never a source screen. |
| `fictional.person` | generation-safe | - | A generated, non-identifiable fictional person or avatar. Never a real person and never a source portrait. |
| `placeholder.company-logo` | generation-safe | - | An invented partner/customer mark with an invented name. Never a real company's trademark. |
| `generated.derived-render` | generation-safe | - | A reflection or ASCII render derived from the slot's own generation-safe parent asset. |
| `placeholder.url` | generation-safe | - | Absolute URLs in a generation PageSpec use reserved hosts only: *.example or *.invalid (RFC 2606/6761). Project routes (/contact) and in-page anchors are allowed. |
| `original.copy` | generation-safe | - | All text is written new for the fictional brand within the section's measured budget; no source sentence, 5-word run, claim or name. |

The generation policies (`generationPolicy`) of seven compliance-critical roles are also pinned.
`extraction/verify_all.py` (`asset-roles`) checks the availability pins (registry vs. both code copies) and the pinned policies against a
second, independent list. Swapping a pinned role to another *valid* policy fails;
`prove_drift.py` proves this.

## Licences

- **Inter** (InterVariable.woff2) is under the **SIL Open Font License 1.1 (OFL-1.1)**.
  It may be bundled and referenced.
- Everything else from the source site has no licence for reuse: images, SVG marks,
  copy and the share image.

## Handling

- Keep the repo private. Do not publish it or recommend making it public.
- The zip is a delivery artifact. Never commit it next to the live folder.
