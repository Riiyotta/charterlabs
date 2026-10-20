# https://www.charterlabs.io/ (homepage only), as cloned in this project

Source: https://www.charterlabs.io/ (homepage only), as cloned in this project
Status: **measured-from-live** · production approved: **false**
1 routes · 1 templates · 12 unique sections

> Generated from `ia.json` by `build.mjs`. Edit the JSON, not this file.

## Shape of the site

The largest 1 template (Homepage) accounts for 1 of 1 routes (100%). The remaining 0 routes span 0 templates.

| template | routes | share |
|---|---:|---:|
| Homepage | 1 | 100% |

## Page chrome

**1 routes carry chrome = `full`** — Homepage.

## Sections by reuse

How widely a section is shared determines whether it belongs in a shared
component library or stays local to its page.

| section | category | templates | routes | implementation | scope |
|---|---|---:|---:|---|---|
| `chrome.header` | CHROME | 1 | 1 | `src/components/Header.jsx` | Present on the single built route, above <main>. |
| `hero.waitlist-hero` | HERO | 1 | 1 | `src/components/Hero.jsx (+ Waitlist.jsx, wrapped by motion/Handoff.jsx)` | First section of main on the single built route. |
| `features.wallet-intro` | FEATURES | 1 | 1 | `src/components/Intro.jsx` | Second section on the single built route. |
| `proof.logo-ticker` | PROOF | 1 | 1 | `src/components/Logo.jsx (wrapped by motion/Handoff.jsx)` | Third section on the single built route. |
| `features.send-slideshow` | FEATURES | 1 | 1 | `src/components/Send.jsx (+ send/Slideshow.jsx)` | Fourth section on the single built route. |
| `transition.light-to-dark` | TRANSITION | 1 | 1 | `src/components/DarkTransition.jsx` | Fifth section on the single built route; every section after it is inverse tone. |
| `features.finances-overview` | FEATURES | 1 | 1 | `src/components/Overview.jsx` | Sixth section on the single built route. |
| `features.earn-collapse` | FEATURES | 1 | 1 | `src/components/Earn.jsx` | Seventh section on the single built route. |
| `features.payroll-rise` | FEATURES | 1 | 1 | `src/components/Payroll.jsx (+ styles/payroll.css)` | Eighth section on the single built route. |
| `features.security-ascii` | FEATURES | 1 | 1 | `src/components/Security.jsx (wrapped by motion/Handoff.jsx)` | Ninth section on the single built route. |
| `support.faq-accordion` | SUPPORT | 1 | 1 | `src/components/Faq.jsx` | Last section of main on the single built route. |
| `chrome.footer` | CHROME | 1 | 1 | `src/components/Footer.jsx` | Present on the single built route, after <main>. |

**0 shared sections** appear in more than one template and belong in a component library.

**12 single-use sections** appear in exactly one template. Building these
as "reusable" components up front would be speculative — keep them page-local
until a second caller actually appears.

## Templates

### Homepage — `template.home`

1 route · `/` · chrome: **full**

| # | category | section | |
|---:|---|---|---|
| 1 | CHROME | `chrome.header` | page-local |
| 2 | HERO | `hero.waitlist-hero` | page-local |
| 3 | FEATURES | `features.wallet-intro` | page-local |
| 4 | PROOF | `proof.logo-ticker` | page-local |
| 5 | FEATURES | `features.send-slideshow` | page-local |
| 6 | TRANSITION | `transition.light-to-dark` | page-local |
| 7 | FEATURES | `features.finances-overview` | page-local |
| 8 | FEATURES | `features.earn-collapse` | page-local |
| 9 | FEATURES | `features.payroll-rise` | page-local |
| 10 | FEATURES | `features.security-ascii` | page-local |
| 11 | SUPPORT | `support.faq-accordion` | page-local |
| 12 | CHROME | `chrome.footer` | page-local |

## Section reference

### CHROME

_Site navigation and footer that frame the page; outside <main>._

**`chrome.header`** — Absolute (non-sticky) 54px header, light tone: centred pill nav (Home / Overview / Company mega-menus with image cards, plus a Contact link) with a snapping highlight pill; on phone a logo + burger opening a tabbed sheet. Drops in from -100px ~1.77s after load.

· Present on the single built route, above <main>. · appears on 1 routes · implemented by `src/components/Header.jsx`

**`chrome.footer`** — Inverse footer (#1a1a1a), sticky to the bottom at >=810px so main scrolls up to uncover it while it scales/fades in; wordmark, copyright and a four-column link nav (2x2 on phone).

· Present on the single built route, after <main>. · appears on 1 routes · implemented by `src/components/Footer.jsx`

### HERO

_Page-opening block with the headline and primary call to action._

**`hero.waitlist-hero`** — Full-height light hero wrapped in a light Handoff (drifts down and darkens to 0.12 as it scrolls away): tilted hero phone image entering on load, h1 + lead paragraph line-reveals, and the expandable email waitlist pill.

· First section of main on the single built route. · appears on 1 routes · implemented by `src/components/Hero.jsx (+ Waitlist.jsx, wrapped by motion/Handoff.jsx)`

### PROOF

_Social proof: partner/backer logos._

**`proof.logo-ticker`** — Light-Handoff-wrapped h3 statement over an infinite marquee of four partner logos at 50px/s (no hover slowdown).

· Third section on the single built route. · appears on 1 routes · implemented by `src/components/Logo.jsx (wrapped by motion/Handoff.jsx)`

### FEATURES

_Product capability modules, each a heading + lead paragraph + phone/photo visual with scroll-linked motion._

**`features.wallet-intro`** — Light intro block with a section gradient: eyebrow + heading + paragraph beside a phone that tilts from -60deg to -40deg with scroll, mirrored by a reflection.

· Second section on the single built route. · appears on 1 routes · implemented by `src/components/Intro.jsx`

**`features.send-slideshow`** — Light payments block: two reflected phones that settle from scale 1.5 / y -300 with scroll, then an eyebrow + h2 and a 5-slide Embla carousel (8s autoplay while >=25% visible, off-screen slides dimmed to 0.1, dots; arrows on phone).

· Fourth section on the single built route. · appears on 1 routes · implemented by `src/components/Send.jsx (+ send/Slideshow.jsx)`

**`features.finances-overview`** — First inverse block: a small caption that fades out while a reflected phone drops in from y -550, followed by h2 + paragraph.

· Sixth section on the single built route. · appears on 1 routes · implemented by `src/components/Overview.jsx`

**`features.earn-collapse`** — Inverse block: a photo between two phones that parallax at +/-0.02 x scroll; 96px past the section top the side panels slide apart, the photo blurs/shrinks away and an overlay paragraph fades in (reversible 1s spring).

· Seventh section on the single built route. · appears on 1 routes · implemented by `src/components/Earn.jsx`

**`features.payroll-rise`** — Inverse block: sticky heading that a black-gradient stage scrolls over, a two-photo row (with reflection) rising from y 500, a centre statement and a three-item stat list; stacked cards on phone.

· Eighth section on the single built route. · appears on 1 routes · implemented by `src/components/Payroll.jsx (+ styles/payroll.css)`

**`features.security-ascii`** — Inverse-Handoff-wrapped block: rounded portrait card whose ASCII-art layer and statement fade in when the section reaches the viewport top (reversible 1s spring), followed by a definition list of security points.

· Ninth section on the single built route. · appears on 1 routes · implemented by `src/components/Security.jsx (wrapped by motion/Handoff.jsx)`

### TRANSITION

_Non-content blocks whose job is to change the page's tone or pacing._

**`transition.light-to-dark`** — 640px block with a sticky display-size statement while a full-viewport black overlay fades in, flipping the page from light to inverse tone.

· Fifth section on the single built route; every section after it is inverse tone. · appears on 1 routes · implemented by `src/components/DarkTransition.jsx`

### SUPPORT

_Help content that answers objections._

**`support.faq-accordion`** — Inverse FAQ: plain h2 beside a five-item single-open accordion (0.5s spring height/opacity, plus-icon bar rotates 90deg).

· Last section of main on the single built route. · appears on 1 routes · implemented by `src/components/Faq.jsx`
