import { useRef, useState } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import Appear from './motion/Appear.jsx'
import Reveal from './motion/Reveal.jsx'
import Waitlist from './Waitlist.jsx'
import { entranceDelay } from './motion/hooks.js'

const IMAGE_MASK =
  'linear-gradient(185deg, #000 50%, rgba(0,0,0,.62) 70%, rgba(0,0,0,.4) 75%, rgba(0,0,0,.16) 85%, transparent 97%)'

/** §2.1 — rendered inside <Handoff tone="light"> by App. */
export default function Hero() {
  const wrapRef = useRef(null)

  // Hero entrance (§3.4): delays counted from navigation start.
  const [d] = useState(() => ({
    image: entranceDelay(0.5),
    title: entranceDelay(1),
    body: entranceDelay(1.2),
    cta: entranceDelay(1.3),
  }))

  // Text fade (§3.5): image wrapper, ["start start", "end start"], opacity 1 → 0.
  const { scrollYProgress } = useScroll({ target: wrapRef, offset: ['start start', 'end start'] })
  const textOpacity = useTransform(scrollYProgress, [0, 1], [1, 0])

  return (
    <section
      id="hero-section"
      data-tone="light"
      className="relative flex min-h-screen w-full flex-col items-center justify-center overflow-x-clip bg-surface pb-128 tablet:pt-128"
    >
      <div className="flex h-514 w-full items-end justify-center">
        <div ref={wrapRef} className="w-380 shrink-0 tablet:w-460">
          <Appear onMount x={-150} y={300} rotateX={0} duration={2} delay={d.image}>
            <div className="relative aspect-[0.77] rotate-19" style={{ WebkitMaskImage: IMAGE_MASK, maskImage: IMAGE_MASK }}>
              <img
                src="/images/hero-phone.2560.webp"
                alt="Handheld iPhone showing the Charter app"
                loading="eager"
                fetchpriority="high"
                decoding="async"
                className="absolute inset-0 size-full object-cover"
              />
            </div>
          </Appear>
        </div>
      </div>

      <motion.div
        className="relative z-1 page-grid gap-y-24 max-tablet:!opacity-100 tablet:text-center"
        style={{ opacity: textOpacity }}
      >
        <Reveal as="h1" amount={0.5} delay={d.title} className="type-h1 text-primary span-text">
          This is what money should feel like.
        </Reveal>
        <Reveal as="p" amount={0.5} delay={d.body} className="type-body1 text-secondary span-narrow tablet:[text-wrap:balance]">
          Your new global wallet for international payments, payroll, and savings.
        </Reveal>
        <Appear onMount delay={d.cta} className="span-narrow">
          <Waitlist />
        </Appear>
      </motion.div>
    </section>
  )
}
