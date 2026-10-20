Source: https://www.charterlabs.io/

# Charter homepage (`/`): clone spec

Measured on the live site with Playwright on 2026-10-20 at **1440×900**, **1280×800** and **390×844**, and cross-checked against the live JS chunks (Next.js 16 / Turbopack, React, Motion (framer-motion), Lenis 1.3.26, Embla Carousel + Autoplay, GSAP-style `SplitText`). The source ships a documented motion-token file (module `24809`). Its values are copied verbatim into §3.

Companion files:
- `/Users/riyaghosh/V3/charterlabs/ASSETS.md`: image/icon map, missing-asset URLs, inline SVG markup.
- `/Users/riyaghosh/V3/charterlabs/reference/screens/`: reference screenshots (1440 full page plus per-section viewports, 390 full page and menu).

Coordinates are written `[left, top(page), width, height]` in CSS px. "1440" means a 1440×900 viewport.

---

## 0. Global system

### 0.1 Breakpoints (from CSS)
| Name | Query | Grid cols | Gutter (`--gutter-x`) | Col gap | `--section-y` |
|---|---|---|---|---|---|
| phone | `< 810px` (`max-width: 809.98px`) | 4 | 20px | 16px | 96px |
| tablet | `≥ 810px` | 8 | 40px | 16px | 112px |
| desktop | `≥ 1200px` | 12 | 32px | 16px | 128px |
| wide | `≥ 1920px` (used only by the payroll blur mask) | 12 | 32px | 16px | 128px |

Extra one-off queries: `min-width: 594px`, `1235px`, `1876px` (ticker widths), `1920px` (payroll mask).
JS breakpoint helpers: `useIsPhone` = `(max-width: 809.98px)`. Lenis and the sticky footer only run at `min-width: 810px`.

### 0.2 Page grid (`.page-grid`)
`display:grid; grid-template-columns: repeat(var(--grid-columns), minmax(0,1fr)); column-gap:16px; width:100%; max-width:1700px; padding-inline:var(--gutter-x); margin-inline:auto`.
`.page-frame` uses the same width, max-width and padding, but not grid.
- 1440: columns are **100px** each. Column *n* left = 32 + (n−1)·116.
- 1280: columns are **86.664px**.
- 390: columns are **75.5px** (4 columns, 20px gutters).

Named spans:
| Class | phone | tablet | desktop | 1440 result |
|---|---|---|---|---|
| `span-main` | 1/-1 | 2 / span 6 | 3 / span 8 | left 264, w 912 |
| `span-narrow` | 1/-1 | 3 / span 4 | 5 / span 4 | left 496, w 448 |
| `span-text` | 1/-1 | 2 / span 6 | 4 / span 6 | left 380, w 680 |
| `span-wide` | 1/-1 | 1/-1 | 2 / span 10 | left 148, w 1144 |
| `px-page-col` | — | — | padding-inline = gutter + 1 col + gap | 148px at 1440, 134.664px at 1280 |

### 0.3 Spacing scale
Tailwind `--spacing: 1px`, so every numeric utility is in px (`pt-128` = 128px, `gap-48` = 48px).
Named tokens: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256.

### 0.4 Fonts
- `@font-face { font-family: inter; src: url(/fonts/InterVariable.woff2) format("woff2"); font-weight: 100 900; font-style: normal; font-display: swap; }`. Live URL: `/_next/static/media/InterVariable_latin-s.p.2gu-elau-8uqe.woff2`. It is preloaded, and `public/fonts/InterVariable.woff2` is the identical file.
- Fallback face: `@font-face { font-family: "inter Fallback"; src: local("Arial"); ascent-override: 89.79%; descent-override: 22.36%; line-gap-override: 0%; size-adjust: 107.89%; }`
- Computed stack on `html`: `inter, "inter Fallback", Inter, ui-sans-serif, system-ui, sans-serif`
- `html`: `font-variation-settings: "opsz" 32; font-feature-settings: "cv03","cv04","cv09","cv11"; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; text-size-adjust: 100%; line-height: 1.5`.
- Headings and `[class*=type-display|type-h]` use `text-wrap: balance`. `p, li, dt, dd` use `text-wrap: pretty`.
- No other font families are loaded. Weights in use: 400, 420, 440, 450, 485, 500, 550. Inter Variable renders these intermediate weights, so do not round them.

### 0.5 Type scale
Letter-spacing values are in em, and computed px are shown in brackets. Each size cell lists desktop ≥1200 / tablet 810–1199 / phone <810. The 1440, 1280 and 390 sizes were measured. Tablet values come from the CSS and were not measured.

| Style | Size (D / T / P) | Weight | Line-height | Letter-spacing | Used for |
|---|---|---|---|---|---|
| `type-display` | 72 / 60 / 44px | 440 | 1 (72px) | −0.03em (−2.16px) | Dark-transition statement |
| `type-h1` | 64 / 54 / 40px | 450 | 1.04 (66.56px) | −0.02em (−1.28px) | Hero h1 |
| `type-h2` | 54 / 46 / 36px | 450 | 1.06 (57.24px) | −0.02em (−1.08px) | All section h2 |
| `type-h3` | 46 / 40 / 32px | 450 | 1.08 (49.68px) | −0.015em (−0.69px) | Logo-section h3, Security statement |
| `type-h4` | 38 / 34 / 28px | 450 | 1.1 (41.8px) | −0.01em (−0.38px) | Payroll statement, mobile menu links |
| `type-h5` | 30 / 26 / 24px | 450 | 1.15 (34.5px) | −0.005em (−0.15px) | "Meet the upgrade.", payroll stat titles on phone |
| `type-h6` | 24 / 22 / 20px | 485 | 1.2 (28.8px) | −0.01em (−0.24px) | FAQ questions, desktop menu links |
| `type-tag` (eyebrow) | 18 / 18 / 16px | 420 | 1.4 (25.2px) | −0.005em (−0.09px) | Eyebrows ("Introducing Charter Wallet") |
| `type-body1` | 21 / 20 / 18px | 450 | 1.38 (28.98px) | 0 | Lead paragraphs, dt/dd |
| `type-body1-strong` | 21 / 20 / 18px | 550 | 1.38 | −0.01em (−0.21px) | Slide titles, payroll stat titles (tablet+) |
| `type-body2` | 17 / 17 / 16px | 400 | 1.5 (25.5px) | 0.005em (0.085px) | FAQ answers, "Supported by…", input |
| `type-body3` | 15 / 15 / 14px | 450 | 1.35 (20.25px) | 0.01em (0.15px) | Nav items, footer |
| `type-caption` | 13 / 13 / 12px | 450 | 1.35 (17.55px) | 0.01em (0.13px) | Menu panel label |
| `type-button` | 17 / 17 / 16px | 500 | 1 (17px) | 0 | "Join Waitlist" |

### 0.6 Color tokens (exact)
Gray ramp: `0 #fff, 50 #fafafa, 100 #f5f5f5, 200 #ebebeb, 300 #d6d6d6, 400 #b3b3b3, 500 #8f8f8f, 600 #6b6b6b, 700 #4d4d4d, 800 #2e2e2e, 900 #1a1a1a, 950 #0d0d0d, 1000 #000`.
Alpha black/white: 4% `#0000000a`, 8% `#00000014`, 12% `#0000001f`, 20% `#0003`, 40% `#0006`, 60% `#0009`, 80% `#000c` (white uses the same alphas).
Status error: `#ff2244`.

Sections set `data-tone`, which swaps these CSS vars:
| Var | `light` (header, hero, intro, logo, send, dark-transition) | `inverse` (overview, earn, payroll, security, faq, footer) |
|---|---|---|
| text primary | `#000` | `#fff` |
| text secondary | `#6b6b6b` | `rgba(255,255,255,.6)` |
| text tertiary | `#8f8f8f` | `rgba(255,255,255,.4)` |
| text disabled | `#b3b3b3` | `rgba(255,255,255,.2)` |
| surface (`bg-surface`) | `#fff` | `#000` |
| surface raised (`bg-raised`) | `#f5f5f5` | `#1a1a1a` (footer bg) |
| border subtle | `rgba(0,0,0,.08)` | `rgba(255,255,255,.08)` |
| border strong | `rgba(0,0,0,.2)` | `rgba(255,255,255,.2)` |

Body bg is `#fff`.

### 0.7 Radii, shadows, filters, gradients
- Radii: xs 4, sm 8, md **16** (FAQ items), card 28, lg **32** (menu image cards), xl **64** (slide image boxes, security card, mobile payroll cards), pill **999px**.
- Blur tokens: `--blur-reveal: 5px` (blurred reflections), `--blur-glass: 10px` (backdrop blurs), `--blur-mirror: 24px` and `--blur-ambient: 48px` (both unused on home).
- Shadows:
  - Waitlist pill: `inset .5px .5px 0 0 rgba(0,0,0,.12), inset -.5px -.5px 0 0 rgba(0,0,0,.12)`
  - Light mirror floor edge: `inset 0 1px 0 0 rgba(0,0,0,.04)`
  - Focused input: `inset 0 0 0 1px <text-primary>`
  - Nothing else uses box-shadow.
- Section background (intro, send): `linear-gradient(180deg, #f5f5f5 0%, #fff 50%)`.
- Payroll stage background: `linear-gradient(to bottom in oklab, transparent 0%, #000 10%)`.
- Every other gradient and mask is listed in its own section below.

### 0.8 Page-level structure (DOM order)
```
body.relative
  header  absolute inset-x-0 top-0 z-10  (NOT fixed/sticky — scrolls away)    [data-tone=light] .nav-drop
  main    relative z-6 bg-surface(#fff) tablet:min-h-svh
    div (view-transition wrapper)
      Handoff(light)  → section#hero-section
      section#intro-section
      Handoff(light)  → section#logo-section
      section#send-section
      section (DarkTransition, no id)
      section#overview-section
      section#earn-section
      section#payroll-section
      Handoff(inverse)→ section#security-section
      section#faq-section
  footer  relative z-5 bg #1a1a1a, tablet:sticky bottom-0  [data-tone=inverse]
```
Handoff wrapper markup: `div.relative.isolate` (style `transform: translateY(y)`) containing the section plus `div.pointer-events-none.absolute.inset-0.z-10.bg-black` (opacity animated). See §3.5.

Measured section boxes (top / height):
| Section | 1440 | 1280 | 390 | Padding |
|---|---|---|---|---|
| header | 0 / 54 | 0 / 54 | 0 / 54 | — |
| hero | 0 / 1059.1 | 0 / 1059.1 | 0 / 872.9 | pt 128 (tablet+; 0 on phone), pb 128 |
| intro | 1059.1 / 720 | 1059.1 / 720 | 872.9 / 749.2 | 0 |
| logo | 1779.1 / 712.5 | 1779.1 / 712.5 | 1622.1 / 670.8 | pt 192, pb 256 (tablet+) / 192 (phone) |
| send | 2491.6 / 1869.7 | 2491.6 / 1869.7 | 2292.9 / 1674.9 | pb 128 |
| dark transition | 4361.3 / 640 | 4361.3 / 640 | 3967.8 / 460 | 0 |
| overview | 5001.3 / 1028 | 5001.3 / 1028 | 4427.8 / 914.5 | pb 128 |
| earn | 6029.3 / 1261.7 | 6029.3 / 1261.7 | 5342.3 / 1246.1 | py 128 |
| payroll | 7290.9 / 1151.7 | 7290.9 / 1151.7 | 6588.3 / 1831.3 | py 128 |
| security | 8442.6 / 1538 | 8442.6 / 1595.9 | 8419.7 / 1634.4 | py 128 |
| faq | 9980.6 / 624 | 10038.5 / 624 | 10054 / 710.2 | py 128 |
| footer | h 532.25 | h 532.25 | h 668.7 | py 192 desktop / 128 tablet / 96 phone |
| **document height** | **11137** | **11195** | **11433** | |

z-index stacking inside main: dark-transition `z-3`, overview `z-4`, payroll `z-3`, security `z-2`, all others `auto`. Header `z-10`, nav overlay `z-9`, main `z-6`, footer `z-5`.

---

## 1. Header / navigation

### 1.1 Desktop and tablet (≥810)
- `header`: `position:absolute; inset-x:0; top:0; z-index:10`, height 54. It is **not sticky**: it scrolls off with the page and has no scroll-state changes, no blur and no shadow.
- Inner bar: `relative z-2 bg #fff`, h 54. The `nav` is `display:flex; height:54px; align-items:flex-start; justify-content:center; padding-top:8px`.
- The row (`relative flex items-center`) is centred: [509, 8, 422, 38] at 1440 and [429, 8, 422, 38] at 1280. Items in order:
  1. "Home" link: [509, 9, 80.4×36]
  2. "Overview" button: [589.4, 9, 103.4×36]
  3. Logo link: 38×38, `rounded-pill`, mark 22×22 black, at [692.8, 8]
  4. "Company" button: [730.8, 9, 105.8×36]
  5. "Contact" link: [836.5, 9, 94.5×36]

  Items are `flex h-36 items-center px-20 type-body3 whitespace-nowrap rounded-pill`, color `#6b6b6b`, 15px/450/20.25px/0.15px.
- **Glide highlight.** An absolutely positioned duplicate row (`inset-0 bg rgba(0,0,0,.04) text #000`, same labels plus a 38px spacer) sits on top. It is clipped by `clip-path: inset(0 Rpx 0 Lpx round 999px)`, so the highlighted item appears as a pill with black text.
  - Default target is the current page ("Home"): `inset(0 342px 0 0 round 999px)`.
  - On mouse hover it moves to the hovered item, for example Overview gives `inset(0 239px 0 80px …)`.
  - L/R animate with a spring `{stiffness:400, damping:36, mass:1}`.
  - Highlight opacity animates 0↔1 over 0.2s when it appears or disappears.
  - Hovering the logo clears the hover target.
- **Nav entrance (home only).** Class `.nav-drop`: `animation: nav-drop 1s cubic-bezier(.16,1,.3,1) 1.5s backwards`, with `@keyframes nav-drop { 0% { transform: translateY(-100px) } }`. Measured: header at −100px until 1.50s, −64px at 1.65s, −9.7px at 1.92s, 0 at 2.55s.
- **Mega menu.** Hovering Home, Overview or Company with a mouse opens `#nav-panel`.
  - Timing: open delay 0.06s on first open (switching is immediate once open); close delay 0.14s after pointer-leave from the header or when hovering a non-menu item; Escape closes it; scrolling more than 48px closes it.
  - Panel: `absolute inset-x-0 top-full bg #fff overflow-clip`. Height animates 0 → auto (measured 362px) with `duration .45s, ease cubic-bezier(.32,.72,0,1)`.
  - Inner: `page-grid pt-48 pb-64` (padding 48px 32px 64px).
  - Every menu column is stacked in the same grid cell (`row-start-1`). The active one cross-fades in at 0.25s and inactive ones fade out at 0.12s.
  - Left column (`col-span-3`, desktop `col-span-4 col-start-2`, so [148, 102, 448×250] at 1440): flex-col, gap 24.
    - Caption `type-caption #6b6b6b` (13px/450/17.55px/0.13px).
    - Then `ul.dim-siblings` flex-col items-start gap 12 of links `type-h6 #000` (24px/485/28.8px/−0.24px).
  - Links stagger in: container `staggerChildren .04, delayChildren .05`. Each `li` goes from `{opacity:0, y:16}` to `{opacity:1, y:0}` with `duration .4s, ease [.32,.72,0,1]`. Hidden transition is 0.12s.
  - Right column (`col-span-5 col-start-4`, desktop `col-span-6 col-start-7`, so [728, 102, 680×250]): flex with gap 16, containing image cards `h-250 flex-1 rounded-lg(32px) bg #f5f5f5 overflow-clip`, image `fill object-cover`. The 2nd card is hidden below 1200px.
  - Menu content:
    - **Home**: caption "Home"; links Wallet `/#intro-section`, Payments `/#send-section`, Finances `/#overview-section`, Security `/#security-section`; images `nav/home-live-activity`, `nav/home-payroll`.
    - **Overview**: caption "Overview"; links Earn `/#earn-section`, Payroll `/#payroll-section`, Expenses `/#overview-section`; images `nav/overview-earn`, `nav/overview-expenses`.
    - **Company**: caption "Company"; links "X (Twitter)" `https://x.com/CharterLabs` (new tab), "LinkedIn" `https://www.linkedin.com/company/charter-labs` (new tab), "FAQ" `/#faq-section`. Media is the **ring card**: a `rounded-lg h-250 flex-1 overflow-clip` card with bg `linear-gradient(180deg,#f5f5f5 0%,#fff 50%)` containing a Mirror (§2.0) of `nav/ring` 164×164. Mirror settings: upper `flex justify-center pt-32`, reflection height 44px, mask `short`, floorRise 45px, floor `light`.
    - **Contact**: plain link to `/contact`.
  - `.dim-siblings a { transition: color .2s }`. While any link is hovered, the others turn tertiary (`#8f8f8f` light, `rgba(255,255,255,.4)` inverse).
- Page overlay while the menu is open: `fixed inset-0 z-9 bg rgba(0,0,0,.2) backdrop-filter: blur(10px)`, fade 0.3s. Clicking it closes the menu.
- Reference screenshot: `reference/screens/1440-nav-overview-open.png`.

### 1.2 Phone (<810)
- Bar: `flex h-54 items-start justify-between px-20 pt-8`.
  - Left: logo link 38×38 at [20, 8].
  - Right: burger button 38×38 at [332, 8]. It holds two bars `absolute h-2 w-20 rounded-pill bg #8f8f8f`, translateY −5px and +5px.
  - When open, both bars go to y 0 and rotate −45deg / +45deg, using spring `{stiffness:400, damping:36, mass:1}`.
- Sheet `#nav-sheet`: `absolute inset-x-0 top-full bg #fff overflow-clip`. Height animates 0 → auto (measured 632px) at 0.45s with `[.32,.72,0,1]`.
- Sheet inner: `flex max-h-[calc(100dvh-54px)] flex-col gap-32 overflow-y-auto px-20 pt-8 pb-24`.
- Tab list: `grid grid-cols-4` (each 87.5px). Tabs are `h-36 type-body3 #6b6b6b` centred: Home, Overview, Company, Contact (Contact is a link). It has the same glide highlight (`clip-path`, bg rgba(0,0,0,.04)). Default tab is Home.
- Tab panel: `grid px-16`. Each panel is flex-col with gap 32:
  - A block `min-h-250 flex-col gap-24` containing caption `type-caption` (12px) and a `ul` flex-col gap 16 of links `type-h4 #000` (28px/450/30.8px/−0.28px). Links use the same stagger as desktop.
  - One image card, `h-250 rounded-lg(32)`.
- While open: `html { overflow: hidden }`; `main` and `footer` get `inert`; the overlay `fixed inset-0 z-9 rgba(0,0,0,.2) blur(10px)` is shown.
- Reference: `reference/screens/390-menu-open.png`.

---

## 2. Sections (DOM order)

### 2.0 Shared component: Mirror (reflections)
Used in Intro, Send, Overview, Earn, Payroll and the nav ring. Structure:
```
div.relative.w-full.overflow-x-clip
  div.relative.z-2.{upperClassName}                 ← the real content
  div.relative (style height: reserve)
    [floor] div.absolute.left-1/2.z-1.-translate-x-1/2   (omitted when floor="none")
            style: top: calc(var(--mirror-floor-rise) * -1) [= -56px]; width: 110%; aspect-ratio: 12; border-radius: 50%;
                   background-image: var(--mirror-floor-{light|dark}); box-shadow: var(--mirror-floor-{light|dark}-edge)
    div.flex.flex-col.justify-end.overflow-clip  (scale: 1 -1 → vertically flipped; inert, aria-hidden)
            style: height: var(--mirror-height-{sm|md|lg|xl}); mask-image: var(--mirror-mask-*); [filter: blur(5px) when blur]
            children: the reflection content (usually the same layout with a pre-made *-reflection image)
    [overlay] (absolutely positioned text placed over the reflection)
```
Tokens:
- Heights: sm 120, md 200, lg 260, xl 300. Floor width 110%, aspect 12:1, rise 56px. At 1440 the floor is [-72, …, 1584×132].
- Floor light: `linear-gradient(180deg, #f5f5f5 0%, rgba(255,255,255,0) 50%)`, edge `inset 0 1px 0 0 rgba(0,0,0,.04)`.
- Floor dark: `linear-gradient(180deg, rgba(255,255,255,.04) 0%, rgba(255,255,255,0) 50%)`, no edge.
- Masks (the reflection is flipped, so 0deg runs from the floor line to the far edge):
  - soft: `linear-gradient(0deg, #000 -50%, rgba(0,0,0,.4) 10%, rgba(0,0,0,.08) 70%, transparent 100%)`
  - deep: `linear-gradient(0deg, #000 0%, rgba(0,0,0,.4) 15%, rgba(0,0,0,.08) 40%, transparent 80%)`
  - short: `linear-gradient(0deg, #000 -35%, transparent 60%)`
  - stage: `linear-gradient(0deg, #000 -15%, rgba(0,0,0,.45) 45%, transparent 90%)`
  - fade: `linear-gradient(0deg, #000 -45%, rgba(0,0,0,.45) 35%, transparent 100%)`
  - wide: `linear-gradient(0deg, #000 -20%, rgba(0,0,0,.4) 20%, transparent 65%)`
  - title: `linear-gradient(0deg, #000 -25%, rgba(0,0,0,.23) 20%, rgba(0,0,0,.06) 45%, transparent 60%)` (unused on home)

### 2.0b Shared component: Reveal (text line reveal) and Appear. See §3.2 and §3.3.

---

### 2.1 Hero: `section#hero-section` (wrapped in Handoff "light")
Classes: `relative w-full bg-surface flex min-h-screen flex-col items-center justify-center overflow-x-clip pb-128 tablet:pt-128`.

1. **Image box**: `flex h-514 w-full items-end justify-center`, at [0, 128, 1440×514].
   - Inner wrapper `w-380 tablet:w-460 shrink-0` (scroll target for the text fade): [490, 44.6, 460×597.4] at 1440. On phone it is [5, 20.5, 380×493.5].
   - Inside it, an Appear div (mount entrance, §3.4) holds `div.relative.aspect-[0.77].rotate-19` (460×597.4, `rotate: 19deg`) with the mask `linear-gradient(185deg, #000 50%, rgba(0,0,0,.62) 70%, rgba(0,0,0,.4) 75%, rgba(0,0,0,.16) 85%, transparent 97%)`.
   - Image: `hero-phone.2560.webp`, fill + `object-cover`, eager, high priority, alt "Handheld iPhone showing the Charter app".
2. **Text grid**: `relative z-1 page-grid gap-y-24 tablet:text-center` (row gap 24), at [0, 642, 1440×289.1]. Its opacity is scroll-linked (§3.5). On phone it is forced to `opacity:1 !important` and left-aligned.
   - `h1.type-h1.text-primary.span-text`: "This is what money should feel like." [380, 642, 680×133.1] (2 lines at 1440 and 1280). Phone: 40px, [20, 514, 350×83.2], start-aligned.
   - `p.type-body1.text-secondary.span-narrow` (tablet+ `text-wrap: balance`): "Your new global wallet for international payments, payroll, and savings." [496, 799.1, 448×58], 2 lines.
   - CTA: Appear `span-narrow` containing the **Waitlist pill** (§2.1.1), form [496, 881.1, 448×50].

#### 2.1.1 Waitlist pill (`form.waitlist`, h 50, width 100% of span-narrow)
- CSS vars: `--open` (0 closed, 1 open; a motion value), `--pill-width: 150px` (230px in the error state), `--waitlist-fill: var(--tone-text-primary)`, `--waitlist-label: var(--tone-surface)`.
  - `@property --waitlist-fill { syntax:"<color>"; inherits:true; initial-value:#000 }`
  - `.waitlist { transition: --waitlist-fill .2s }`
- Pill bg span: `absolute inset-y-0 left-1/2 -translate-x-1/2 rounded-pill` (phone: `left:0; translate:0`).
  - `width: calc(var(--pill-width) + (100% - var(--pill-width)) * var(--open))`
  - `background-image: radial-gradient(224% 716.8% at calc(60.2% - 10.2% * var(--open)) calc(-553.2% + 603.2% * var(--open)), transparent 23.4885%, var(--waitlist-fill) 77.2329%)`
  - Closed, this gives a solid black 150×50 pill; open, it is effectively transparent.
  - Box-shadow: the inset hairlines from §0.7.
- Label button "Join Waitlist": `absolute inset-y-0 left-1/2 w-(--pill-width) -translate-x-1/2 flex items-center justify-center rounded-pill type-button whitespace-nowrap`.
  - Color `var(--waitlist-label)` (white), with `transition: color .2s`.
  - `opacity: calc(1 - var(--open)*4)`.
  - Hidden on phone (`max-tablet:hidden`) unless it is showing a status message.
- **Hover** (`.waitlist:has([data-waitlist-trigger]:not(:disabled):hover)`): `--waitlist-fill` becomes `#fff` and the label becomes `#000`. Measured: fill rgb(18) → 204 at 74ms → 255 at ~240ms; label 237 → 0 over the same time. The result is a white pill with black text and 12% hairline edges.
- **Click**:
  - `--open` animates 0→1 with spring `{stiffness:80, damping:20, mass:1}`. Measured: 0.913 at the first frame after click, 0.95 at 93ms, 0.983 at 294ms, 1 at ~790ms. Width goes 150 → 448.
  - The input is focused after 250ms.
  - The form auto-closes 20s after pointer-leave if the input is empty. Escape also closes it.
- Field layer: `absolute inset-0`, `opacity: calc(var(--open)*2 - 1)`.
  - Input: `size-full rounded-pill bg-transparent pr-56 pl-24 type-body2 text-primary` (17px/400). Placeholder "Email", color `#b3b3b3`. Focus style `box-shadow: inset 0 0 0 1px #000`.
  - Submit: `absolute top-3 right-3 bottom-3 aspect-square rounded-pill bg #000 text #fff` (44×44 at [897, 884]), arrow SVG 16px. Hover `opacity .8` with `transition: opacity .2s cubic-bezier(.4,0,.2,1)`. Pending state shows a spinner.
- Phone (<810): always open (`[data-phone-open]` forces `--open:1`), so it shows the input pill full-width [20, 694.9, 350×50] with the submit circle.
- Success text "Thank you"; error text "Something went wrong" (`#ff2244`, pill width 230), held for 2.5s. Posts JSON `{email}` to `https://submit-form.com/ZQnoBKhLj`.

---

### 2.2 Intro: `section#intro-section` (no Handoff)
- Classes: `relative w-full overflow-clip`, bg `linear-gradient(180deg, #f5f5f5 0%, #fff 50%)`. Height 720 = 600 upper + 120 reflection.
- Mirror settings: height `sm`, mask `soft`, floor `light`. Upper class: `page-grid grid-rows-1 items-end h-420 tablet:h-600 overflow-clip`.
- **Text column** (tablet+ only): `col-span-4 hidden tablet:flex flex-col justify-center gap-24 self-stretch overflow-clip desktop:col-start-2`, at [148, 1059.1, 448×600] at 1440 and [134.7, …, 394.7] at 1280.
  - `div.flex.flex-col.gap-12.overflow-clip` contains:
    - `p.type-tag.text-secondary` "Introducing Charter Wallet" (Reveal, threshold 0) at [148, 1227.8]
    - `h2.type-h2.text-primary` "The new gold standard." (Reveal, threshold 0, delay 0.2), 2 lines, h 114.5
  - `p.type-body1.text-secondary` "A global account to send money fast, receive locally, and manage everything in one secure place." (Reveal, threshold 0, delay 0.1), 3 lines at 1440.
- **Phone column**: `col-span-3 col-start-2 flex min-w-0 flex-col items-start pb-2 tablet:col-span-4 tablet:col-start-5 desktop:col-span-5 desktop:col-start-7`, at [728, …, 564] at 1440.
  - Image `intro-phone.2560.webp` (991×2048): `h-auto w-280 max-w-none tablet:w-full tablet:max-w-420`. That is 420×868 at desktop and 280 wide on phone. Alt "Charter App Home UI".
  - Rest transform is `rotate(-40deg)` (no perspective). Bottom-aligned (`items-end`) and clipped by the 600px upper box.
  - Scroll-driven on tablet and desktop; one-shot appear on phone (§3.5, §3.4).
- Reflection: the same grid and column using `intro-phone-reflection.2560.webp` (496×1025) with the same transforms. It is 120px tall, flipped, with the soft mask.
- Phone (<810): the text block moves below the mirror into `div.page-frame.flex.flex-col.gap-24.overflow-clip.tablet:hidden` (padding 0 20px), using the same three Reveals. Upper height is 420.

---

### 2.3 Logo: `section#logo-section` (wrapped in Handoff "light")
- Classes: `relative w-full bg-surface flex flex-col pt-192 pb-192 tablet:pb-256`.
- `div#send-scroll-trigger` (scroll trigger for Send, §3.5): `pointer-events-none absolute inset-x-0 bottom-0 h-screen`. At tablet only (810–1199) it uses `top:-432px; height:auto`.
- `div.page-grid.gap-y-32.overflow-clip`:
  1. `div.relative.z-1.span-main.pb-4` contains `h3.type-h3.text-primary.text-center` "Your new home base for everyday money. From daily spending to global payments, all in one place."
     - Reveal: delay 0.1, default threshold 0.5.
     - 1440: [264, 1971.1, 912×153], 3 lines: "Your new home base for everyday / money. From daily spending to / global payments, all in one place.".
     - Phone: 32px, [20, 1814.1, 350×172.8].
  2. `div[data-grid-exempt].col-span-full.flex.flex-col.items-center.gap-24.overflow-clip`:
     - `p.type-body2.text-secondary` "Supported by world-class financial partners" [556.6, 2156.1, 326.9×25.5]
     - **Ticker** (§3.7): `div.overflow-hidden.shrink-0.mix-blend-difference` with `mask-image: radial-gradient(60.8974% 656% at 50% 50%, #000 0%, transparent 38.7264%)`.
       - Width: 593px (<594), 1234px (594–1234), **1875px** (1235–1875, so 1440 and 1280), 2516px (≥1876). Height 30. Centered, overflowing the viewport: left −217.5 at 1440, −297.5 at 1280, −101.5 at 390.
       - Track: `flex w-max`, 6 copies of `ul.flex.shrink-0.items-center.gap-48.pr-48` (each 639.73px wide).
       - Each copy holds logos `h-30 w-auto` in order: Circle (117×30), HiFi (86.4×30), Turnkey (112.5×30), Rhinestone (133.2×30).

---

### 2.4 Send: `section#send-section`
- Classes: `relative w-full overflow-clip pb-128`, bg `linear-gradient(180deg,#f5f5f5 0%,#fff 50%)`.
- **Tablet/desktop phones** (`hidden tablet:block`): Mirror with height sm (120), mask soft, floor light. Upper: `flex h-718 justify-center gap-12 overflow-clip pt-48`, [0, 2491.6, 1440×718].
  - Two phones `relative h-670 w-260 shrink-0` with fill + object-cover images. At rest, left is x 454 and right is x 726 (1440), top 2539.6.
    - Left: `currency.2560.webp`
    - Right: `amount.2560.webp`
  - Reflection: the same row using `currency-reflection` / `amount-reflection`. Transforms are scroll-linked (§3.5) and applied to both rows.
  - Section continues at 3329.6 (= section top + 718 + 120).
- **Phone phones** (`page-grid py-128 tablet:hidden`): two `col-span-2 min-w-0` columns, each with `div[data-appear].relative.aspect-[0.39].w-full.max-w-260` (167×428.2 at 390) and a fill image (currency left, amount right). Phone motion is in §3.4 and §3.5.
- **Text + carousel**: `div.flex.flex-col.gap-48.overflow-clip` contains:
  - `div.page-grid.gap-y-16.overflow-clip` at [0, 3329.6, 1440×155.7]:
    - `p.type-tag.text-secondary.col-span-full.desktop:col-span-5.desktop:col-start-2` "Global payments" (Reveal, threshold 0) [148, 3329.6, 564×25.2]
    - `h2#send-heading.type-h2.text-primary.col-span-full.tablet:col-span-6.desktop:col-span-5.desktop:col-start-2` "Sending money has never been easier." (Reveal, threshold 0, delay 0.2), 2 lines [148, 3370.8, 564×114.5]
  - **Carousel** (`role=region aria-roledescription=carousel`): `relative mx-auto h-700 w-full max-w-page(1700)`, [0, 3533.3, 1440×700].
    - Viewport: `cursor-grab active:cursor-grabbing`, padding-inline `var(--gutter-x)`, desktop `px-page-col` (148px at 1440, 134.664 at 1280, 20 on phone). `--slide-dim: 1` on phone, `0.1` on tablet+.
    - Container: `-ml-16 flex touch-pan-y`.
    - Slide: `min-w-0 shrink-0 grow-0 basis-full pl-16 desktop:basis-1/2`, so 580 wide (564 content) at 1440, 497.3 content at 1280, 350 on phone.
    - Article `flex flex-col`:
      - Image box: `flex h-500 justify-center overflow-clip rounded-xl(64px) bg #fafafa`, `p-32` unless the layout is a tilt. `items-start` for layout "top", `items-center` otherwise.
      - Image: `h-auto w-full max-w-400 shrink-0`, `draggable=false`. Tilt-right uses `rotate: 22.5deg`; tilt-left uses `rotate: -22.5deg`.
      - Text block `flex flex-col gap-4 px-20 py-24`: `h3.type-body1-strong.text-primary` + `p.max-w-500.type-body1.text-secondary`.
    - Slides (exact copy):
      1. layout `top`, `recipient` (1982×4096). Title "Pick a recipient. Send in seconds." Body "Choose a saved contact or add a bank recipient in a few taps. Charter routes payouts to supported banks across the US, EU, MXN, and BRL."
      2. layout `center`, `virtual-account` (991×2048). Title "Your own USD & EUR accounts." Body "Get paid like a local with virtual USD/EUR details. Receive from clients or employers abroad, then move funds when you’re ready."
      3. layout `tilt-right`, `currency` (796×2048). Title "One balance, any currency." Body "Select a currency to preview what they’ll receive. Send USDC globally, with clear, real-time conversions before you confirm."
      4. layout `tilt-left`, `amount` (796×2048). Title "Confirm the total. Move instantly." Body "Set the amount and see settlement speed upfront, your USDC moves in seconds. Cashing out? ACH and PIX land fast, with clear totals before you send."
      5. layout `center`, `receipt` (991×2048). Title "A receipt you can trust." Body "Track every step with timestamps, fees, and status. Supported bank payouts today in the US, EU, Mexico, and Brazil."
    - Dots (tablet+): `absolute bottom-0 left-1/2 -translate-x-1/2 flex items-center rounded-pill bg rgba(0,0,0,.2) px-4`, 128×32 at [656, 4201.3].
      - 5 buttons `h-32 w-24 rounded-pill`, each with a `size-10 rounded-pill bg #fff` dot.
      - Active dot opacity 1, others 0.5, with `transition: opacity .3s cubic-bezier(.4,0,.2,1)`.
    - Phone arrows: `absolute right-12 bottom-0 flex gap-8`, two `size-40 rounded-pill bg rgba(0,0,0,.2) text-white` buttons with chevrons (prev rotated 180deg), at [290, …] and [338, …] on 390.
    - Behaviour: §3.8.

---

### 2.5 Dark transition: `section` (no id), between Send and Overview
- Classes: `relative z-3 h-460 tablet:h-640 w-full bg-surface(#fff)`.
- `div#overview-screen-trigger`: `pointer-events-none absolute inset-x-0 bottom-0 z-3 h-screen bg-black`, opacity scroll-linked (§3.5). Because it is 100vh tall and bottom-anchored, it extends above the section.
- `div#overview-dark-trigger`: `absolute inset-x-0 bottom-0 h-[20vh]` (an invisible trigger).
- `div.page-grid.h-full.grid-rows-1.items-center.overflow-clip` contains `div.sticky.top-124.span-text.overflow-clip.pb-8`, which holds `p.type-display.text-primary.text-center` "A global account. That truly goes beyond borders." (Reveal, threshold 0, delay 0.1).
  - 1440: [380, 4569.3, 680×224], 3 lines "A global account. / That truly goes / beyond borders.".
  - Phone: 44px, [20, 4127.8, 350×140].
  - The text sits at sticky top 124px. The black overlay (z-3) fades over it. Text stays black, so it disappears into the black.

---

### 2.6 Overview: `section#overview-section` (inverse)
- Classes: `relative z-4 w-full bg-surface(#000) pb-128`.
- `p.type-h5.text-primary` "Meet the upgrade.": `absolute top-48 left-1/2 z-3 -translate-x-1/2 whitespace-nowrap`, white, 30px. [599.9, 5049.3, 240.2×34.5]. Opacity is scroll-linked (§3.5).
- `div.overflow-clip` contains a Mirror: height lg (260), mask deep, floor dark.
  - Upper: `overview-top-fade flex justify-center overflow-clip tablet:h-640 tablet:items-end`. Mask on the upper:
    - phone: `linear-gradient(#0000 20%, #000000a3 40%, #000 55%)`
    - ≥810: `linear-gradient(#0000 15%, #000000a3 30%, #000 40%)`
  - Phone image: `div.w-full.max-w-560` containing `overview.2560.webp` (1138×1536) `h-auto w-full`. That is 560×755.9, bottom-aligned in the 640 box, alt "Charter app overview of earnings and expenses". On phone the upper height is auto (526.5 at 390).
  - Reflection: `overview-reflection.2560.webp` (901×1214) in the same wrapper, at opacity 0.7, 260 tall.
  - Overlay: `absolute inset-x-0 bottom-0 z-5 page-grid gap-y-24 overflow-clip text-center`:
    - `h2.type-h2.text-primary.span-text` "A single place to handle it all." (Reveal, threshold 0) [380, 5762.1, 680×57.2]. It is 1 line at 1440 and 2 lines at 1280.
    - `p.type-body1.text-secondary.span-narrow` "Manage your payroll, savings and expenses. All in a single and clean overview." (Reveal, threshold 0, delay 0.1) [496, 5843.3, 448×58].

---

### 2.7 Earn: `section#earn-section` (inverse)
- Classes: `relative w-full overflow-clip bg-surface(#000) py-128`.
- Wrapper: `div.flex.flex-col.items-center.gap-48.overflow-clip`.
- Head: `div.page-grid.gap-y-12.overflow-clip.pb-4.text-center`, [0, 6157.3, 1440×155.7]:
  - `p.type-tag.text-secondary.span-text` "Don't let your money sit idle." (Reveal, threshold 0)
  - `h2.type-h2.text-primary.span-text` "Earn up to 4.50% APY on savings." (Reveal, threshold 0, delay 0.2), 2 lines "Earn up to 4.50% / APY on savings."
- **Stage, tablet+** (`hidden w-full max-w-1920 tablet:block`, [0, 6360.9, 1440×802]): Mirror with height md (200), mask stage, floor none, blur (`filter: blur(5px)` on the reflection). Upper uses `mb-4`.
  - Row: `relative flex h-598 w-full shrink-0 items-end justify-between overflow-clip`.
    - Left panel (`data-layer=earn-left`): `relative z-1 flex h-568 w-1/4 justify-center overflow-clip items-end`, 360×568 at 1440.
      - Backdrop `backdrop.2560.webp` (fill, object-cover).
      - Phone `relative aspect-[796/2048] w-full max-w-260 shrink-0` (260×668.9), image `forecast.2560.webp`. Bottom-aligned, so its top overflows and is clipped.
    - Photo (`data-layer=earn-photo`): `absolute inset-x-0 top-0 mx-auto h-full w-1/2 overflow-clip` (720×598), image `photo.2560.webp` fill cover, alt "A hiker sitting on a rock above a lake and autumn hills". z-3 when open, z-0 when closed.
    - Right panel (`earn-right`): same as left but `items-start`, image `earnings.2560.webp`.
  - Reflection: the same row (images with empty alt), flipped, 200 tall, blurred 5px, stage mask.
  - Overlay: `absolute inset-x-0 bottom-64 z-2 page-grid` containing `p.type-body1.text-secondary.text-center.span-text` "Put your money to work with Earn from Charter. Earn up to 4.50% APY on your savings in our vaults. Deposit and withdraw whenever you like." [380, 7041, 680×58]. Its initial opacity is 0 (§3.6).
- **Phone** (`flex w-full flex-col items-center gap-4 overflow-clip tablet:hidden`):
  - Mirror with height sm (120), mask fade, floor none, blur, upper `mb-4`.
  - Row `flex h-600 w-full shrink-0 gap-2`, two cells `relative flex min-w-0 flex-1 items-center justify-center overflow-clip px-24`. The left cell has `pb-124` and the right cell has `pt-124`. Each cell has the backdrop plus a phone (`max-w-260`, aspect 796/2048).
  - Then `page-grid` containing the same paragraph (always visible).

---

### 2.8 Payroll: `section#payroll-section` (inverse)
- Classes: `relative z-3 w-full bg-surface(#000) py-128`.
- Wrapper: `div.mx-auto.flex.w-full.max-w-1920.flex-col.items-center.gap-32.tablet:gap-0`.
- Head: `div.z-1.page-grid.gap-y-12.overflow-clip.text-center.tablet:sticky.tablet:top-188`, [0, 7418.9, 1440×151.7]:
  - `p.type-tag.text-secondary.span-text` "Get paid as you work." (Reveal, threshold 0)
  - `h2.type-h2.text-primary.span-text` "Payroll every hour, day week or month." (Reveal, threshold 0, delay 0.2), 2 lines "Payroll every hour, / day week or month."
- **Stage, tablet+**: `relative z-2 hidden w-full tablet:block`, with bg `linear-gradient(to bottom, transparent 0%, #000 10%)`, at [0, 7570.6, 1440×744]. It holds a Mirror: height xl (300), mask wide, floor none, blur, upper `mb-4 overflow-clip` (440 tall).
  - Photo row (`data-layer=payroll-photos`): `relative flex w-full shrink-0` (scroll-linked y, §3.5).
    - Two cells `relative aspect-[1.92] min-h-440 min-w-0 flex-1 overflow-clip` (720×440 at 1440):
      - left `payroll-portrait.webp` (alt "A woman arranging flowers by a window")
      - right `payday.2560.webp` with `object-position: 44.4% 28.3%` (alt "A hand holding a phone with Charter payment notifications on its lock screen")
    - Center blur: `absolute inset-0 bg rgba(0,0,0,.2) backdrop-filter: blur(10px)` with mask:
      - <1200: `linear-gradient(90deg, transparent 10%, #000 40% 60%, transparent 90%)`
      - ≥1200: `linear-gradient(90deg, transparent 20%, #000 40% 60%, transparent 80%)`
      - ≥1920: `linear-gradient(90deg, transparent 25%, #000 35% 65%, transparent 75%)`
    - Top hairline: `absolute inset-x-0 top-0 z-1 border-t 1px rgba(255,255,255,.12)`.
    - Statement: `absolute inset-x-0 top-1/2 z-1 -translate-y-1/2 flex flex-col items-center gap-16 text-primary mix-blend-overlay`:
      - `h3.type-h4.text-center.max-w-300` "Earn now.<br>Spend later." [623, …, 194.1×83.6]
      - `p.type-body2.text-center.max-w-300` "Never wait on payroll again."
  - Reflection: the same row with `portrait-reflection` / `payday-reflection` (same object-position), without blur, line or statement. 300 tall, blurred 5px, wide mask.
  - Overlay over the reflection: `absolute inset-x-0 top-0 z-5 h-full content-center pb-32 page-grid gap-y-48`:
    - `ul.span-text.flex.flex-col.items-center.gap-32.tablet:flex-row.tablet:items-start.tablet:justify-between.tablet:gap-0` at [380, 8052.1, 680×58]. Its three `li.flex.flex-col-reverse.items-center.whitespace-nowrap.tablet:w-130.tablet:flex-col` items are each 130 wide (lefts 380 / 655 / 930):
      - title `span.type-h5.text-primary.tablet:type-body1-strong` (21px/550 on desktop)
      - label `span.type-body1.text-secondary`
      - Pairs: "Real time"/"Instant", "Your schedule"/"Flexible", "Spend Today"/"Available"
    - `p.type-body1.text-secondary.text-center.span-text` "Waiting weeks for money you already earned doesn’t make sense. With Charter, your pay can arrive as you work so you can spend or save when you need to." [380, 8158.1, 680×86.9]
- **Phone** (`relative z-2 flex w-full flex-col gap-32 py-12 tablet:hidden`):
  - `page-frame flex flex-col gap-8` with two cards `relative h-500 overflow-clip rounded-xl(64px)`:
    - card 1: `flex flex-col items-center justify-end p-32`, `portrait-soft` fill cover, statement (gap 12, h4 28px)
    - card 2: `payday` with object-position 44.4% 28.3%
    - Each card has a `pointer-events-none absolute inset-0 rounded-xl border-3 border rgba(255,255,255,.12)` overlay.
  - Then the same ul and p. On phone the ul is a column with gap 32, and each li is reversed: label (18px) above title (`type-h5` 24px/450).

---

### 2.9 Security: `section#security-section` (inverse, wrapped in Handoff "inverse")
- Classes: `relative z-2 w-full bg-surface(#000) py-128`.
- Wrapper: `div.page-grid.gap-y-48`.
- Head: `div.span-main.flex.flex-col.gap-12.overflow-clip.pb-8.text-center` [264, 8570.6, 912×106.2]:
  - `p.type-body1.text-secondary` "Security that is always on." (Reveal, threshold 0)
  - `h2.type-h2.text-primary` "Highest grade security" (Reveal, threshold 0, delay 0.2)
- `div.col-span-full.grid.grid-cols-subgrid.gap-y-12` contains:
  - **Card**: `relative col-span-full flex h-600 items-center justify-center overflow-clip rounded-xl(64px) p-48 desktop:span-wide`, [148, 8724.8, 1144×600] at 1440, [134.7, …, 1010.7] at 1280, [20, …, 350] on phone.
    - `security-portrait.webp` fill cover (alt "A woman in sunglasses outside a building").
    - `div[data-layer=security-ascii].absolute.inset-0` containing `portrait-ascii.2560.webp` fill cover. Opacity toggles (§3.6).
    - `div[data-layer=security-statement].relative.mix-blend-overlay` containing `h3.type-h3.text-primary.text-center` "Your wallet.<br>Your money." (white, 46px) [600, 8975.1, 240.1×99.4]. Opacity toggles.
    - A duplicate `div.absolute.z-1.mix-blend-overlay` containing `p[aria-hidden]` with the same text and style. Opacity toggles (it is stacked to double the overlay strength).
    - Border overlay: `pointer-events-none absolute inset-0 z-2 rounded-xl border-3 border rgba(255,255,255,.12)`.
  - **List**: `dl.relative.z-2.col-span-full.grid.grid-cols-subgrid.desktop:span-main` [264, 9336.8, 912×515.8]. Rows are `col-span-full grid grid-cols-subgrid gap-y-4`:
    - Rows 1–2: `border-b 1px rgba(255,255,255,.08) pt-48 pb-24`
    - Row 3: `pt-32 pb-48`
    - `dt.type-body1.text-primary.col-span-full.tablet:col-span-3` (332 wide at 1440, left 264)
    - `dd.type-body1.text-secondary.col-span-full.tablet:col-span-5` (564 wide, left 612)
    - Copy:
      1. "100% Non-custodial" — "Charter pairs advanced biometrics, resilient recovery, and cryptographic safeguards in a fully non-custodial wallet. Meaning your funds are controlled by you alone."
      2. "Passkeys & Biometrics" — "Sign in and approve with Face ID or Touch ID. Charter uses passkey signing backed by your device’s secure enclave, so your keys stay protected. No passwords to steal, and no extra steps to remember."
      3. "Account recovery" — "Lose a device or get locked out. You can restore access with secure recovery options, so your wallet isn’t tied to a single phone forever. Your keys stay yours, always."

---

### 2.10 FAQ: `section#faq-section` (inverse)
- Classes: `relative w-full overflow-clip bg-surface(#000) py-128`.
- `div.page-grid.gap-y-32`:
  - `div.span-main.pt-16.tablet:pt-0.desktop:col-span-2.desktop:col-start-3.desktop:pt-16` contains `h2.type-h2.text-primary` "FAQ". It is plain text with no Reveal. Position [264, 10124.6] at 1440.
  - List: `div.span-main.-mx-20.tablet:-mx-24.flex.flex-col.gap-4.p-4.desktop:col-span-6.desktop:col-start-5`, [472, 10108.6, 728×368] at 1440.
  - Each item is `div.overflow-clip.rounded-md(16px)` containing `h3.type-h6` > `button`:
    - Button: `flex w-full cursor-pointer items-center justify-between gap-16 rounded-md px-16 py-20 tablet:px-20 text-start`, color `rgba(255,255,255,.8)`, 24px/485.
    - Closed height is 68.8 at desktop and 64 on phone.
    - Icon: `span.relative.flex.size-18.shrink-0.items-center.justify-center.text-secondary` containing a `h-2 w-12` bar and a `h-12 w-2` bar (`rounded-pill bg-current`, rgba(255,255,255,.6)).
    - Panel: `overflow-hidden`, height 0 ↔ auto, opacity 0 ↔ 1. Content is `type-body2 text-secondary flex flex-col gap-8 px-16 pb-20 tablet:px-20`, with one `<p>` per paragraph.
  - Single-open accordion: clicking one closes the others, and clicking the open one closes it. All items start closed. There is no hover style. Motion is in §3.6.
  - Questions and answers (exact; paragraphs separated by " ¶ "):
    1. "How does Charter work?" — "Charter Wallet is different from other financial apps you may have used before." ¶ "Your Charter Wallet is self-custodial. This means that you own and control access to the money in your wallet. Your ownership is secured using a private cryptographic key, which is generated for you during setup." ¶ "Money in your Charter Wallet is digital currency. It is held in your Charter Wallet as digital dollars, a digital currency issued by Circle Internet Financial." ¶ "We always display the value of your Wallet balance and all transfers in both digital dollars or digital euros, and government-issued currency of your choice, like USD, EUR, or BRL."
    2. "How long do transfers take?" — "Most normal, contact-to-contact (peer-to-peer) transfers take less than five seconds on the Charter Wallet app." ¶ "Most deposit and withdraw (onramp/offramp) transfers take five minutes or less. In some cases, processing can take 1- 2 business days. This will depend on the recipient's bank."
    3. "How secure is my Charter Wallet?" — "With Charter Wallet, you own and control the money in your wallet. Access to your wallet is controlled using a private key from a secure enclave (iPhone) or a trusted execution environment (TEE) (Android)." ¶ "This key is securely generated and stored on your phone, and is protected by your phone’s unique cryptographic security system and your biometrics (Face ID or fingerprints)." ¶ "Your private key is the only way to access your wallet. No one other than you can access your key, including Charter Labs. This means that you are always in control of your wallet. Wallets that work like this are known as self-custody wallets."
    4. "Why is my balance in digital dollars" (no question mark on live) — "We use digital currency to enable global money transfers, regardless of the currency." ¶ "It is held in your Charter Wallet as digital dollars, a digital currency issued by Circle Internet Financial." ¶ "Using digital currency lets you send money globally, regardless of the currency."
    5. "Which payment methods are supported?" — "Learn about the different ways you can add money to your Charter Wallet." ¶ "Charter’s Virtual Bank Accounts lets you receive and deposit money in US dollars, euros, Mexican pesos, or Brazilian reais, even if you don’t live in those countries. *Conditions apply" ¶ "When a deposit arrives to your virtual bank account, it is automatically converted to the primary currency of your Charter Wallet." ¶ "Charter’s Virtual Account’s are offered in partnership with Hifi Bridge LLC."

---

### 2.11 Footer: `footer` (inverse, bg `#1a1a1a`)
- Classes: `relative z-5 w-full overflow-hidden bg-raised tablet:sticky tablet:bottom-0`.
- Because it sits after `main` (z-6) and is sticky to the bottom, main scrolls up and uncovers it. Its inner div is animated (§3.5).
- Inner: `div.page-grid.gap-y-64.py-96.tablet:py-128.desktop:py-192` (padding 192px 32px at 1440; total height 532.25).
  - `div.col-span-full.flex.flex-col.items-start.justify-between.gap-64.desktop:col-span-4`:
    - Logo link (wordmark SVG `h-20 w-auto`, 107.77×20, white; focus-visible opacity .6)
    - `p.type-body3.text-secondary.hidden.desktop:block` "© 2026 Charter Labs Inc. All rights reserved."
  - `nav[aria-label=Footer].dim-siblings.col-span-full.grid.grid-cols-subgrid.gap-y-48.desktop:col-span-8.desktop:col-start-5`. It has four columns `col-span-2 flex flex-col gap-8`, each with `h2.type-body3.text-secondary` and `ul.flex.flex-col.gap-8` of `a.type-body3.text-primary`:
    - **Home**: Wallet `/#intro-section`, Payments `/#send-section`, Finances `/#overview-section`, Security `/#security-section`
    - **Services**: Earn `/#earn-section`, Payroll `/#payroll-section`, Expenses `/#overview-section`
    - **Contact**: Email `/contact`, "Twitter / X" `https://x.com/CharterLabs` (new tab), LinkedIn `https://www.linkedin.com/company/charter-labs` (new tab)
    - **Company**: FAQ `/#faq-section`, "Privacy Policy" `/legal/privacy-policy`
  - `p.type-body3.text-secondary.col-span-full.desktop:hidden`: the same copyright line, shown below 1200.
- Measured rest positions at 1440:
  - Column lefts 518.4 / 727.2 / 936 / 1144.8 (each 216 wide before the scale transform)
  - Logo at x 100.8
  - Column headers at footer-top + 192; links every 28.8px
- 1280: columns at 462.4 / 647.2 / 832 / 1016.8.
- 390: 2×2 grid. Columns are 167 wide at x 20 / 203. Rows are 194.9 apart (gap 48); text is 14px.

---

## 3. Motion system

Libraries on live:
- Motion (framer-motion), using duration-based springs: `{type:"spring", duration, bounce}`.
- Lenis 1.3.26.
- Embla Carousel with the Autoplay plugin.
- A GSAP-style `SplitText.create(el, {type:"lines", mask:"lines", linesClass:"reveal-line", autoSplit:true, aria:"none"})`.

To reproduce in the React clone, install `framer-motion` (or `motion`), `lenis`, `embla-carousel-react` and `embla-carousel-autoplay`, plus a line splitter (GSAP `SplitText`, or a manual line splitter with the same DOM). `rotateX` is applied **without perspective** everywhere (it reads as a vertical squash).

### 3.1 Motion tokens (verbatim from the source's token file)
```js
reveal:      { from:{opacity:0, y:100, rotateX:50, blur:5}, spring:{duration:1, bounce:0}, stagger:.1, threshold:.5 }
appear:      { from:{opacity:0, y:100, rotateX:50}, spring:{duration:1, bounce:0}, threshold:.5 }
revealMask:  { from:{yPercent:110}, duration:1, ease:[.16,1,.3,1], stagger:.06 }   // the variant actually used everywhere
footerReveal:{ from:{opacity:0, y:-100, scale:.9}, startAt:1.35, endAt:.1 }
press:       { spring:{stiffness:80, damping:20, mass:1} }
accordion:   { spring:{duration:.5, bounce:0} }
nav:         { glide:{stiffness:400, damping:36, mass:1}, panel:{duration:.45, ease:[.32,.72,0,1]}, overlay:{duration:.3},
               link:{from:{opacity:0, y:16}, duration:.4, ease:[.32,.72,0,1], stagger:.04}, openDelay:.06, closeDelay:.14 }
smoothScroll:{ lerp:.06 }
hero:        { image:{from:{x:-150, y:300}, duration:2, delay:.5}, title:{delay:1}, body:{delay:1.2}, cta:{delay:1.3}, loadCredit:1 }
waitlist:    { closedWidth:150, messageWidth:230, closeAfter:20, messageHold:2.5 }
intro.phone: { from:{x:-150, y:-150, rotateX:30, rotateY:30, rotate:-60}, rest:{rotate:-40},
               appear:{from:{opacity:0, x:-150, y:-300, rotate:-20, rotateX:40, rotateY:30}, spring:{duration:1.5, bounce:0}, threshold:.5} }
ticker:      { velocity:50 /*px/s*/, hoverFactor:.5 }      // + gap 48, logoHeight 30
send.phones: { from:{x:150, y:-300, scale:1.5, rotateX:40}, appear:{from:{x:260, y:-200}, spring:{duration:1.5, bounce:0}}, parallax:.02 }
slideshow:   { autoplay:8 /*s*/, dimOpacity:.1, duration:35 /*Embla*/ }
overview:    { image:{from:{opacity:0, y:-550}, appear:{from:{opacity:0, y:-450}, spring:{duration:1, bounce:0}}}, reflectionOpacity:.7 }
earn:        { switchAt:96, spring:{duration:1, bounce:0}, photo:{closed:{opacity:0, scale:.8, blur:10}}, parallax:.02 }
payroll:     { photos:{from:{y:500}} }
security:    { switchAt:0, spring:{duration:1, bounce:0} }
handoff:     { y:240, overlay:{light:.12, inverse:.6} }
pageTransition:{ duration:1, ease:[.25,.46,.45,.94], blur:5 }   // cross-page only
```

### 3.2 Text reveal: `Reveal` (all eyebrows, headings and lead paragraphs listed in §2)
- Server HTML renders the element with `data-reveal="pending"`. CSS hides it before JS runs: `html.js [data-reveal=pending]{visibility:hidden; animation:0s linear 4s forwards reveal-failsafe}` with `@keyframes reveal-failsafe{to{visibility:visible}}`, so it is shown after 4s if JS fails.
- On mount the text is split into lines, giving this DOM:
  ```html
  <h2 data-reveal="ready">
    <div class="reveal-line-mask" style="position:relative;display:block;text-align:<inherit>;overflow:clip">
      <div class="reveal-line" style="position:relative;display:block;text-align:<inherit>;will-change:transform;transform:translateY(110%)">line text</div>
    </div>…
  ```
  CSS: `.reveal-line-mask{overflow:clip; overflow-clip-margin:.06em; margin-bottom:-.18em}` and `.reveal-line{padding-bottom:.18em}`. The extra 0.18em keeps descenders unclipped without changing layout height.
- Trigger: IntersectionObserver with `threshold` = the prop (default **0.5**; most sections pass **0**; the Logo h3 uses the default 0.5). It fires once, then disconnects. Hero Reveals use `trigger:"mount"` (§3.4).
- Animation per line: `y: 110% → 0%`, `duration 1s`, `ease cubic-bezier(.16,1,.3,1)` (expo-out). Line *i* starts at `delay + 0.06·i`. After it finishes the split is reverted and `data-reveal="done"`.
- Measured on the Logo h3 (3 lines, line box 57.96px, so start offset 63.75px):
  - Line 1 starts ~108ms after the trigger. Line 2 is +50–60ms later, line 3 +110ms.
  - Line 1 sits at 25.6px at 257ms, 6.25px at 458ms, 0.9px at 708ms, and 0 at ~1.06s.
- Delays used: tag 0, h2 **0.2**, body p **0.1**, Logo h3 0.1, Dark-transition display 0.1. Security and FAQ follow the per-section notes in §2.
- `prefers-reduced-motion: reduce`: no split, shown immediately.

### 3.3 `[data-appear]`: the Appear component
- `data-appear` is only a marker. The motion is a Motion `motion.div`. The CSS hook is `@media (prefers-reduced-motion: reduce){[data-appear]{opacity:1!important; filter:none!important; transform:none!important}}`.
- Default: `initial {opacity:0, x:0, y:100, rotateX:50}` → `{opacity:1, x:0, y:0, rotateX:0}`, spring `{duration:1, bounce:0}`. Trigger is `whileInView` once, viewport `amount 0.5`. Props can override x, y, rotateX, duration, delay, and trigger `"mount"`.
- Elements with `data-appear` on home:
  - Hero image (mount: x −150, y 300, rotateX 0, duration 2, delay 0.5)
  - Hero CTA (mount, delay 1.3, defaults otherwise)
  - Phone-only intro phone (§3.4)
  - Phone-only send phones
  - Phone-only overview image
- A Motion spring with `bounce:0` and `duration:d` is critically damped. With framer-motion use the same config: `transition={{type:'spring', duration:1, bounce:0, delay}}`.

### 3.4 Load and appear sequences
**Hero entrance.** Delays count from navigation start: `entranceDelay(d) = d − min(elapsedSinceNavStart, 1s)` when less than 3s have elapsed. Measured on live with a fast load (domInteractive 77ms):
| t (ms from nav start) | Event |
|---|---|
| 0–500 | Hero image hidden (opacity 0, translate(−150px, 300px)); h1/p lines at translateY(110%); CTA opacity 0; header translateY(−100px) |
| **500** | Hero image starts: opacity 0→1, x −150→0, y 300→0, spring duration **2s** bounce 0. Measured opacity/x: 0.066/−140 @586, 0.39/−92 @786, 0.66/−51 @986, 0.83/−26 @1186, 0.93/−10 @1453, 0.97/−4.6 @1653, 0.99/−1.6 @1920, 1/0 @~2500 |
| **1000** | h1 line 1 mask reveal (1s expo-out); line 2 at **1060** |
| **1200** | Body p line 1; line 2 at 1260 |
| **1300** | CTA Appear: opacity 0→1, y 100→0, rotateX 50→0, spring 1s (opacity 0.21 @1386, 0.61 @1520, 0.90 @1720, 1 @2320) |
| **1500** | Header `nav-drop` CSS animation, 1s cubic-bezier(.16,1,.3,1) from translateY(−100px) (−64 @1653, −24.8 @1786, −9.7 @1920, −1.2 @2186, 0 @~2550) |

**Phone-only one-shot appears:**
- **Intro phone** (in view at amount 0.5): `{opacity:0, x:-150, y:-300, rotate:-20, rotateX:40, rotateY:30}` → `{opacity:1, x:0, y:0, rotate:-40, rotateX:0, rotateY:0}`, spring 1.5s, bounce 0. The reflection does the same.
- **Send phones** (once, when the section top reaches viewport middle, IO rootMargin `0px 0px -50% 0px`): left `{x:-260, y:-200}` and right `{x:260, y:-200}` → `{0,0}`, spring 1.5s, bounce 0. The outer column then drifts `y = ∓0.02 × scrollY` (left negative, right positive). At 390 and scroll 2690 this measured ∓53.8px.
- **Overview image** (same middle-line trigger): `{opacity:0, y:-450}` → `{opacity:1 (reflection .7), y:0}`, spring 1s.

### 3.5 Scroll-linked effects (tablet and desktop unless noted)
Two progress helpers are used:
- `useTargetProgress(id, line)`: `p = clamp((scrollY + lineOffset − elTop)/elHeight, 0, 1)`. `lineOffset` is 0 for "start", vh/2 for "middle", vh for "end". `elTop` is the untransformed `offsetTop` sum.
- Motion `useScroll({target, offset})`.

All of these are linear (`useTransform`) with no easing. Values below were measured at 1440×900, with scroll sampled every 100px.

| Effect | Element(s) | Progress source | Mapping | Measured at 1440 |
|---|---|---|---|---|
| Hero text fade | `#hero-section .page-grid` | Motion `useScroll` on the 460px image wrapper, offset `["start start","end start"]`. Live uses a native `ViewTimeline` | opacity 1→0 (phone: always 1) | opacity 0.74 @200, 0.405 @400, 0.07 @600, 0 @≥800 |
| Handoff (hero, logo, security) | `div.relative.isolate` wrapper + inner black overlay | `useScroll` target wrapper, offset `["end end","end start"]` (0 when wrapper bottom is at viewport bottom, 1 when it reaches viewport top) | translateY 0→240px (phone: 0); overlay opacity 0→0.12 (light) / 0→0.6 (inverse security) | hero wrapper: y 10.9 @200, 117.6 @600, 224 @1000, 240 @≥1059; overlay 0.0055→0.12. Logo: starts @~1592, 240 @2492. Security: starts @~9081, 240 / 0.6 @~9981 |
| Intro phone tilt | `[data-layer=intro-phone]` and `-reflection` | `#hero-section`, line start → p = scrollY/1059 | x −150→0, y −150→0, rotate −60→−40deg, rotateX 30→0, rotateY 30→0 | @0: `translateX(-150px) translateY(-150px) rotate(-60deg) rotateX(30deg) rotateY(30deg)`; @500: −79.18/−79.18/−50.56/15.84/15.84; @≥1059: `rotate(-40deg)` |
| Send phones | `[data-layer=send-left/right]` and reflections | `#send-scroll-trigger` (100vh tall at the bottom of the logo section, top 1592 at 1440), line start | left x −150→0 (right +150→0), y −300→0, scale 1.5→1, rotateX 40→0 | starts @1592; @2000: x ∓82, y −164, scale 1.2733, rotateX 21.87; none @≥2492 |
| Dark overlay | `#overview-screen-trigger` (black, 100vh) | `#overview-dark-trigger` (bottom 20vh = 180px of the dark-transition section, top 4821), line **middle** | opacity 0→1 | 0 until 4371; 0.16 @4400, 0.72 @4500, 1 @≥4551 |
| "Meet the upgrade." | `#overview-section > p` | same trigger, line start | opacity 1→0 | 1 until 4821; 0.56 @4900, 0 @≥5001 |
| Overview phone drop | `[data-layer=overview-screen]` | `#overview-screen-trigger` (top 4101, h 900), line start | y −550→0; opacity 0→1 (reflection 0→0.7) | @4200: y −489.5, op 0.11; @4600: −245, 0.554; @5000: −0.6, 0.999 |
| Earn phone drift (all sizes) | inner phone of each Earn panel | raw scrollY | left y = +0.02·scrollY, right y = −0.02·scrollY | e.g. ±122px at scrollY 6100 |
| Payroll photo rise | `[data-layer=payroll-photos]` and reflection | `#payroll-section`, line **end** (top 7291, h 1152) | translateY 500→0 | 500 until 6391; 452.7 @6500, 235.7 @7000, 18.7 @7500, 0 @≥7543 |
| Footer reveal (≥810, no reduced motion) | `footer > div` | `p = clamp((1.35 − (maxScroll − scrollY)/footerH) / (1.35 − 0.1), 0, 1)`, footerH 532.25, maxScroll 10237 | opacity 0→1, translateY −100→0, scale 0.9→1 | starts @~9518; @9600: op 0.122, y −87.8, s 0.912; @10000: 0.724 / −27.6 / 0.972; done @~10184 |

Sticky elements:
- Dark-transition statement: `sticky; top:124px` inside its 640px section.
- Payroll head: `tablet:sticky; top:188px; z-1`. The photo stage (z-2, black gradient) scrolls over it.
- Footer: `tablet:sticky; bottom:0`.

### 3.6 Scroll-triggered toggles (springs, reversible)
- **Earn stage.** Closed when `earn-section.getBoundingClientRect().top <= -96` (scrollY ≥ 6125.3 at 1440). It reverses when scrolling back above that line. Spring is duration 1, bounce 0.
  - Left panel: `x: 0% → 100%`
  - Right panel: `x: 0% → -100%`
  - Photo: `opacity 1 → 0, scale 1 → .8, filter blur(0px) → blur(10px)`, z-index 3 → 0
  - Overlay paragraph: opacity 0 → 1
  - Measured translateX on the left panel: 3.8% @+71px of scroll past the trigger, 50% @~0.37s, 90.8% @~0.9s, 100% at settle.
  - Reflections mirror this.
  - References: `1440-y6029-earn-open.png`, `1440-y6300-earn-closed.png`.
- **Security card.** On when `security-section` top ≤ 0 (scrollY ≥ 8442.6 at 1440). The ASCII image, the statement and its duplicate go opacity 0 ↔ 1, spring 1s bounce 0.
- **FAQ accordion.** Panel `height 0↔auto` and `opacity 0↔1`. The vertical icon bar goes `rotate 0↔90deg` (plus becomes minus). Spring is duration 0.5, bounce 0 (about 50% at 0.1s, 97% at 0.3s). Before hydration, panels have `.faq-panel-pending{opacity:0;height:0;overflow:hidden}`.

### 3.7 Logo ticker (marquee)
- `.ticker-track{animation: ticker var(--ticker-duration) linear infinite}` with `@keyframes ticker{to{transform:translateX(calc(-100% / var(--ticker-copies)))}}`.
- `--ticker-copies: 6`. `--ticker-duration: 12.82s` = `setWidth 641 / velocity 50`.
- Measured WAAPI: duration 12820ms, linear, infinite, keyframe `translateX(-16.6667%)`. Movement is ~50px/s (−512.9 → −562.9 in 1s).
- Hover: `animation.updatePlaybackRate(0.5)` on pointerenter and back to 1 on pointerleave.
- Reduced motion: no animation.

### 3.8 Send slideshow (Embla)
- Options: `{loop:true, align:"start", duration:35}`, Embla defaults otherwise (`dragThreshold:10`, `containScroll:"trimSnaps"`).
- Autoplay: `{delay:8000, playOnInit:false, stopOnInteraction:false, stopOnMouseEnter:true}`. It plays only while the carousel is ≥25% visible (IntersectionObserver threshold 0.25) and is disabled under reduced motion. Verified on live: it advanced to slide 2 after ~8s in view.
- Slide dimming (tablet+), recomputed on every scroll frame: each `article` gets `opacity = dim + (1−dim)·visibleFraction`, where `dim = --slide-dim` (0.1 on tablet+, 1 on phone). `visibleFraction` is the horizontal overlap of the article with the viewport's content box (padding-left −1px to padding-right +1px), divided by article width. At rest on desktop, slides 1–2 are at 1.0 and the rest at 0.1.
- Dots: clicking does `scrollTo(i)`. The active dot is opacity 1, others 0.5 (0.3s transition).

### 3.9 Smooth scroll (Lenis)
- `new Lenis({ lerp: 0.06, autoRaf: true, anchors: true })`, created only when `(min-width: 810px)` matches and reduced motion is off. It is destroyed or re-created when those queries change. On phone `html` has no `lenis` class and scrolling is native.
- Token note: after one wheel tick the page covers half the distance in ~205ms and 90% in ~670ms.
- Lenis CSS (include it verbatim):
  ```css
  html.lenis, html.lenis body { height: auto; }
  .lenis:not(.lenis-autoToggle).lenis-stopped { overflow: clip; }
  .lenis [data-lenis-prevent], .lenis [data-lenis-prevent-wheel], .lenis [data-lenis-prevent-touch],
  .lenis [data-lenis-prevent-vertical], .lenis [data-lenis-prevent-horizontal] { overscroll-behavior: contain; }
  .lenis.lenis-smooth iframe { pointer-events: none; }
  ```
- Without Lenis: `@media (prefers-reduced-motion:no-preference){html:not(.lenis){scroll-behavior:smooth}}`.

### 3.10 Hover / interaction states (complete list)
| Element | Change | Timing |
|---|---|---|
| Nav item / logo (desktop) | Glide pill (rgba(0,0,0,.04) bg, text #6b6b6b → #000 via the clipped overlay) moves to the hovered item | spring stiffness 400, damping 36; opacity 0.2s |
| Nav menu link lists, footer nav | `.dim-siblings`: non-hovered links → tertiary | `color .2s` (ease) |
| Waitlist "Join Waitlist" | pill fill #000 → #fff, label #fff → #000 | `--waitlist-fill .2s`, `color .2s` (ease) |
| Waitlist submit | opacity 1 → .8 | `opacity .2s cubic-bezier(.4,0,.2,1)` |
| Ticker | speed ×0.5 | immediate playbackRate |
| Slideshow | `cursor: grab` / `grabbing`; drag to scroll; autoplay pauses on mouseenter | — |
| Slide dots | — (click only) | dot opacity .3s |
| FAQ buttons | no hover style | accordion spring 0.5s |
| Focus-visible | rings `2px` in tone primary (nav items, buttons, waitlist with ring-offset 2); footer and menu links get `underline` on focus-visible; footer logo opacity .6 | — |
No hover underlines, shadows or scale effects are used anywhere on the page.

### 3.11 Reduced motion
- `.nav-drop`, `.ticker-track` and the `reveal-failsafe` animation are disabled.
- `[data-appear]` is forced to opacity 1 with no transform or filter.
- Reveals show immediately.
- Lenis is off.
- Handoff y is 0. The overlay still dims.
- Toggles use `duration:0`. The footer reveal is static.

---

## 4. Responsive notes (1280 vs 1440 vs 390)

### 1280 (desktop rules, 12 columns of 86.664px)
- Everything scales by column width.
- Hero text at x 340 / w 600; span-narrow 442.7 / 394.7.
- Intro text column 134.7 / 394.7.
- Send text 134.7 / 497.3. Carousel padding 134.664px; slide article 497.3 wide; image box 497.3×500.
- Payroll li lefts 340 / 575 / 810.
- Security card 1010.7 wide. dt 292 wide at 237.3; dd 497.3 at 545.3.
- FAQ list [418.7, …, 648]. Items 640 wide.
- Nav row is centred at x 429.
- Line breaks change in:
  - Overview h2 (2 lines)
  - Earn paragraph (3 lines)
  - Security dt/dd (rows 1–3 are 115.9 tall)
  - Footer columns 170.4 wide

### 390 (phone, 4 columns of 75.5px, gutter 20)
- Header switches to the logo + burger bar.
- Hero: pt 0, image box still 514 tall (image 380 wide), text start-aligned, waitlist always open full-width.
- Intro: phone image 280 wide (rotated −40deg, appears on view); text below the mirror; upper height 420.
- Logo: h3 32px; ticker container 593 wide.
- Send: phones in a 2-column grid (`py-128`) with appear plus parallax; carousel shows one slide (350 wide) and prev/next arrows instead of dots; no dimming.
- Dark transition: section 460 tall, display text 44px.
- Overview: image appears once; upper height auto; text 36px h2.
- Earn: static two-panel phone row (600 tall, gap 2) with blurred reflection; no photo, no switch.
- Payroll: two 500px rounded cards plus a stacked stats list; no photo-row motion.
- Security: card 350×600, dt/dd stacked full-width.
- FAQ: list −20px side margin; items 382 wide; button padding 20px 16px.
- Footer: not sticky, no reveal (`opacity:1; transform:none`); 2×2 link grid; copyright at the bottom; padding 96px 20px.

---

## 5. What could not be measured / caveats
- **Tablet range (810–1199)** was not loaded. Its values (8 columns, 40px gutter, tablet type sizes, tablet-only classes such as `tablet:max-desktop:-top-432` on `#send-scroll-trigger`) come from the CSS.
- **Hero entrance timings** depend on load speed by design (`entranceDelay`). The table in §3.4 is for a fast load. On a load slower than 1s the delays shrink by up to 1s. On in-site navigation (more than 3s since start) the full delays apply.
- **Spring-driven opacity and filter on the Earn photo and Security layers** run through WAAPI, so inline styles only show the final value. Their curve is the Motion spring `{duration:1, bounce:0}` given in the source.
- **The Earn photo z-index swap** (3 → 0) happens immediately on toggle (class change), not animated.
- **Exact `--open` overshoot** of the waitlist spring: the first sampled frame after click was already 0.913 (Playwright click latency). The end state and spring constants are exact.
