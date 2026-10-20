import { useEffect, useRef, useState } from 'react'
import { motion, useMotionValueEvent, useScroll } from 'framer-motion'
import Reveal from './motion/Reveal.jsx'
import { usePrefersReducedMotion } from './motion/hooks.js'

// §2.9 list copy
const ROWS = [
  {
    dt: '100% Non-custodial',
    dd: 'Charter pairs advanced biometrics, resilient recovery, and cryptographic safeguards in a fully non-custodial wallet. Meaning your funds are controlled by you alone.',
    className: 'border-b border-subtle pt-48 pb-24',
  },
  {
    dt: 'Passkeys & Biometrics',
    dd: 'Sign in and approve with Face ID or Touch ID. Charter uses passkey signing backed by your device’s secure enclave, so your keys stay protected. No passwords to steal, and no extra steps to remember.',
    className: 'border-b border-subtle pt-48 pb-24',
  },
  {
    dt: 'Account recovery',
    dd: 'Lose a device or get locked out. You can restore access with secure recovery options, so your wallet isn’t tied to a single phone forever. Your keys stay yours, always.',
    className: 'pt-32 pb-48',
  },
]

// security token (§3.1): { switchAt:0, spring:{duration:1, bounce:0} }
const SWITCH_AT = 0

const FILL = 'absolute inset-0 h-full w-full object-cover'

/** §2.9 Security. Wrapped in <Handoff tone="inverse"> by App.jsx. */
export default function Security() {
  const ref = useRef(null)
  const reduced = usePrefersReducedMotion()
  const [on, setOn] = useState(false)
  const { scrollY } = useScroll()

  // §3.6: on when section top <= 0, reversible.
  const check = () => {
    const el = ref.current
    if (el) setOn(el.getBoundingClientRect().top <= SWITCH_AT)
  }
  useMotionValueEvent(scrollY, 'change', check)
  useEffect(check, [])

  const layer = {
    initial: { opacity: 0 },
    animate: { opacity: on ? 1 : 0 },
    transition: reduced ? { duration: 0 } : { type: 'spring', duration: 1, bounce: 0 },
  }

  return (
    <section ref={ref} id="security-section" data-tone="inverse" className="relative z-2 w-full bg-surface py-128">
      <div className="page-grid gap-y-48">
        <div className="span-main flex flex-col gap-12 overflow-clip pb-8 text-center">
          <Reveal as="p" amount={0} className="type-body1 text-secondary">
            Security that is always on.
          </Reveal>
          <Reveal as="h2" amount={0} delay={0.2} className="type-h2 text-primary">
            Highest grade security
          </Reveal>
        </div>

        <div className="col-span-full grid grid-cols-subgrid gap-y-12">
          <div className="relative col-span-full flex h-600 items-center justify-center overflow-clip rounded-xl p-48 desktop:col-span-10 desktop:col-start-2">
            <img
              src="/images/security-portrait.webp"
              alt="A woman in sunglasses outside a building"
              width={1128}
              height={788}
              loading="lazy"
              decoding="async"
              className={FILL}
            />
            <motion.div data-layer="security-ascii" aria-hidden="true" className="absolute inset-0" {...layer}>
              <img
                src="/images/portrait-ascii.2560.webp"
                alt=""
                width={1128}
                height={788}
                loading="lazy"
                decoding="async"
                className={FILL}
              />
            </motion.div>
            <motion.div data-layer="security-statement" className="relative mix-blend-overlay" {...layer}>
              <h3 className="type-h3 text-center text-primary">
                Your wallet.
                <br />
                Your money.
              </h3>
            </motion.div>
            <motion.div className="absolute z-1 mix-blend-overlay" {...layer}>
              <p aria-hidden="true" className="type-h3 text-center text-primary">
                Your wallet.
                <br />
                Your money.
              </p>
            </motion.div>
            <div
              aria-hidden="true"
              className="pointer-events-none absolute inset-0 z-2 rounded-xl border-3 border-alpha-white-12"
            />
          </div>

          <dl className="relative z-2 col-span-full grid grid-cols-subgrid desktop:col-span-8 desktop:col-start-3">
            {ROWS.map((r) => (
              <div key={r.dt} className={`col-span-full grid grid-cols-subgrid gap-y-4 ${r.className}`}>
                <dt className="type-body1 col-span-full text-primary tablet:col-span-3">{r.dt}</dt>
                <dd className="type-body1 col-span-full text-secondary tablet:col-span-5">{r.dd}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  )
}
