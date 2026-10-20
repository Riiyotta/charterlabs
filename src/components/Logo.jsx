import Reveal from './motion/Reveal.jsx'

// ticker token (§3.1/§3.7): 6 copies, 50px/s → 12.82s per copy (measured).
// No hover slowdown: live has none (animation QA), despite §3.7.
const COPIES = 6
const DURATION = '12.82s'

// `ratio`: live always renders the 160w next/image variants (160×41, 160×56,
// 160×43, 160×36) whose rounded ratios give 117.06 / 85.70 / 111.63 / 133.33px
// widths at h-30 (one copy = 640px, not 641).
const LOGOS = [
  { src: '/images/circle.2560.webp', alt: 'Circle', width: 780, height: 200, ratio: '160 / 41' },
  { src: '/images/hifi.2560.webp', alt: 'HiFi', width: 576, height: 200, ratio: '160 / 56' },
  { src: '/images/turnkey.2560.webp', alt: 'Turnkey', width: 360, height: 96, ratio: '160 / 43' },
  { src: '/images/rhinestone.2560.webp', alt: 'Rhinestone', width: 888, height: 200, ratio: '160 / 36' },
]

function Ticker() {
  return (
    <div className="w-593 shrink-0 overflow-hidden mix-blend-difference [mask-image:var(--ticker-mask)] min-[594px]:w-1234 min-[1235px]:w-1875 min-[1876px]:w-2516">
      <div className="ticker-track flex w-max" style={{ '--ticker-copies': COPIES, '--ticker-duration': DURATION }}>
        {Array.from({ length: COPIES }, (_, i) => (
          <ul
            key={i}
            aria-label={i === 0 ? 'Partners' : undefined}
            aria-hidden={i === 0 ? undefined : 'true'}
            className="flex shrink-0 items-center gap-48 pr-48"
          >
            {LOGOS.map(({ ratio, ...logo }) => (
              <li key={logo.alt} className="shrink-0">
                <img {...logo} loading="lazy" decoding="async" className="h-30 w-auto" style={{ aspectRatio: ratio }} />
              </li>
            ))}
          </ul>
        ))}
      </div>
    </div>
  )
}

/** §2.3 — rendered inside <Handoff tone="light"> by App. */
export default function Logo() {
  return (
    <section id="logo-section" data-tone="light" className="relative flex w-full flex-col bg-surface pt-192 pb-192 tablet:pb-256">
      {/* Scroll trigger for Send (§3.5): 100vh at the bottom; tablet-only top:-432 / h:auto */}
      <div
        id="send-scroll-trigger"
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 bottom-0 h-screen tablet:max-desktop:-top-432 tablet:max-desktop:h-auto"
      />
      <div className="page-grid gap-y-32 overflow-clip">
        <div className="relative z-1 span-main pb-4">
          <Reveal as="h3" delay={0.1} className="type-h3 text-center text-primary">
            Your new home base for everyday money. From daily spending to global payments, all in one place.
          </Reveal>
        </div>
        <div data-grid-exempt="" className="col-span-full flex flex-col items-center gap-24 overflow-clip">
          <p className="type-body2 text-secondary">Supported by world-class financial partners</p>
          <Ticker />
        </div>
      </div>
    </section>
  )
}
