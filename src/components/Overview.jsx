import { useRef } from 'react'
import { motion, useInView, useTransform } from 'framer-motion'
import Mirror from './motion/Mirror.jsx'
import Reveal from './motion/Reveal.jsx'
import { useIsPhone, useTargetProgress } from './motion/hooks.js'

// overview token (§3.1): reflectionOpacity .7; phone appear {opacity:0, y:-450}, spring 1s.
const REFLECTION_OPACITY = 0.7
const APPEAR_T = { type: 'spring', duration: 1, bounce: 0 }

/** §2.6 Overview. */
export default function Overview() {
  const isPhone = useIsPhone()

  // "Meet the upgrade." (§3.5): #overview-dark-trigger, line start → opacity 1→0.
  const dark = useTargetProgress('overview-dark-trigger', 'start')
  const meetOpacity = useTransform(dark, [0, 1], [1, 0])

  // Phone drop (§3.5, tablet+): #overview-screen-trigger, line start.
  const p = useTargetProgress('overview-screen-trigger', 'start')
  const y = useTransform(p, [0, 1], [-550, 0])
  const opacity = useTransform(p, [0, 1], [0, 1])
  const reflOpacity = useTransform(p, [0, 1], [0, REFLECTION_OPACITY])

  // Phone one-shot appear (§3.4): section top reaches viewport middle.
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: '0px 0px -50% 0px' })

  const layer = (to) =>
    isPhone
      ? {
          'data-appear': '',
          initial: { opacity: 0, y: -450 },
          animate: inView ? { opacity: to, y: 0 } : { opacity: 0, y: -450 },
          transition: APPEAR_T,
        }
      : { style: { y, opacity: to === 1 ? opacity : reflOpacity } }

  return (
    <section ref={sectionRef} id="overview-section" data-tone="inverse" className="relative z-4 w-full bg-surface pb-128">
      <motion.p
        className="type-h5 text-primary absolute left-1/2 top-48 z-3 -translate-x-1/2 whitespace-nowrap"
        style={{ opacity: meetOpacity }}
      >
        Meet the upgrade.
      </motion.p>
      <div className="overflow-clip">
        <Mirror
          height="lg"
          mask="deep"
          floor="dark"
          upperClassName="overview-top-fade flex justify-center overflow-clip tablet:h-640 tablet:items-end"
          reflection={
            <div className="flex justify-center">
              <motion.div
                key={isPhone ? 'p' : 'd'}
                data-layer="overview-screen-reflection"
                className="w-full max-w-560"
                {...layer(REFLECTION_OPACITY)}
              >
                <img
                  src="/images/overview-reflection.2560.webp"
                  alt=""
                  width={901}
                  height={1214}
                  loading="lazy"
                  decoding="async"
                  // live (next/image, phone DPR1) loads the 640w variant (640×862) whose
                  // rounded ratio sets the layout height; match it so text below
                  // lands on the same sub-pixel.
                  className="h-auto w-full max-tablet:aspect-[640/862]"
                />
              </motion.div>
            </div>
          }
          overlay={
            <div className="absolute inset-x-0 bottom-0 z-5 page-grid gap-y-24 overflow-clip text-center">
              <Reveal as="h2" amount={0} className="type-h2 text-primary span-text">
                A single place to handle it all.
              </Reveal>
              <Reveal as="p" amount={0} delay={0.1} className="type-body1 text-secondary span-narrow">
                Manage your payroll, savings and expenses. All in a single and clean overview.
              </Reveal>
            </div>
          }
        >
          <motion.div key={isPhone ? 'p' : 'd'} data-layer="overview-screen" className="w-full max-w-560" {...layer(1)}>
            <img
              src="/images/overview.2560.webp"
              alt="Charter app overview of earnings and expenses"
              width={1138}
              height={1536}
              loading="lazy"
              decoding="async"
              // phone: live 640w variant is 640×864 (see reflection note)
              className="h-auto w-full max-tablet:aspect-[640/864]"
            />
          </motion.div>
        </Mirror>
      </div>
    </section>
  )
}
