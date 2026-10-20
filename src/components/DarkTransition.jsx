import { motion, useTransform } from 'framer-motion'
import Reveal from './motion/Reveal.jsx'
import { useTargetProgress } from './motion/hooks.js'

/** §2.5 Dark transition (no id). */
export default function DarkTransition() {
  // Dark overlay (§3.5): #overview-dark-trigger, line middle → opacity 0→1.
  const p = useTargetProgress('overview-dark-trigger', 'middle')
  const opacity = useTransform(p, [0, 1], [0, 1])

  return (
    <section data-tone="light" className="relative z-3 h-460 w-full bg-surface tablet:h-640">
      <motion.div
        id="overview-screen-trigger"
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 bottom-0 z-3 h-screen bg-black"
        style={{ opacity }}
      />
      <div id="overview-dark-trigger" aria-hidden="true" className="pointer-events-none absolute inset-x-0 bottom-0 h-[20vh]" />
      <div className="page-grid h-full grid-rows-1 items-center overflow-clip">
        <div className="sticky top-124 span-text overflow-clip pb-8">
          <Reveal as="p" amount={0} delay={0.1} className="type-display text-primary text-center">
            A global account. That truly goes beyond borders.
          </Reveal>
        </div>
      </div>
    </section>
  )
}
