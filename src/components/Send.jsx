import { useRef } from 'react'
import { motion, useInView, useScroll, useTransform } from 'framer-motion'
import Mirror from './motion/Mirror.jsx'
import Reveal from './motion/Reveal.jsx'
import { useTargetProgress } from './motion/hooks.js'
import Slideshow from './send/Slideshow.jsx'

const PHONE = 'relative h-670 w-260 shrink-0'
const FILL = 'absolute inset-0 size-full object-cover'

// send.phones (§3.1, §3.4): phone-only one-shot appear + parallax .02
const APPEAR_T = { type: 'spring', duration: 1.5, bounce: 0 }
const PARALLAX = 0.02

function PhoneRow({ left, right, leftAlt, rightAlt, leftLayer, rightLayer, t }) {
  return (
    <>
      <motion.div data-layer={leftLayer} className={PHONE} style={t.left}>
        <img src={left} alt={leftAlt} loading="lazy" decoding="async" className={FILL} />
      </motion.div>
      <motion.div data-layer={rightLayer} className={PHONE} style={t.right}>
        <img src={right} alt={rightAlt} loading="lazy" decoding="async" className={FILL} />
      </motion.div>
    </>
  )
}

/** §2.4 Send. */
export default function Send() {
  // Tablet/desktop phones (§3.5): #send-scroll-trigger, line start.
  const p = useTargetProgress('send-scroll-trigger', 'start')
  const xl = useTransform(p, [0, 1], [-150, 0])
  const xr = useTransform(p, [0, 1], [150, 0])
  const y = useTransform(p, [0, 1], [-300, 0])
  const scale = useTransform(p, [0, 1], [1.5, 1])
  const rotateX = useTransform(p, [0, 1], [40, 0])
  const t = { left: { x: xl, y, scale, rotateX }, right: { x: xr, y, scale, rotateX } }

  // Phone phones (§3.4): appear once when the section top reaches viewport middle.
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: '0px 0px -50% 0px' })
  const { scrollY } = useScroll()
  const driftL = useTransform(scrollY, (v) => -PARALLAX * v)
  const driftR = useTransform(scrollY, (v) => PARALLAX * v)

  const phoneCol = (src, alt, x, drift) => (
    <motion.div className="col-span-2 min-w-0" style={{ y: drift }}>
      <motion.div
        data-appear=""
        className="relative aspect-[0.39] w-full max-w-260"
        initial={{ x, y: -200 }}
        animate={inView ? { x: 0, y: 0 } : { x, y: -200 }}
        transition={APPEAR_T}
      >
        <img src={src} alt={alt} loading="lazy" decoding="async" className={FILL} />
      </motion.div>
    </motion.div>
  )

  return (
    <section
      ref={sectionRef}
      id="send-section"
      data-tone="light"
      className="relative w-full overflow-clip pb-128"
      style={{ backgroundImage: 'var(--section-gradient)' }}
    >
      <div className="hidden tablet:block">
        <Mirror
          height="sm"
          mask="soft"
          floor="light"
          upperClassName="flex h-718 justify-center gap-12 overflow-clip pt-48"
          reflection={
            <div className="flex justify-center gap-12">
              <PhoneRow
                left="/images/currency-reflection.2560.webp"
                right="/images/amount-reflection.2560.webp"
                leftAlt=""
                rightAlt=""
                leftLayer="send-left-reflection"
                rightLayer="send-right-reflection"
                t={t}
              />
            </div>
          }
        >
          <PhoneRow
            left="/images/currency.2560.webp"
            right="/images/amount.2560.webp"
            leftAlt="Charter app currency selection"
            rightAlt="Charter app amount entry"
            leftLayer="send-left"
            rightLayer="send-right"
            t={t}
          />
        </Mirror>
      </div>

      <div className="page-grid py-128 tablet:hidden">
        {phoneCol('/images/currency.2560.webp', 'Charter app currency selection', -260, driftL)}
        {phoneCol('/images/amount.2560.webp', 'Charter app amount entry', 260, driftR)}
      </div>

      <div className="flex flex-col gap-48 overflow-clip">
        <div className="page-grid gap-y-16 overflow-clip">
          <Reveal as="p" amount={0} className="type-tag text-secondary col-span-full desktop:col-span-5 desktop:col-start-2">
            Global payments
          </Reveal>
          <Reveal
            as="h2"
            id="send-heading"
            amount={0}
            delay={0.2}
            className="type-h2 text-primary col-span-full tablet:col-span-6 desktop:col-span-5 desktop:col-start-2"
          >
            Sending money has never been easier.
          </Reveal>
        </div>
        <Slideshow />
      </div>
    </section>
  )
}
