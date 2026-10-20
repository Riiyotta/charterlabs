import { useLayoutEffect, useRef, useState } from 'react'
import { motion, useMotionValueEvent, useScroll, useTransform } from 'framer-motion'
import Mirror from './motion/Mirror.jsx'
import Reveal from './motion/Reveal.jsx'
import { usePrefersReducedMotion } from './motion/hooks.js'

// §3.1 earn token: switchAt 96, spring {duration 1, bounce 0}, photo closed {opacity 0, scale .8, blur 10}, parallax .02
const SWITCH_AT = 96
const PARALLAX = 0.02
const SPRING = { type: 'spring', duration: 1, bounce: 0 }

const FILL = 'absolute inset-0 h-full w-full object-cover'
const PHONE = 'relative aspect-[796/2048] w-full max-w-260 shrink-0'
const PANEL = 'relative z-1 flex h-568 w-1/4 justify-center overflow-clip'
const COPY =
  'Put your money to work with Earn from Charter. Earn up to 4.50% APY on your savings in our vaults. Deposit and withdraw whenever you like.'

const ALT_LEFT = 'Charter app screen with a vault balance and its earnings forecast'
const ALT_RIGHT = 'Charter app screen with an earnings overview'
const ALT_PHOTO = 'A hiker sitting on a rock above a lake and autumn hills'

function Img({ src, alt = '', className = FILL, style }) {
  return <img src={src} alt={alt} loading="lazy" decoding="async" className={className} style={style} />
}

/** Phone screen inside a panel; `y` is the ±0.02·scrollY drift (§3.5). */
function Phone({ src, alt, y }) {
  return (
    <motion.div className={PHONE} style={{ y }}>
      <Img src={src} alt={alt} />
    </motion.div>
  )
}

/** Desktop/tablet stage row (§2.7). `reflect` drops alts and suffixes data-layer. */
function StageRow({ closed, transition, leftY, rightY, reflect }) {
  const sfx = reflect ? '-reflection' : ''
  return (
    <div className="relative flex h-598 w-full shrink-0 items-end justify-between overflow-clip">
      <motion.div
        data-layer={`earn-left${sfx}`}
        className={`${PANEL} items-end`}
        initial={false}
        animate={{ x: closed ? '100%' : '0%' }}
        transition={transition}
      >
        <Img src="/images/backdrop.2560.webp" />
        <Phone src="/images/forecast.2560.webp" alt={reflect ? '' : ALT_LEFT} y={leftY} />
      </motion.div>
      <motion.div
        data-layer={`earn-photo${sfx}`}
        className={`absolute inset-x-0 top-0 mx-auto h-full w-1/2 overflow-clip ${closed ? 'z-0' : 'z-3'}`}
        initial={false}
        animate={
          closed
            ? { opacity: 0, scale: 0.8, filter: 'blur(10px)' }
            : { opacity: 1, scale: 1, filter: 'blur(0px)' }
        }
        transition={transition}
      >
        <Img src="/images/photo.2560.webp" alt={reflect ? '' : ALT_PHOTO} />
      </motion.div>
      <motion.div
        data-layer={`earn-right${sfx}`}
        className={`${PANEL} items-start`}
        initial={false}
        animate={{ x: closed ? '-100%' : '0%' }}
        transition={transition}
      >
        <Img src="/images/backdrop.2560.webp" />
        <Phone src="/images/earnings.2560.webp" alt={reflect ? '' : ALT_RIGHT} y={rightY} />
      </motion.div>
    </div>
  )
}

/** Phone (<810) static two-cell row (§2.7). */
function PhoneRow({ leftY, rightY, reflect }) {
  const CELL = 'relative flex min-w-0 flex-1 items-center justify-center overflow-clip px-24'
  return (
    <div className="flex h-600 w-full shrink-0 gap-2">
      <div className={`${CELL} pb-124`}>
        <Img src="/images/backdrop.2560.webp" />
        <Phone src="/images/forecast.2560.webp" alt={reflect ? '' : ALT_LEFT} y={leftY} />
      </div>
      <div className={`${CELL} pt-124`}>
        <Img src="/images/backdrop.2560.webp" />
        <Phone src="/images/earnings.2560.webp" alt={reflect ? '' : ALT_RIGHT} y={rightY} />
      </div>
    </div>
  )
}

/** §2.7 Earn. */
export default function Earn() {
  const ref = useRef(null)
  const reduced = usePrefersReducedMotion()
  const { scrollY } = useScroll()

  // §3.6: closed while section top <= -96 (reversible).
  const [closed, setClosed] = useState(false)
  const check = () => {
    const el = ref.current
    if (el) setClosed(el.getBoundingClientRect().top <= -SWITCH_AT)
  }
  useMotionValueEvent(scrollY, 'change', check)
  useLayoutEffect(check, [])

  // §3.5: inner phones drift, left +0.02·scrollY, right −0.02·scrollY (all sizes).
  const leftY = useTransform(scrollY, (v) => v * PARALLAX)
  const rightY = useTransform(scrollY, (v) => -v * PARALLAX)

  const transition = reduced ? { duration: 0 } : SPRING

  return (
    <section ref={ref} id="earn-section" data-tone="inverse" className="relative w-full overflow-clip bg-surface py-128">
      <div className="flex flex-col items-center gap-48 overflow-clip">
        <div className="page-grid gap-y-12 overflow-clip pb-4 text-center">
          <Reveal as="p" amount={0} className="type-tag text-secondary span-text">
            Don&apos;t let your money sit idle.
          </Reveal>
          <Reveal as="h2" amount={0} delay={0.2} className="type-h2 text-primary span-text">
            Earn up to 4.50% APY on savings.
          </Reveal>
        </div>

        {/* Stage, tablet+ */}
        <div className="hidden w-full max-w-1920 tablet:block">
          <Mirror
            height="md"
            mask="stage"
            floor="none"
            blur
            upperClassName="mb-4"
            reflection={<StageRow closed={closed} transition={transition} leftY={leftY} rightY={rightY} reflect />}
            overlay={
              <div className="page-grid absolute inset-x-0 bottom-64 z-2">
                <motion.p
                  className="type-body1 text-secondary text-center span-text"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: closed ? 1 : 0 }}
                  transition={transition}
                >
                  {COPY}
                </motion.p>
              </div>
            }
          >
            <StageRow closed={closed} transition={transition} leftY={leftY} rightY={rightY} />
          </Mirror>
        </div>

        {/* Phone */}
        <div className="flex w-full flex-col items-center gap-4 overflow-clip tablet:hidden">
          <Mirror
            height="sm"
            mask="fade"
            floor="none"
            blur
            upperClassName="mb-4"
            reflection={<PhoneRow leftY={leftY} rightY={rightY} reflect />}
          >
            <PhoneRow leftY={leftY} rightY={rightY} />
          </Mirror>
          <div className="page-grid">
            <p className="type-body1 text-secondary text-center span-text">{COPY}</p>
          </div>
        </div>
      </div>
    </section>
  )
}
