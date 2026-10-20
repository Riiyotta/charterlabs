import { useEffect, useLayoutEffect, useState } from 'react'
import { useMotionValue, useScroll, useTransform } from 'framer-motion'

export const PHONE_QUERY = '(max-width: 809.98px)'
export const TABLET_UP_QUERY = '(min-width: 810px)'
export const REDUCED_MOTION_QUERY = '(prefers-reduced-motion: reduce)'

const match = (q) => typeof window !== 'undefined' && window.matchMedia(q).matches

/** Live boolean for a media query. */
export function useMediaQuery(query) {
  const [matches, setMatches] = useState(() => match(query))
  useEffect(() => {
    const mql = window.matchMedia(query)
    const on = () => setMatches(mql.matches)
    on()
    mql.addEventListener('change', on)
    return () => mql.removeEventListener('change', on)
  }, [query])
  return matches
}

/** `(max-width: 809.98px)` — the source's `useIsPhone`. */
export const useIsPhone = () => useMediaQuery(PHONE_QUERY)
export const usePrefersReducedMotion = () => useMediaQuery(REDUCED_MOTION_QUERY)

/** Untransformed page top of an element (offsetTop sum; ignores transforms). */
export function pageOffsetTop(el) {
  let top = 0
  while (el) {
    top += el.offsetTop
    el = el.offsetParent
  }
  return top
}

/**
 * The source's `useTargetProgress(id, line)` (§3.5).
 *   p = clamp((scrollY + lineOffset − elTop) / elHeight, 0, 1)
 * lineOffset: "start" → 0, "middle" → vh/2, "end" → vh.
 * `target` is an element id string (looked up on mount) or a React ref.
 * Returns a framer-motion MotionValue<number> in [0, 1]; feed it to useTransform.
 */
export function useTargetProgress(target, line = 'start') {
  const { scrollY } = useScroll()
  // geometry lives in a MotionValue so a re-measure re-runs the transform
  // even when scrollY hasn't changed
  const geo = useMotionValue({ top: 0, height: 1, vh: 0 })

  useLayoutEffect(() => {
    const el = typeof target === 'string' ? document.getElementById(target) : target?.current
    if (!el) return
    const measure = () => {
      geo.set({
        top: pageOffsetTop(el),
        height: el.offsetHeight || 1,
        vh: window.innerHeight,
      })
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
  }, [target, geo])

  return useTransform([scrollY, geo], ([y, { top, height, vh }]) => {
    const offset = line === 'middle' ? vh / 2 : line === 'end' ? vh : 0
    return Math.min(1, Math.max(0, (y + offset - top) / height))
  })
}

/**
 * Hero entrance timing (§3.4): delays count from navigation start.
 *   entranceDelay(d) = d − min(elapsedSinceNavStart, 1s)   while < 3s have elapsed
 * After 3s (in-site navigation) the full delay applies. Seconds in, seconds out.
 * Call once at mount (e.g. `useState(() => entranceDelay(1))`).
 */
export function entranceDelay(d) {
  const elapsed = performance.now() / 1000
  if (elapsed >= 3) return d
  return Math.max(0, d - Math.min(elapsed, 1))
}
