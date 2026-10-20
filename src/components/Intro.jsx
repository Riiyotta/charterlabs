import { useRef } from 'react'
import { motion, useInView, useTransform } from 'framer-motion'
import Mirror from './motion/Mirror.jsx'
import Reveal from './motion/Reveal.jsx'
import { useIsPhone, useTargetProgress } from './motion/hooks.js'

const PHONE_COL =
  'col-span-3 col-start-2 flex min-w-0 flex-col items-start pb-2 tablet:col-span-4 tablet:col-start-5 desktop:col-span-5 desktop:col-start-7'
const LAYER = 'w-280 tablet:w-full tablet:max-w-420'
const IMG = 'h-auto w-280 max-w-none tablet:w-full tablet:max-w-420'

// intro.phone.appear (§3.1/§3.4): phone-only one-shot
const APPEAR_FROM = { opacity: 0, x: -150, y: -300, rotate: -20, rotateX: 40, rotateY: 30 }
const APPEAR_TO = { opacity: 1, x: 0, y: 0, rotate: -40, rotateX: 0, rotateY: 0 }
const APPEAR_T = { type: 'spring', duration: 1.5, bounce: 0 }

function IntroText() {
  return (
    <>
      <div className="flex flex-col gap-12 overflow-clip">
        <Reveal as="p" amount={0} className="type-tag text-secondary">
          Introducing Charter Wallet
        </Reveal>
        <Reveal as="h2" amount={0} delay={0.2} className="type-h2 text-primary">
          The new gold standard.
        </Reveal>
      </div>
      <Reveal as="p" amount={0} delay={0.1} className="type-body1 text-secondary">
        A global account to send money fast, receive locally, and manage everything in one secure place.
      </Reveal>
    </>
  )
}

/** §2.2 Intro. */
export default function Intro() {
  const isPhone = useIsPhone()
  // Live observes the whole #intro-section at amount 0.5 (observing the
  // transformed layer never reaches 0.5 because the upper box clips it).
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, amount: 0.5 })

  // Tablet/desktop tilt (§3.5): progress through #hero-section, line start.
  const p = useTargetProgress('hero-section', 'start')
  const x = useTransform(p, [0, 1], [-150, 0])
  const y = useTransform(p, [0, 1], [-150, 0])
  const rotate = useTransform(p, [0, 1], [-60, -40])
  const rotateX = useTransform(p, [0, 1], [30, 0])
  const rotateY = useTransform(p, [0, 1], [30, 0])

  const layerProps = isPhone
    ? {
        'data-appear': '',
        initial: APPEAR_FROM,
        animate: inView ? APPEAR_TO : APPEAR_FROM,
        transition: APPEAR_T,
      }
    : { style: { x, y, rotate, rotateX, rotateY } }

  return (
    <section
      ref={sectionRef}
      id="intro-section"
      data-tone="light"
      className="relative w-full overflow-clip"
      style={{ backgroundImage: 'var(--section-gradient)' }}
    >
      <Mirror
        height="sm"
        mask="soft"
        floor="light"
        upperClassName="page-grid grid-rows-1 items-end h-420 overflow-clip tablet:h-600"
        reflection={
          <div className="page-grid grid-rows-1 items-end">
            <div className={PHONE_COL}>
              <motion.div key={isPhone ? 'p' : 'd'} data-layer="intro-phone-reflection" className={LAYER} {...layerProps}>
                <img
                  src="/images/intro-phone-reflection.2560.webp"
                  alt=""
                  width={496}
                  height={1025}
                  loading="lazy"
                  decoding="async"
                  className={IMG}
                />
              </motion.div>
            </div>
          </div>
        }
      >
        <div className="col-span-4 hidden flex-col justify-center gap-24 self-stretch overflow-clip tablet:flex desktop:col-start-2">
          <IntroText />
        </div>
        <div className={PHONE_COL}>
          <motion.div key={isPhone ? 'p' : 'd'} data-layer="intro-phone" className={LAYER} {...layerProps}>
            <img
              src="/images/intro-phone.2560.webp"
              alt="Charter App Home UI"
              width={991}
              height={2048}
              loading="lazy"
              decoding="async"
              className={IMG}
            />
          </motion.div>
        </div>
      </Mirror>

      <div className="page-frame flex flex-col gap-24 overflow-clip tablet:hidden">
        <IntroText />
      </div>
    </section>
  )
}
