# Motion primitives

Import from `src/components/motion` (barrel `index.js`). Values come from CLONE_SPEC §3.

## `<Reveal>` — line mask reveal (§3.2)
`<Reveal as="h2" className="type-h2 text-primary" delay={0.2} amount={0}>Text</Reveal>`
- `as` tag (default `div`), `delay` s, `amount` IO threshold (default **0.5**; most sections pass **0**), `onMount` (hero only).
- Splits into `.reveal-line-mask > .reveal-line` per line, each `translateY(110%) → 0`, 1s `cubic-bezier(.16,1,.3,1)`, line *i* at `delay + .06·i`. Reverts to the original text afterwards (`data-reveal="done"`).
- Children: plain text (`<br>` / inline elements OK). Spec delays: tag 0, h2 0.2, body p 0.1.

## `<Appear>` — fade + rise + un-tilt (§3.3)
`<Appear className="span-narrow" delay={1.3} onMount>…</Appear>`
- Props: `as`, `x` (0), `y` (100), `rotateX` (50), `duration` (1), `delay` (0), `onMount` (false), `amount` (0.5, once). Spring `{duration, bounce:0}`; adds `data-appear`. Other props (className/style/ref) pass through.

## `<Handoff>` — drift + dim wrapper (§0.8, §3.5)
`<Handoff tone="inverse"><section …/></Handoff>`
- `tone` `"light"` (overlay → .12) | `"inverse"` (→ .6), `endOpacity` override, `distance` (240). useScroll offset `["end end","end start"]`. y and the overlay are both 0 under reduced motion; y is 0 on phone.

## `<Mirror>` — reflection (§2.0)
`<Mirror height="sm" mask="soft" floor="light" upperClassName="page-grid h-600" reflection={<…/>} overlay={<div className="absolute …"/>}>{content}</Mirror>`
- `height` sm|md|lg|xl or CSS length/number; `mask` soft|deep|short|stage|fade|wide|title; `floor` light|dark|none; `floorRise`; `blur` (5px); `reserve`; `className`, `upperClassName`, `upperStyle`, `reflectionClassName`, `reflectionStyle`.
- Put the same transforms on reflection layers yourself (e.g. share one MotionValue).

## `<SmoothScroll />`
Lenis `{lerp:.06, autoRaf:true, anchors:true}`, only `(min-width:810px)` and no reduced motion. Already mounted in `App.jsx`. Lenis moves the real window scroll, so framer `useScroll` stays in sync. Instance exposed as `window.lenis` when active.

## Hooks (`hooks.js`)
- `useTargetProgress(idOrRef, line)` → MotionValue 0..1 = `clamp((scrollY + lineOffset − offsetTop)/height)`; `line` `"start"|"middle"|"end"` (§3.5). Use with `useTransform(p, [0,1], [a,b])`.
- `useIsPhone()` (`max-width:809.98px`), `usePrefersReducedMotion()`, `useMediaQuery(q)`.
- `entranceDelay(d)` → hero delays counted from navigation start (§3.4). Call once at mount.
- `pageOffsetTop(el)` → untransformed page top.

## CSS helpers in `src/index.css`
`.page-grid`, `.page-frame`, `.span-main|narrow|text|wide`, `.px-page-col` (all work with `tablet:`/`desktop:`), `.type-*`, `.dim-siblings`, `.overview-top-fade`, `.ticker-track`, Mirror vars (`--mirror-*`), `--section-gradient`. Tailwind numeric utilities are px (`h-514` = 514px). Breakpoints: `tablet:` ≥810, `desktop:` ≥1200, `wide:` ≥1920, `max-tablet:` <810, `tablet:max-desktop:` 810–1199.
