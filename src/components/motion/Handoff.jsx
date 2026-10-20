import { useRef } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import { useIsPhone, usePrefersReducedMotion } from './hooks.js'

// handoff token (§3.1): { y:240, overlay:{ light:.12, inverse:.6 } }
const OVERLAY = { light: 0.12, inverse: 0.6 }

/**
 * Handoff — wraps a section so that, as its bottom travels from the viewport
 * bottom to the viewport top, it drifts down and dims under a black overlay
 * while the next section scrolls over it (§0.8, §3.5).
 *
 * Props
 *  tone        "light" (overlay → .12) | "inverse" (overlay → .6). Default "light".
 *  endOpacity  override the overlay's final opacity.
 *  distance    drift in px at progress 1 (default 240). 0 on phone / reduced motion.
 *  children    the <section>.
 *
 * Progress: useScroll target = wrapper, offset ["end end", "end start"].
 */
export default function Handoff({ tone = 'light', endOpacity, distance = 240, children }) {
  const ref = useRef(null)
  const isPhone = useIsPhone()
  const reduced = usePrefersReducedMotion()
  const { scrollYProgress } = useScroll({ target: ref, offset: ['end end', 'end start'] })
  const drift = isPhone || reduced ? 0 : distance
  const y = useTransform(scrollYProgress, [0, 1], [0, drift])
  // Reduced motion: no drift and no darkening (source overlay stays at 0).
  const opacity = useTransform(scrollYProgress, [0, 1], [0, reduced ? 0 : endOpacity ?? OVERLAY[tone]])

  return (
    <motion.div ref={ref} className="relative isolate" style={{ y }}>
      {children}
      <motion.div aria-hidden="true" className="pointer-events-none absolute inset-0 z-10 bg-black" style={{ opacity }} />
    </motion.div>
  )
}
