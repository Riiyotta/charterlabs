import { useEffect } from 'react'
import Lenis from 'lenis'
import { REDUCED_MOTION_QUERY, TABLET_UP_QUERY } from './hooks.js'

/**
 * SmoothScroll — Lenis `{ lerp: .06, autoRaf: true, anchors: true }` (§3.9).
 * Created only while `(min-width: 810px)` matches and reduced motion is off;
 * destroyed / re-created when those queries change. Phone scrolls natively.
 *
 * Lenis drives the real window scroll position, so native `scroll` events fire
 * every frame and framer-motion's useScroll / our useTargetProgress stay in
 * sync with no extra wiring. Renders nothing; mount once near the app root.
 */
export default function SmoothScroll() {
  useEffect(() => {
    const wide = window.matchMedia(TABLET_UP_QUERY)
    const reduced = window.matchMedia(REDUCED_MOTION_QUERY)
    let lenis = null

    const sync = () => {
      const want = wide.matches && !reduced.matches
      if (want && !lenis) {
        lenis = new Lenis({ lerp: 0.06, autoRaf: true, anchors: true })
        window.lenis = lenis
      } else if (!want && lenis) {
        lenis.destroy()
        lenis = null
        window.lenis = undefined
      }
    }
    sync()
    wide.addEventListener('change', sync)
    reduced.addEventListener('change', sync)
    return () => {
      wide.removeEventListener('change', sync)
      reduced.removeEventListener('change', sync)
      lenis?.destroy()
      window.lenis = undefined
    }
  }, [])
  return null
}
