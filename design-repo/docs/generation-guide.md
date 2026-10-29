# Generating a PageSpec

0. **Set `mode`.** `generation` for any page for another brand (the default use).
   `clone` only for a private fidelity rebuild of the source. Every rule below about
   original content is enforced in generation mode (`docs/sensitivity-and-licensing.md`).
1. **Pick the template.** `templates/templates.json` has one template,
   `template.home`, for route `/`. Copy its `nodes` in order. You may drop optional
   nodes, which raises a warning; never add, repeat or reorder them.
2. **Set the node fields from the template node:** `variant` from
   `allowedVariants`, `tone`, `anchorId`, and `handoff` (the observed value or
   `null`). The tone runs light → `transition.light-to-dark` → inverse, and never
   returns to light.
3. **Copy `motion` verbatim** from the section contract (`sections/*.json` →
   `motion`). Motion is not a creative field. The validator requires an exact
   match, and the schema rejects any extra field.
4. **Write original copy** for every field in the section's `content` model, within
   `maxChars` and `maxWords`. `lines` fields have exactly `count` explicit lines.
   Lists have exactly the measured item counts: 5 slides, 3 stats, 3 security rows,
   5 FAQ items with 2–4 paragraphs each, 4 partners, and footer columns of 4/3/3/2
   links. `maxLines` is the line count measured at 1440. It is a render-check:
   the validator enforces characters and words.
5. **Media:** every image is `{assetRole, assetRef, alt}`.
   - The role must be one the slot allows. In generation mode it must also be a
     `generation-safe` role (see the section's `generatedAssetRoles`), and `assetRef`
     must be your project's own file, never a source file.
   - Decorative slots use `alt: ""`.
   - Follow `docs/sensitivity-and-licensing.md` for what each role may contain.
6. **Links:**
   - `/#anchor` links must target a node on the page.
   - Project routes such as `/contact` must exist in *your* project. They are
     unbuilt in the clone.
   - External links are https. In generation mode they use reserved placeholder hosts
     (`*.example`, `*.invalid`) until the operator supplies real ones outside this repo.
7. **Config:** set `config.waitlistEndpoint` to your own https form endpoint. It
   receives `POST {email}` as JSON.
8. **Validate:** `python3 schema/semantic_validate.py your.pagespec.json`. If it
   fails, feed the errors back to the model and retry.

Styling: every colour, size and timing comes from the section and component
contracts. The optional `nodes[].styleTokens` (surface, text, border,
sectionPaddingY, headingStyle, fontFamily, radius) takes token ids from
`tokens/llm/token-catalog.json` only; `tokens/llm/token-policy.json` lists the
TOKEN_* rules (unknown token, raw colour, arbitrary spacing, unsupported font,
theme/token mismatch).

Examples: `schema/examples/generated-home.pagespec.json` (mode=generation, fictional
brand, placeholder assets and URLs) and `schema/examples/clone-home.pagespec.json`
(mode=clone, real brand, partner names and source files; its copy is stand-in text
because this repo never stores the source copy).
