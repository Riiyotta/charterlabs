import { motion, useTransform } from 'framer-motion'
import Mirror from './motion/Mirror.jsx'
import Reveal from './motion/Reveal.jsx'
import { useTargetProgress } from './motion/hooks.js'
import '../styles/payroll.css'

const FILL = 'absolute inset-0 h-full w-full object-cover'
const PAYDAY_POS = { objectPosition: '44.4% 28.3%' }
const CELL = 'relative aspect-[1.92] min-h-440 min-w-0 flex-1 overflow-clip'

const ALT_PORTRAIT = 'A woman arranging flowers by a window'
const ALT_PAYDAY = 'A hand holding a phone with Charter payment notifications on its lock screen'
const BODY =
  'Waiting weeks for money you already earned doesn’t make sense. With Charter, your pay can arrive as you work so you can spend or save when you need to.'
const STATS = [
  ['Real time', 'Instant'],
  ['Your schedule', 'Flexible'],
  ['Spend Today', 'Available'],
]

function Img({ src, alt = '', style }) {
  return <img src={src} alt={alt} loading="lazy" decoding="async" className={FILL} style={style} />
}

function Statement({ className }) {
  return (
    <div className={`flex flex-col items-center text-primary mix-blend-overlay ${className}`}>
      <h3 className="type-h4 text-center max-w-300">
        Earn now.
        <br />
        Spend later.
      </h3>
      <p className="type-body2 text-center max-w-300">Never wait on payroll again.</p>
    </div>
  )
}

function Stats({ className = '' }) {
  return (
    <div className={`page-grid gap-y-48 ${className}`}>
      <ul className="span-text flex flex-col items-center gap-32 tablet:flex-row tablet:items-start tablet:justify-between tablet:gap-0">
        {STATS.map(([title, label]) => (
          <li key={title} className="flex flex-col-reverse items-center whitespace-nowrap tablet:w-130 tablet:flex-col">
            {/* nowrap: index.css `[class*=type-h]{text-wrap:balance}` resets text-wrap-mode on this span */}
            <span className="type-h5 text-primary whitespace-nowrap tablet:type-body1-strong">{title}</span>
            <span className="type-body1 text-secondary">{label}</span>
          </li>
        ))}
      </ul>
      <p className="type-body1 text-secondary text-center span-text">{BODY}</p>
    </div>
  )
}

/** §2.8 Payroll. */
export default function Payroll() {
  // §3.5: photo row rises y 500 → 0 over #payroll-section, line end.
  const p = useTargetProgress('payroll-section', 'end')
  const y = useTransform(p, [0, 1], [500, 0])

  return (
    <section id="payroll-section" data-tone="inverse" className="relative z-3 w-full bg-surface py-128">
      <div className="mx-auto flex w-full max-w-1920 flex-col items-center gap-32 tablet:gap-0">
        <div className="z-1 page-grid gap-y-12 overflow-clip text-center tablet:sticky tablet:top-188">
          <Reveal as="p" amount={0} className="type-tag text-secondary span-text">
            Get paid as you work.
          </Reveal>
          <Reveal as="h2" amount={0} delay={0.2} className="type-h2 text-primary span-text">
            Payroll every hour, day week or month.
          </Reveal>
        </div>

        {/* Stage, tablet+ */}
        <div className="payroll-stage relative z-2 hidden w-full tablet:block">
          <Mirror
            height="xl"
            mask="wide"
            floor="none"
            blur
            upperClassName="mb-4 overflow-clip"
            reflection={
              <motion.div data-layer="payroll-photos-reflection" className="relative flex w-full shrink-0" style={{ y }}>
                <div className={CELL}>
                  <Img src="/images/portrait-reflection.2560.webp" />
                </div>
                <div className={CELL}>
                  <Img src="/images/payday-reflection.2560.webp" style={PAYDAY_POS} />
                </div>
              </motion.div>
            }
            overlay={<Stats className="absolute inset-x-0 top-0 z-5 h-full content-center pb-32" />}
          >
            <motion.div data-layer="payroll-photos" className="relative flex w-full shrink-0" style={{ y }}>
              <div className={CELL}>
                <Img src="/images/payroll-portrait.webp" alt={ALT_PORTRAIT} />
              </div>
              <div className={CELL}>
                <Img src="/images/payday.2560.webp" alt={ALT_PAYDAY} style={PAYDAY_POS} />
              </div>
              <div aria-hidden="true" className="payroll-center-blur absolute inset-0 bg-alpha-black-20 backdrop-blur-glass" />
              <div aria-hidden="true" className="absolute inset-x-0 top-0 z-1 border-t border-alpha-white-12" />
              <Statement className="absolute inset-x-0 top-1/2 z-1 -translate-y-1/2 gap-16" />
            </motion.div>
          </Mirror>
        </div>

        {/* Phone */}
        <div className="relative z-2 flex w-full flex-col gap-32 py-12 tablet:hidden">
          <div className="page-frame flex flex-col gap-8">
            <div className="relative flex h-500 flex-col items-center justify-end overflow-clip rounded-xl p-32">
              <Img src="/images/portrait-soft.2560.webp" alt={ALT_PORTRAIT} />
              <Statement className="relative z-1 gap-12" />
              <div aria-hidden="true" className="pointer-events-none absolute inset-0 rounded-xl border-3 border-alpha-white-12" />
            </div>
            <div className="relative h-500 overflow-clip rounded-xl">
              <Img src="/images/payday.2560.webp" alt={ALT_PAYDAY} style={PAYDAY_POS} />
              <div aria-hidden="true" className="pointer-events-none absolute inset-0 rounded-xl border-3 border-alpha-white-12" />
            </div>
          </div>
          <Stats />
        </div>
      </div>
    </section>
  )
}
