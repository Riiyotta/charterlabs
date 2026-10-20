# Sensitivity, licensing and AI-generation rules

The source of this design-repo is a **real, live company's website** (Charter,
charterlabs.io). Its brand, logo mark, wordmark, marketing copy and product
screenshots are proprietary. The people in its photos are real. Its partner logos
(Circle, HiFi, Rhinestone, Turnkey) are third-party trademarks.

This repo captures **only the design language**: layout, tokens, motion, structure
and measured copy budgets. A generator using it must produce original content.

## Hard rules for any generator

1. **Never reproduce the Charter wordmark or logo mark**, in any colour, trace or
   approximation. Use `brand.mark` and `brand.wordmark` with the target project's
   own assets (`project-supplied-only`, pinned).
2. **Never reproduce the real partner logos or name the real partners.** The
   `partner.logo` role is `fictional-placeholder-only` (pinned). It allows invented
   placeholder marks, or the target project's own partners with their permission.
   The validator rejects the four partner names in partner slots.
3. **Never reproduce, edit or imitate the real people's photos.** `photo.portrait`
   is `generate-non-identifiable-or-licensed-stock` (pinned). Use generated,
   non-identifiable people or model-released licensed stock, and record the licence.
4. **Never reuse the proprietary marketing copy.**
   - The repo stores no source text, only **copy budgets** (chars, words, lines and
     item counts measured from the real layout) plus **sha256 fingerprints** of every
     source string of three or more words.
   - `NO_VERBATIM_SOURCE_COPY` rejects verbatim reuse.
   - `NO_SOURCE_BRAND_NAME` rejects the source brand token anywhere: in copy, alt
     text, links, asset refs and `brand.name`.
5. **Never reuse any source image file.** Every role lists its `sourceFiles`, with
   `reuseOfSourceFiles: "forbidden"`. `ASSET_REF_NOT_SOURCE_FILE` rejects them by basename.
6. **Never carry the live form endpoint or the real social profiles.** These are
   fingerprinted, not stored. The original site posts the waitlist to the company's own
   hosted form service. The clone ships a no-op (`fakeSubmit`).
   `config.waitlistEndpoint` is a **required, project-supplied https URL**
   (`WAITLIST_ENDPOINT_PROJECT_SUPPLIED`). Social links are instance data
   (`EXTERNAL_LINK_NOT_PROTECTED`).

## Per-role generation and licensing guidance

| assetRole | policy | what to do |
|---|---|---|
| `brand.mark` | project-supplied-only (pinned) | Target brand's own mark. Never draw the ring mark. |
| `brand.wordmark` | project-supplied-only (pinned) | Target brand's own wordmark. |
| `social.og-image` | project-supplied-only (pinned) | The project's own 1200×630 share image. |
| `device.screen` | generate-original-fictional-ui (pinned) | **Phone UI screenshots: generate an original fictional app UI** in the target brand. Never copy source screens, numbers or layouts. Keep each slot's aspect. |
| `device.screen-reflection` | derive-from-generated-parent | Downscaled reflection of *your* generated screen. |
| `nav.card-image` | generate-original-fictional-ui | Fictional product shots for the mega-menu cards. |
| `nav.ring` | generate-original | An abstract 164×164 object render. |
| `partner.logo` | fictional-placeholder-only (pinned) | **Fictional placeholder marks**, or the project's own permissioned partners. |
| `texture.backdrop` | generate-original | A soft backdrop texture. |
| `photo.lifestyle` | generate-non-identifiable-or-licensed-stock | A landscape or lifestyle image. Licensed stock needs a recorded licence. |
| `photo.product-in-hand` | generate-original-fictional-ui (pinned) | A hand and phone showing a fictional UI. |
| `photo.portrait` | generate-non-identifiable-or-licensed-stock (pinned) | **Generated non-identifiable people or licensed stock.** |
| `photo.portrait-ascii` | derive-from-generated-parent | ASCII render of the slot's own replacement portrait. |
| `photo.reflection` | derive-from-generated-parent | Reflection of the slot's own replacement photo. |

`extraction/verify_all.py` (`asset-roles`) checks the pinned policies against a
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
