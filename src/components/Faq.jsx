import { useState } from 'react'
import { motion } from 'framer-motion'
import { usePrefersReducedMotion } from './motion/hooks.js'

// §2.10 copy (exact; no question mark on item 4, as on live)
const ITEMS = [
  {
    q: 'How does Charter work?',
    a: [
      'Charter Wallet is different from other financial apps you may have used before.',
      'Your Charter Wallet is self-custodial. This means that you own and control access to the money in your wallet. Your ownership is secured using a private cryptographic key, which is generated for you during setup.',
      'Money in your Charter Wallet is digital currency. It is held in your Charter Wallet as digital dollars, a digital currency issued by Circle Internet Financial.',
      'We always display the value of your Wallet balance and all transfers in both digital dollars or digital euros, and government-issued currency of your choice, like USD, EUR, or BRL.',
    ],
  },
  {
    q: 'How long do transfers take?',
    a: [
      'Most normal, contact-to-contact (peer-to-peer) transfers take less than five seconds on the Charter Wallet app.',
      "Most deposit and withdraw (onramp/offramp) transfers take five minutes or less. In some cases, processing can take 1- 2 business days. This will depend on the recipient's bank.",
    ],
  },
  {
    q: 'How secure is my Charter Wallet?',
    a: [
      'With Charter Wallet, you own and control the money in your wallet. Access to your wallet is controlled using a private key from a secure enclave (iPhone) or a trusted execution environment (TEE) (Android).',
      'This key is securely generated and stored on your phone, and is protected by your phone’s unique cryptographic security system and your biometrics (Face ID or fingerprints).',
      'Your private key is the only way to access your wallet. No one other than you can access your key, including Charter Labs. This means that you are always in control of your wallet. Wallets that work like this are known as self-custody wallets.',
    ],
  },
  {
    q: 'Why is my balance in digital dollars',
    a: [
      'We use digital currency to enable global money transfers, regardless of the currency.',
      'It is held in your Charter Wallet as digital dollars, a digital currency issued by Circle Internet Financial.',
      'Using digital currency lets you send money globally, regardless of the currency.',
    ],
  },
  {
    q: 'Which payment methods are supported?',
    a: [
      'Learn about the different ways you can add money to your Charter Wallet.',
      'Charter’s Virtual Bank Accounts lets you receive and deposit money in US dollars, euros, Mexican pesos, or Brazilian reais, even if you don’t live in those countries. *Conditions apply',
      'When a deposit arrives to your virtual bank account, it is automatically converted to the primary currency of your Charter Wallet.',
      'Charter’s Virtual Account’s are offered in partnership with Hifi Bridge LLC.',
    ],
  },
]

// accordion token (§3.1): spring { duration:.5, bounce:0 }
const SPRING = { type: 'spring', duration: 0.5, bounce: 0 }

function Item({ i, item, open, onToggle, transition }) {
  return (
    <div className="overflow-clip rounded-md">
      <h3 className="type-h6">
        <button
          type="button"
          id={`faq-button-${i}`}
          aria-expanded={open}
          aria-controls={`faq-panel-${i}`}
          onClick={onToggle}
          className="flex w-full cursor-pointer items-center justify-between gap-16 rounded-md px-16 py-20 text-start text-alpha-white-80 outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary tablet:px-20"
        >
          {item.q}
          <span aria-hidden="true" className="relative flex size-18 shrink-0 items-center justify-center text-secondary">
            <span className="absolute h-2 w-12 rounded-pill bg-current" />
            <motion.span
              data-bar=""
              className="absolute h-12 w-2 rounded-pill bg-current"
              initial={false}
              animate={{ rotate: open ? 90 : 0 }}
              transition={transition}
            />
          </span>
        </button>
      </h3>
      <motion.div
        id={`faq-panel-${i}`}
        role="region"
        aria-labelledby={`faq-button-${i}`}
        inert={open ? undefined : ''}
        className="overflow-hidden"
        initial={false}
        animate={open ? { height: 'auto', opacity: 1 } : { height: 0, opacity: 0 }}
        transition={transition}
      >
        <div className="type-body2 flex flex-col gap-8 px-16 pb-20 text-secondary tablet:px-20">
          {item.a.map((p, k) => (
            <p key={k}>{p}</p>
          ))}
        </div>
      </motion.div>
    </div>
  )
}

/** §2.10 FAQ: single-open accordion, all closed initially. */
export default function Faq() {
  const [openIndex, setOpenIndex] = useState(-1)
  const reduced = usePrefersReducedMotion()
  const transition = reduced ? { duration: 0 } : SPRING

  return (
    <section id="faq-section" data-tone="inverse" className="relative w-full overflow-clip bg-surface py-128">
      <div className="page-grid gap-y-32">
        <div className="span-main pt-16 tablet:pt-0 desktop:col-span-2 desktop:col-start-3 desktop:pt-16">
          <h2 className="type-h2 text-primary">FAQ</h2>
        </div>
        <div className="span-main -mx-20 flex flex-col gap-4 p-4 tablet:-mx-24 desktop:col-span-6 desktop:col-start-5">
          {ITEMS.map((item, i) => (
            <Item
              key={item.q}
              i={i}
              item={item}
              open={openIndex === i}
              onToggle={() => setOpenIndex((cur) => (cur === i ? -1 : i))}
              transition={transition}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
