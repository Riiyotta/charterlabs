Source: https://www.charterlabs.io/

# Asset manifest — Charter homepage

The live site serves every raster through a custom Next image loader:
`/images/<path>.<ext>` → `/_img/images/<path-without-ext>.<width>.webp`, with widths
`96,160,256,384,512,640,828,1080,1440,1920,2560`. The `.2560.webp` variant is the largest and is
capped at the source's intrinsic size, so some files are smaller than 2560px (dimensions below are
the real pixel sizes of the files in `public/images/`).

Font: `public/fonts/InterVariable.woff2` is byte-identical (md5 `303d7327d865357eb0324acf880fe96e`)
to the live `https://www.charterlabs.io/_next/static/media/InterVariable_latin-s.p.2gu-elau-8uqe.woff2`.

## 1. Already in `public/images/` (mapped to live source paths)

| public/images file | px (w×h) | Live source path | Used in | Notes |
|---|---|---|---|---|
| hero-phone.2560.webp | 1058×1396 | /images/home/hero-phone.png | Hero | fill/object-cover in 0.77-aspect box rotated 19deg, masked |
| intro-phone.2560.webp | 991×2048 | /images/home/intro-phone.png | Intro (upper) | intrinsic attrs width=991 height=2048 |
| intro-phone-reflection.2560.webp | 496×1025 | /images/home/intro-phone-reflection.webp | Intro (reflection) | width=496 height=1025 |
| circle.2560.webp | 780×200 | /images/home/logos/circle.png | Logo ticker | h-30 → 117×30 |
| hifi.2560.webp | 576×200 | /images/home/logos/hifi.png | Logo ticker | 86.4×30 |
| turnkey.2560.webp | 360×96 | /images/home/logos/turnkey.png | Logo ticker | 112.5×30 |
| rhinestone.2560.webp | 888×200 | /images/home/logos/rhinestone.png | Logo ticker | 133.2×30 |
| currency.2560.webp | 796×2048 | /images/home/send/currency.png | Send phones (left) + slide 3 | |
| currency-reflection.2560.webp | 167×430 | /images/home/send/currency-reflection.png | Send reflection (left) | low-res on live too |
| amount.2560.webp | 796×2048 | /images/home/send/amount.png | Send phones (right) + slide 4 | |
| amount-reflection.2560.webp | 167×430 | /images/home/send/amount-reflection.png | Send reflection (right) | |
| recipient.2560.webp | 1982×4096 | /images/home/send/recipient.png | Slide 1 | width=1982 height=4096 |
| virtual-account.2560.webp | 991×2048 | /images/home/send/virtual-account.png | Slide 2 | |
| receipt.2560.webp | 991×2048 | /images/home/send/receipt.png | Slide 5 | |
| overview.2560.webp | 1138×1536 | /images/home/overview/overview.png | Overview phone | width=1138 height=1536 |
| overview-reflection.2560.webp | 901×1214 | /images/home/overview/overview-reflection.webp | Overview reflection | width=901 height=1214 |
| backdrop.2560.webp | 1172×1472 | /images/home/earn/backdrop.png | Earn side panels (behind phones) | object-cover |
| forecast.2560.webp | 796×2048 | /images/home/earn/forecast.png | Earn left phone | |
| earnings.2560.webp | 796×2048 | /images/home/earn/earnings.png | Earn right phone | |
| photo.2560.webp | 1920×1280 | /images/home/earn/photo.jpg | Earn centre photo (hiker) | |
| payroll-portrait.webp | 2560×1706 | /images/home/payroll/portrait.webp | Payroll photo row, left (desktop) | = reference `portrait.2560.webp` (same md5) |
| portrait-reflection.2560.webp | 596×395 | /images/home/payroll/portrait-reflection.webp | Payroll reflection, left | |
| payday.2560.webp | 2533×2048 | /images/home/payroll/payday.png | Payroll photo row, right + phone card 2 | object-position 44.4% 28.3% |
| payday-reflection.2560.webp | 598×481 | /images/home/payroll/payday-reflection.webp | Payroll reflection, right | object-position 44.4% 28.3% |
| portrait-soft.2560.webp | 2560×1706 | /images/home/payroll/portrait-soft.png | Payroll phone card 1 (<810px only) | |
| security-portrait.webp | 1128×788 | /images/home/security/portrait.jpg | Security card base photo | = reference `portrait(1).2560.webp` (same md5) |
| portrait-ascii.2560.webp | 1128×788 | /images/home/security/portrait-ascii.png | Security card ASCII overlay | |

## 2. NOT in `public/images/` — must be downloaded

### Nav mega-menu / mobile sheet images (shown on hover of Home/Overview/Company, and in the mobile menu)

| Suggested filename | Full URL (largest variant) | Intrinsic (from code) | Used in |
|---|---|---|---|
| nav-home-live-activity.webp | https://www.charterlabs.io/_img/images/nav/home-live-activity.2560.webp | 3600×2400 attr | Home menu, card 1 (alt "Charter Live Activity widget on a phone lock screen.") |
| nav-home-payroll.webp | https://www.charterlabs.io/_img/images/nav/home-payroll.2560.webp | 2400×1300 attr | Home menu, card 2 (desktop ≥1200 only) |
| nav-overview-earn.webp | https://www.charterlabs.io/_img/images/nav/overview-earn.2560.webp | 2400×1300 attr | Overview menu, card 1 |
| nav-overview-expenses.webp | https://www.charterlabs.io/_img/images/nav/overview-expenses.2560.webp | 2400×1300 attr | Overview menu, card 2 (desktop only) |
| nav-ring.webp | https://www.charterlabs.io/_img/images/nav/ring.2560.webp | 164×164 attr (file is small, 18.9 KB) | Company menu "ring" mirror card |

All return HTTP 200. Smaller variants: replace `.2560.` with `.1920.`/`.1080.`/`.640.`/`.384.`/`.160.`.

### Favicons / social

| URL | Type | Notes |
|---|---|---|
| https://www.charterlabs.io/icons/icon-light.svg | image/svg+xml, 845 B | `<link rel="icon" type="image/svg+xml" media="(prefers-color-scheme: light)">` |
| https://www.charterlabs.io/icons/icon-dark.png | image/png 192×192 | `<link rel="icon" sizes="192x192" media="(prefers-color-scheme: dark)">` |
| https://www.charterlabs.io/icons/apple-touch-icon.png | image/png 180×180 | `<link rel="apple-touch-icon" sizes="180x180">` |
| https://www.charterlabs.io/social/charter-wallet.png | og/twitter image 1200×630 | optional (meta only) |
| /favicon.ico | — | 404 on live; none exists |

`icon-light.svg` content (verbatim):
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="281" height="282" fill="none"><g clip-path="url(#a)"><path fill="#000" d="M140.525.956C63.142.956.481 63.704.481 141s62.66 140.044 140.044 140.044S280.481 218.384 280.481 141c0-77.383-62.66-140.044-139.956-140.044M240.607 199.63c-17.703 10.429-32.251 24.889-42.68 42.679-11.568 19.719-32.951 32.952-57.402 32.952-24.45 0-45.922-13.233-57.49-32.952-10.428-17.702-24.888-32.25-42.679-42.679-19.718-11.568-32.951-32.951-32.951-57.49 0-24.538 13.233-45.921 32.951-57.402 17.703-10.429 32.25-24.889 42.68-42.679 11.566-19.719 32.95-32.952 57.488-32.952 24.539 0 45.922 13.233 57.402 32.951 10.429 17.703 24.889 32.25 42.68 42.68 19.718 11.567 32.951 32.951 32.951 57.401s-13.233 46.01-32.951 57.49Z"/></g><defs><clipPath id="a"><path fill="#fff" d="M.481.956h280v280.088h-280z"/></clipPath></defs></svg>
```

### Head metadata (live)
- `<title>Charter - Global Neobank</title>`
- description / og:description / twitter:description: "Providing a seamless, cost-effective, and accessible global payment platform. Send and receive money across borders instantly and with near-zero fees."
- og:url https://www.charterlabs.io, og:type website, twitter:card summary_large_image
- og/twitter image alt: "A hand holding a phone with the Charter Wallet app, next to the Charter logo and the words “A wallet built for you.”"

## 3. Videos
None. The homepage loads no `<video>`, no Lottie, no canvas. All motion is CSS/JS transforms on images.

## 4. Inline SVGs (verbatim from the live DOM)

### 4.1 Charter mark (nav centre logo + mobile nav logo) — rendered `size-22` (22×22) inside a 38×38 link, `fill: currentColor` (black)
```svg
<svg viewBox="0 0 18 18" fill="currentColor" aria-hidden="true" class="size-22"><path d="M9 0C4.02691 0 0 4.03254 0 9C0 13.9675 4.02691 18 9 18C13.9731 18 17.9944 13.9731 17.9944 9C17.9944 4.02691 13.9675 0 9 0ZM15.4318 12.7678C14.2941 13.438 13.3592 14.3673 12.689 15.5106C11.9456 16.7778 10.5713 17.6283 9 17.6283C7.42866 17.6283 6.04881 16.7778 5.30538 15.5106C4.63517 14.373 3.70588 13.438 2.56258 12.7678C1.29537 12.0244 0.444931 10.6502 0.444931 9.07322C0.444931 7.49625 1.29537 6.12203 2.56258 5.38423C3.70025 4.71402 4.63517 3.78473 5.30538 2.64143C6.04881 1.37422 7.42303 0.52378 9 0.52378C10.577 0.52378 11.9512 1.37422 12.689 2.64143C13.3592 3.7791 14.2885 4.71402 15.4318 5.38423C16.699 6.12766 17.5494 7.50188 17.5494 9.07322C17.5494 10.6446 16.699 12.03 15.4318 12.7678Z"></path></svg>
```

### 4.2 Charter wordmark (footer logo) — `h-20 w-auto` → renders 107.77×20, white (`currentColor` in inverse tone)
```svg
<svg viewBox="0 0 97 18" fill="currentColor" aria-hidden="true" class="h-20 w-auto"><path d="M9 0C4.02691 0 0 4.03254 0 9C0 13.9675 4.02691 18 9 18C13.9731 18 17.9944 13.9731 17.9944 9C17.9944 4.02691 13.9675 0 9 0ZM15.4318 12.7678C14.2941 13.438 13.3592 14.3673 12.689 15.5106C11.9456 16.7778 10.5713 17.6283 9 17.6283C7.42866 17.6283 6.04881 16.7778 5.30538 15.5106C4.63517 14.373 3.70588 13.438 2.56258 12.7678C1.29537 12.0244 0.444931 10.6502 0.444931 9.07322C0.444931 7.49625 1.29537 6.12203 2.56258 5.38423C3.70025 4.71402 4.63517 3.78473 5.30538 2.64143C6.04881 1.37422 7.42303 0.52378 9 0.52378C10.577 0.52378 11.9512 1.37422 12.689 2.64143C13.3592 3.7791 14.2885 4.71402 15.4318 5.38423C16.699 6.12766 17.5494 7.50188 17.5494 9.07322C17.5494 10.6446 16.699 12.03 15.4318 12.7678Z"></path><path d="M31.7211 17.4775C30.1508 17.4775 28.786 17.1332 27.6266 16.4445C26.482 15.7409 25.5868 14.7602 24.9411 13.5026C24.31 12.2301 23.9945 10.7329 23.9945 9.01123C23.9945 7.30449 24.3174 5.81484 24.9631 4.54227C25.6235 3.2697 26.548 2.28159 27.7367 1.57794C28.9254 0.874284 30.2976 0.522457 31.8531 0.522457C33.1299 0.522457 34.2746 0.761999 35.2872 1.24108C36.2998 1.72017 37.1363 2.39388 37.7966 3.26222C38.457 4.11559 38.8753 5.13364 39.0514 6.31638H36.0796C35.8008 5.35821 35.2798 4.61713 34.5167 4.09313C33.7683 3.55416 32.8511 3.28468 31.7651 3.28468C30.7965 3.28468 29.9453 3.51673 29.2116 3.98084C28.4925 4.44496 27.9348 5.1037 27.5386 5.95707C27.1424 6.81044 26.9442 7.82849 26.9442 9.01123C26.9442 10.1491 27.1424 11.1521 27.5386 12.0205C27.9348 12.8738 28.4925 13.5401 29.2116 14.0192C29.9453 14.4833 30.7965 14.7153 31.7651 14.7153C32.8657 14.7153 33.805 14.4458 34.5827 13.9069C35.3752 13.3679 35.9035 12.6418 36.1677 11.7285H39.0954C38.89 12.8664 38.4424 13.8694 37.7526 14.7378C37.0776 15.6061 36.219 16.2798 35.1771 16.7589C34.1498 17.238 32.9978 17.4775 31.7211 17.4775Z"></path><path d="M42.7035 17.2081H40.0179V0.5H42.7255V7.55152C43.063 7.01255 43.5326 6.58587 44.1343 6.27147C44.7507 5.9421 45.4551 5.77741 46.2476 5.77741C47.583 5.77741 48.5956 6.18912 49.2854 7.01255C49.9898 7.83598 50.342 8.95883 50.342 10.3811V17.2081H47.6564V11.0324C47.6564 10.4036 47.561 9.88705 47.3702 9.48283C47.1794 9.0786 46.9153 8.77917 46.5778 8.58454C46.2402 8.37494 45.844 8.27015 45.3891 8.27015C44.8314 8.27015 44.3471 8.3974 43.9362 8.65192C43.54 8.89146 43.2318 9.22831 43.0117 9.66248C42.8062 10.0967 42.7035 10.5907 42.7035 11.1447V17.2081Z"></path><path d="M60.3109 6.11427H62.7324V17.2081H60.2449L60.0688 15.4789C59.7313 16.0478 59.2396 16.5269 58.5939 16.9161C57.9482 17.3054 57.1851 17.5 56.3046 17.5C55.2479 17.5 54.3381 17.2455 53.575 16.7365C52.8118 16.2125 52.2322 15.5013 51.8359 14.603C51.4397 13.7048 51.2416 12.6792 51.2416 11.5264C51.2416 10.3587 51.4544 9.34809 51.88 8.49472C52.3055 7.64135 52.8999 6.97512 53.663 6.49604C54.4408 6.01695 55.336 5.77741 56.3486 5.77741C57.1557 5.77741 57.9042 5.95707 58.5939 6.31638C59.2983 6.66072 59.8193 7.16226 60.1568 7.821L60.3109 6.11427ZM60.0248 11.6612C60.0248 10.9875 59.9 10.3961 59.6505 9.88705C59.4011 9.37803 59.0415 8.98129 58.5719 8.69683C58.117 8.41237 57.5813 8.27015 56.965 8.27015C56.3486 8.27015 55.8056 8.41986 55.336 8.71929C54.8811 9.00374 54.5289 9.40048 54.2794 9.90951C54.0446 10.4185 53.9272 11.0024 53.9272 11.6612C53.9272 12.3199 54.0446 12.9038 54.2794 13.4128C54.5289 13.9218 54.8811 14.3261 55.336 14.6255C55.7909 14.91 56.3266 15.0522 56.9429 15.0522C57.574 15.0522 58.117 14.91 58.5719 14.6255C59.0268 14.341 59.379 13.9443 59.6285 13.4353C59.8927 12.9113 60.0248 12.3199 60.0248 11.6612Z"></path><path d="M70.8137 6.06935V8.607H69.8231C68.8399 8.607 68.0694 8.87649 67.5117 9.41546C66.9541 9.93945 66.6753 10.7404 66.6753 11.8184V17.2081H63.9897V6.13672H66.5212L66.7413 8.42734H66.4771C66.6239 7.69375 66.9688 7.09489 67.5117 6.63078C68.0547 6.16667 68.7591 5.93461 69.625 5.93461C69.8158 5.93461 70.0065 5.9421 70.1973 5.95707C70.3881 5.97204 70.5936 6.00947 70.8137 6.06935Z"></path><path d="M71.5425 6.11427H78.3665V8.40489H71.5425V6.11427ZM78.3665 15.0297V17.4551C77.363 17.4551 77.3466 17.4551 76.5835 17.4551C75.9084 17.4551 75.3141 17.3353 74.8004 17.0958C74.2868 16.8413 73.8906 16.437 73.6117 15.8831C73.3476 15.3292 73.2155 14.6105 73.2155 13.7272V2.65588H75.8791V13.2556C75.8791 13.9144 76.0038 14.3785 76.2533 14.648C76.5175 14.9025 76.8477 15.0297 77.2439 15.0297C77.5644 15.0297 77.5644 15.0297 78.3665 15.0297Z"></path><path d="M84.1028 17.5C83.0315 17.5 82.0776 17.253 81.2411 16.7589C80.4193 16.2499 79.7736 15.5612 79.304 14.6929C78.8344 13.8096 78.5996 12.799 78.5996 11.6612C78.5996 10.5084 78.827 9.49031 79.282 8.607C79.7369 7.72369 80.3753 7.03501 81.1971 6.54095C82.0189 6.03192 82.9581 5.77741 84.0148 5.77741C85.1154 5.77741 86.062 6.01695 86.8544 6.49604C87.6469 6.96015 88.2559 7.6114 88.6815 8.4498C89.1218 9.2882 89.3419 10.2913 89.3419 11.459V12.29L80.0084 12.3124L80.0524 10.5608H86.6783C86.6783 9.79723 86.4362 9.1834 85.9519 8.71929C85.4823 8.25517 84.8439 8.02312 84.0368 8.02312C83.4057 8.02312 82.8701 8.15786 82.4298 8.42734C82.0043 8.69683 81.6814 9.10106 81.4613 9.64003C81.2411 10.179 81.1311 10.8377 81.1311 11.6162C81.1311 12.814 81.3806 13.7197 81.8795 14.3336C82.3932 14.9474 83.1489 15.2543 84.1468 15.2543C84.8806 15.2543 85.4823 15.1121 85.9519 14.8276C86.4362 14.5432 86.7517 14.1389 86.8985 13.6149H89.3859C89.1511 14.8276 88.5641 15.7783 87.6249 16.467C86.7004 17.1557 85.5263 17.5 84.1028 17.5Z"></path><path d="M96.9945 6.06935V8.607H96.0039C95.0207 8.607 94.2502 8.87649 93.6926 9.41546C93.1349 9.93945 92.8561 10.7404 92.8561 11.8184V17.2081H90.1705V6.13672H92.702L92.9221 8.42734H92.658C92.8047 7.69375 93.1496 7.09489 93.6926 6.63078C94.2355 6.16667 94.94 5.93461 95.8058 5.93461C95.9966 5.93461 96.1874 5.9421 96.3782 5.95707C96.5689 5.97204 96.7744 6.00947 96.9945 6.06935Z"></path></svg>
```

### 4.3 Waitlist submit "send" arrow — `size-16 translate-x-1` (16×16, shifted +1px right), white on black 44×44 circle
```svg
<svg aria-hidden="true" viewBox="0 0 16 16" class="size-16 translate-x-1" fill="currentColor"><path d="M1.5 2 15 8 1.5 14l3-6-3-6Z"></path></svg>
```

### 4.4 Slideshow chevrons (phone-only prev/next buttons) — 16×16 stroke icon; "prev" adds `rotate-180`
```svg
<svg aria-hidden="true" viewBox="0 0 16 16" class="size-16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 3 5 5-5 5"></path></svg>
```

### 4.5 Waitlist pending spinner (not an SVG) — `<span class="size-16 animate-spin rounded-pill border-2 border-current border-t-transparent">` (16×16, 2px border, top transparent, spin 1s linear infinite)

### 4.6 FAQ plus/minus icon (not an SVG) — 18×18 box; two 2px-thick bars `rounded-pill bg-current` (12×2 horizontal, 2×12 vertical), colour rgba(255,255,255,0.6); the vertical bar rotates 0→90deg when open.

### 4.7 Mobile burger (not an SVG) — two spans 20×2, radius 999px, bg #8f8f8f, translateY(−5px)/(+5px); open: y 0, rotate ±45deg.
