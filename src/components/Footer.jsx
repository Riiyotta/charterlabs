import { useLayoutEffect, useRef } from 'react'
import { motion, useMotionValue, useScroll, useTransform } from 'framer-motion'
import { Wordmark } from './icons.jsx'
import { useMediaQuery, usePrefersReducedMotion, TABLET_UP_QUERY } from './motion/hooks.js'

// §2.11 footer nav
const COLUMNS = [
  {
    title: 'Home',
    links: [
      ['Wallet', '/#intro-section'],
      ['Payments', '/#send-section'],
      ['Finances', '/#overview-section'],
      ['Security', '/#security-section'],
    ],
  },
  {
    title: 'Services',
    links: [
      ['Earn', '/#earn-section'],
      ['Payroll', '/#payroll-section'],
      ['Expenses', '/#overview-section'],
    ],
  },
  {
    title: 'Contact',
    links: [
      ['Email', '/contact'],
      ['Twitter / X', 'https://x.com/CharterLabs', true],
      ['LinkedIn', 'https://www.linkedin.com/company/charter-labs', true],
    ],
  },
  {
    title: 'Company',
    links: [
      ['FAQ', '/#faq-section'],
      ['Privacy Policy', '/legal/privacy-policy'],
    ],
  },
]

const COPYRIGHT = '© 2026 Charter Labs Inc. All rights reserved.'
const LINK = 'type-body3 text-primary outline-none focus-visible:underline'

// footerReveal token (§3.1): { from:{opacity:0, y:-100, scale:.9}, startAt:1.35, endAt:.1 }
const START_AT = 1.35
const END_AT = 0.1

/**
 * §3.5 footer reveal progress:
 *   p = clamp((1.35 − (maxScroll − scrollY)/footerH) / (1.35 − 0.1), 0, 1)
 */
function useFooterProgress(ref) {
  const { scrollY } = useScroll()
  // [maxScroll, footerH]; a MotionValue so geometry changes re-run the transform
  const geo = useMotionValue([1, 1])

  useLayoutEffect(() => {
    const el = ref.current
    if (!el) return
    const measure = () => {
      geo.set([document.documentElement.scrollHeight - window.innerHeight, el.offsetHeight || 1])
    }
    measure()
    const ro = new ResizeObserver(measure)
    ro.observe(document.body)
    ro.observe(el)
    window.addEventListener('resize', measure)
    return () => {
      ro.disconnect()
      window.removeEventListener('resize', measure)
    }
  }, [ref, geo])

  return useTransform([scrollY, geo], ([y, [max, h]]) => {
    const p = (START_AT - (max - y) / h) / (START_AT - END_AT)
    return Math.min(1, Math.max(0, p))
  })
}

/** §2.11 Footer: sticky bottom-0 at ≥810, uncovered as main scrolls away. */
export default function Footer() {
  const ref = useRef(null)
  const tabletUp = useMediaQuery(TABLET_UP_QUERY)
  const reduced = usePrefersReducedMotion()
  const p = useFooterProgress(ref)
  const opacity = useTransform(p, [0, 1], [0, 1])
  const y = useTransform(p, [0, 1], [-100, 0])
  const scale = useTransform(p, [0, 1], [0.9, 1])
  // Phone / reduced motion: static (opacity 1, no transform).
  const style = tabletUp && !reduced ? { opacity, y, scale } : undefined

  return (
    <footer
      ref={ref}
      data-tone="inverse"
      className="relative z-5 w-full overflow-hidden bg-raised tablet:sticky tablet:bottom-0"
    >
      <motion.div key={style ? 'reveal' : 'static'} style={style}>
        <div className="page-grid gap-y-64 py-96 tablet:py-128 desktop:py-192">
          <div className="col-span-full flex flex-col items-start justify-between gap-64 desktop:col-span-4">
            <a aria-label="Charter home" className="text-primary outline-none focus-visible:opacity-60" href="/">
              <Wordmark className="h-20 w-auto" />
            </a>
            <p className="type-body3 hidden text-secondary desktop:block">{COPYRIGHT}</p>
          </div>
          <nav
            aria-label="Footer"
            className="dim-siblings col-span-full grid grid-cols-subgrid gap-y-48 desktop:col-span-8 desktop:col-start-5"
          >
            {COLUMNS.map((col) => (
              <div key={col.title} className="col-span-2 flex flex-col gap-8">
                <h2 className="type-body3 text-secondary">{col.title}</h2>
                <ul className="flex flex-col gap-8">
                  {col.links.map(([label, href, external]) => (
                    <li key={label}>
                      {external ? (
                        <a href={href} target="_blank" rel="noopener noreferrer" className={LINK}>
                          {label}
                          <span className="sr-only"> (opens in a new tab)</span>
                        </a>
                      ) : (
                        <a href={href} className={LINK}>
                          {label}
                        </a>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </nav>
          <p className="type-body3 col-span-full text-secondary desktop:hidden">{COPYRIGHT}</p>
        </div>
      </motion.div>
    </footer>
  )
}
