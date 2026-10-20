import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import { AnimatePresence, animate, cancelFrame, frame, motion, useMotionTemplate, useMotionValue } from 'framer-motion'
import { LogoMark } from './icons.jsx'
import Mirror from './motion/Mirror.jsx'
import { TABLET_UP_QUERY } from './motion/hooks.js'

// nav tokens (§3.1)
const GLIDE = { type: 'spring', stiffness: 400, damping: 36, mass: 1 }
const PANEL = { duration: 0.45, ease: [0.32, 0.72, 0, 1] }
const OVERLAY = { duration: 0.3 }
const OPEN_DELAY = 60
const CLOSE_DELAY = 140

const ITEM = 'flex h-36 items-center px-20 type-body3 whitespace-nowrap'
const FOCUS = 'outline-none focus-visible:ring-2 focus-visible:ring-primary'

// §1.1 menu content
const MENUS = [
  {
    id: 'home',
    label: 'Home',
    links: [
      { label: 'Wallet', href: '/#intro-section' },
      { label: 'Payments', href: '/#send-section' },
      { label: 'Finances', href: '/#overview-section' },
      { label: 'Security', href: '/#security-section' },
    ],
    images: [
      { src: '/images/nav/home-live-activity.webp', alt: 'Charter Live Activity widget on a phone lock screen.' },
      { src: '/images/nav/home-payroll.webp', alt: '' },
    ],
  },
  {
    id: 'overview',
    label: 'Overview',
    links: [
      { label: 'Earn', href: '/#earn-section' },
      { label: 'Payroll', href: '/#payroll-section' },
      { label: 'Expenses', href: '/#overview-section' },
    ],
    images: [
      { src: '/images/nav/overview-earn.webp', alt: '' },
      { src: '/images/nav/overview-expenses.webp', alt: '' },
    ],
  },
  {
    id: 'company',
    label: 'Company',
    links: [
      { label: 'X (Twitter)', href: 'https://x.com/CharterLabs', external: true },
      { label: 'LinkedIn', href: 'https://www.linkedin.com/company/charter-labs', external: true },
      { label: 'FAQ', href: '/#faq-section' },
    ],
    ring: true,
  },
]

// Link stagger (§1.1): container stagger .04 / delay .05; li {opacity 0, y 16} → rest .4s; hide .12s
const listVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.04, delayChildren: 0.05 } },
}
const itemVariants = {
  hidden: { opacity: 0, y: 16, transition: { duration: 0.12 } },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.32, 0.72, 0, 1] } },
}
// Columns cross-fade: active in .25s, inactive out .12s
const fade = (active) => ({
  initial: false,
  animate: { opacity: active ? 1 : 0 },
  transition: { duration: active ? 0.25 : 0.12 },
  style: { pointerEvents: active ? 'auto' : 'none' },
  'aria-hidden': active ? undefined : true,
  inert: active ? undefined : '',
})

/**
 * Gliding highlight: returns a clip-path MotionValue that insets an overlay
 * row down to the target item, springing L/R with {400, 36, 1}. With `snap`
 * (used by both glides, as measured on the source) the spring renders a
 * single frame and then snaps to the target on the next frame.
 */
function useGlide(rowRef, itemRefs, target, { snap: snapTo = false } = {}) {
  const l = useMotionValue(0)
  const r = useMotionValue(0)
  const opacity = useMotionValue(target ? 1 : 0)
  const placed = useRef(false)
  const snap = useRef(null) // cancels a pending snap
  // Create the template before the placement effects so it is subscribed first.
  const clipPath = useMotionTemplate`inset(0px ${r}px 0px ${l}px round var(--radius-pill))`

  const apply = useCallback(
    (force) => {
      const row = rowRef.current
      const el = target && itemRefs.current[target]
      if (!row || !el) placed.current = false
      if (!row) return
      // First placement after (re)appearing jumps; later target changes spring.
      const instant = force || !placed.current
      if (el) {
        placed.current = true
        const L = el.offsetLeft
        const R = row.offsetWidth - (el.offsetLeft + el.offsetWidth)
        snap.current?.()
        if (instant) {
          l.stop()
          r.stop()
          l.set(L)
          r.set(R)
        } else if (!snapTo) {
          animate(l, L, GLIDE)
          animate(r, R, GLIDE)
        } else {
          // Source behaviour: the spring renders a single
          // frame, then the highlight snaps to the target on the next frame.
          animate(l, L, GLIDE)
          animate(r, R, GLIDE)
          const jump = () => {
            l.stop()
            r.stop()
            l.set(L)
            r.set(R)
          }
          const unsub = l.on('change', () => {
            unsub()
            frame.update(jump)
          })
          snap.current = () => {
            unsub()
            cancelFrame(jump)
            snap.current = null
          }
        }
      }
      animate(opacity, el ? 1 : 0, { duration: instant ? 0 : 0.2 })
    },
    [rowRef, itemRefs, target, snapTo, l, r, opacity],
  )

  useLayoutEffect(() => {
    apply(false)
  }, [apply])

  // Re-measure (no animation) when fonts load or the row resizes. The observer
  // is not re-created on every target change (latest `apply` via ref), so its
  // initial callback doesn't cut the in-flight glide.
  const applyRef = useRef(apply)
  applyRef.current = apply
  useEffect(() => {
    const row = rowRef.current
    if (!row) return
    let alive = true
    const ro = new ResizeObserver(() => applyRef.current(true))
    ro.observe(row)
    document.fonts?.ready.then(() => alive && applyRef.current(true))
    return () => {
      alive = false
      ro.disconnect()
    }
    // Re-attach only when the row can (dis)appear (phone tabs mount with the sheet).
  }, [rowRef, target != null])

  useEffect(() => () => snap.current?.(), [])

  return { clipPath, opacity }
}

function ImageCard({ src, alt, className = '' }) {
  return (
    <div className={`relative h-250 flex-1 overflow-clip rounded-lg bg-gray-100 ${className}`}>
      <img src={src} alt={alt} loading="lazy" decoding="async" className="absolute inset-0 size-full object-cover" />
    </div>
  )
}

/** Company "ring" card: Mirror of nav/ring 164×164 (§1.1). */
function RingCard({ className = '' }) {
  const ring = (alt) => (
    <img src="/images/nav/ring.webp" alt={alt} width={164} height={164} loading="lazy" decoding="async" className="size-164" />
  )
  return (
    <div className={`relative h-250 flex-1 overflow-clip rounded-lg ${className}`} style={{ backgroundImage: 'var(--section-gradient)' }}>
      <Mirror
        upperClassName="flex justify-center pt-32"
        height={44}
        mask="short"
        floorRise={45}
        floor="light"
        reflection={<div className="flex justify-center">{ring('')}</div>}
      >
        {ring('')}
      </Mirror>
    </div>
  )
}

function LinkList({ links, active, className, linkClassName, onNavigate }) {
  return (
    <motion.ul
      className={`dim-siblings ${className}`}
      variants={listVariants}
      initial="hidden"
      animate={active ? 'visible' : 'hidden'}
    >
      {links.map((link) => (
        <motion.li key={link.label} variants={itemVariants}>
          <a
            href={link.href}
            className={`${linkClassName} outline-none focus-visible:underline`}
            {...(link.external ? { target: '_blank', rel: 'noopener noreferrer' } : null)}
            onClick={onNavigate}
          >
            {link.label}
            {link.external && <span className="sr-only"> (opens in a new tab)</span>}
          </a>
        </motion.li>
      ))}
    </motion.ul>
  )
}

/* ------------------------------------------------------------------------ */

export default function Header() {
  const [menu, setMenu] = useState(null) // desktop mega menu id
  const [hover, setHover] = useState(null) // desktop glide hover target
  const [sheetOpen, setSheetOpen] = useState(false) // phone sheet
  const [tab, setTab] = useState('home') // phone tab
  const menuRef = useRef(null)
  menuRef.current = menu
  const timers = useRef({})

  // nav-drop: the source's 1.5s delay counts from its hydration (~0.27s after
  // navigation), so its motion begins ~1.77s after navigation start. The CSS
  // delay (index.css) is 1.77s; anchor the animation to navigation start
  // (document timeline origin) instead of to mount.
  const headerRef = useRef(null)
  useLayoutEffect(() => {
    const a = headerRef.current?.getAnimations().find((x) => x.animationName === 'nav-drop')
    if (a && performance.now() < 1770) a.startTime = 0
  }, [])

  /* ---------------- desktop menu open / close ---------------- */
  const clearTimers = () => {
    clearTimeout(timers.current.open)
    clearTimeout(timers.current.close)
  }
  const requestOpen = (id) => {
    clearTimers()
    if (menuRef.current) setMenu(id)
    else timers.current.open = setTimeout(() => setMenu(id), OPEN_DELAY)
  }
  const requestClose = () => {
    clearTimers()
    timers.current.close = setTimeout(() => setMenu(null), CLOSE_DELAY)
  }
  const closeNow = () => {
    clearTimers()
    setMenu(null)
  }
  useEffect(() => clearTimers, [])

  // Escape closes; scrolling > 48px closes.
  useEffect(() => {
    if (!menu) return
    const startY = window.scrollY
    const onKey = (e) => e.key === 'Escape' && closeNow()
    const onScroll = () => Math.abs(window.scrollY - startY) > 48 && closeNow()
    window.addEventListener('keydown', onKey)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      window.removeEventListener('keydown', onKey)
      window.removeEventListener('scroll', onScroll)
    }
  }, [menu])

  const mouse = (fn) => (e) => {
    if (e.pointerType === 'mouse') fn(e)
  }

  /* ---------------- phone sheet ---------------- */
  useEffect(() => {
    if (!sheetOpen) return
    const html = document.documentElement
    const targets = [document.querySelector('main'), document.querySelector('footer')].filter(Boolean)
    html.style.overflow = 'hidden'
    targets.forEach((t) => t.setAttribute('inert', ''))
    const onKey = (e) => e.key === 'Escape' && setSheetOpen(false)
    const mql = window.matchMedia(TABLET_UP_QUERY)
    const onMql = () => mql.matches && setSheetOpen(false)
    window.addEventListener('keydown', onKey)
    mql.addEventListener('change', onMql)
    return () => {
      html.style.overflow = ''
      targets.forEach((t) => t.removeAttribute('inert'))
      window.removeEventListener('keydown', onKey)
      mql.removeEventListener('change', onMql)
    }
  }, [sheetOpen])

  /* ---------------- glides ---------------- */
  const rowRef = useRef(null)
  const itemRefs = useRef({})
  const glide = useGlide(rowRef, itemRefs, hover ?? menu ?? 'home', { snap: true })

  const tabRowRef = useRef(null)
  const tabRefs = useRef({})
  const tabGlide = useGlide(tabRowRef, tabRefs, sheetOpen ? tab : null, { snap: true })

  const navItem = (id, label, el) => {
    const isMenu = MENUS.some((m) => m.id === id)
    const common = {
      ref: (node) => (itemRefs.current[id] = node),
      'data-glide': id,
      'data-nav-trigger': id,
      className: `${ITEM} rounded-pill text-secondary ${FOCUS}`,
      onPointerEnter: mouse(() => {
        setHover(id)
        if (isMenu) requestOpen(id)
        else requestClose()
      }),
    }
    const menuAttrs = isMenu
      ? { 'aria-haspopup': 'true', 'aria-expanded': menu === id, 'aria-controls': 'nav-panel' }
      : null
    if (el === 'a')
      return (
        <a {...common} {...menuAttrs} href={id === 'home' ? '/' : '/contact'} aria-current={id === 'home' ? 'page' : undefined}>
          {label}
        </a>
      )
    return (
      <button
        type="button"
        {...common}
        {...menuAttrs}
        onClick={() => (menu === id ? closeNow() : (clearTimers(), setMenu(id)))}
      >
        {label}
      </button>
    )
  }

  const overlayOpen = !!menu || sheetOpen

  return (
    <>
      <header
        data-tone="light"
        ref={headerRef}
        className="nav-drop absolute inset-x-0 top-0 z-10"
        onPointerEnter={mouse(() => clearTimeout(timers.current.close))}
        onPointerLeave={mouse(() => {
          setHover(null)
          requestClose()
        })}
      >
        <div className="relative z-2 bg-surface">
          {/* ---------- Desktop / tablet ---------- */}
          <nav aria-label="Main" className="hidden h-54 items-start justify-center pt-8 tablet:flex">
            <div ref={rowRef} className="relative flex items-center" onPointerLeave={mouse(() => setHover(null))}>
              {navItem('home', 'Home', 'a')}
              {navItem('overview', 'Overview', 'button')}
              <a
                aria-label="Charter home"
                href="/"
                className={`flex size-38 items-center justify-center rounded-pill text-primary ${FOCUS}`}
                onPointerEnter={mouse(() => {
                  setHover(null)
                  requestClose()
                })}
              >
                <LogoMark />
              </a>
              {navItem('company', 'Company', 'button')}
              {navItem('contact', 'Contact', 'a')}

              {/* Glide highlight: duplicate row clipped to the target item */}
              <motion.div
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 flex items-center bg-alpha-black-4 text-primary"
                style={{ clipPath: glide.clipPath, opacity: glide.opacity }}
              >
                <span className={ITEM}>Home</span>
                <span className={ITEM}>Overview</span>
                <span className="size-38" />
                <span className={ITEM}>Company</span>
                <span className={ITEM}>Contact</span>
              </motion.div>
            </div>
          </nav>

          {/* ---------- Phone bar ---------- */}
          <div className="flex h-54 items-start justify-between px-20 pt-8 tablet:hidden">
            <a aria-label="Charter home" href="/" className={`flex size-38 items-center justify-center rounded-pill text-primary ${FOCUS}`}>
              <LogoMark />
            </a>
            <button
              type="button"
              aria-label={sheetOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={sheetOpen}
              aria-controls="nav-sheet"
              className={`relative flex size-38 items-center justify-center rounded-pill ${FOCUS}`}
              onClick={() => setSheetOpen((o) => !o)}
            >
              <motion.span
                aria-hidden="true"
                className="absolute h-2 w-20 rounded-pill bg-gray-500"
                initial={false}
                animate={{ y: sheetOpen ? 0 : -5, rotate: sheetOpen ? -45 : 0 }}
                transition={GLIDE}
              />
              <motion.span
                aria-hidden="true"
                className="absolute h-2 w-20 rounded-pill bg-gray-500"
                initial={false}
                animate={{ y: sheetOpen ? 0 : 5, rotate: sheetOpen ? 45 : 0 }}
                transition={GLIDE}
              />
            </button>
          </div>
        </div>

        {/* ---------- Desktop mega menu panel ---------- */}
        <AnimatePresence initial={false}>
          {menu && (
            <motion.div
              key="nav-panel"
              id="nav-panel"
              className="absolute inset-x-0 top-full z-1 hidden overflow-clip bg-surface tablet:block"
              initial={{ height: 0 }}
              animate={{ height: 'auto' }}
              exit={{ height: 0 }}
              transition={PANEL}
            >
              <div className="page-grid pt-48 pb-64">
                {MENUS.map((m) => {
                  const active = menu === m.id
                  return [
                    <motion.div
                      key={`${m.id}-l`}
                      className="col-span-3 col-start-1 row-start-1 flex flex-col gap-24 desktop:col-span-4 desktop:col-start-2"
                      {...fade(active)}
                    >
                      <p className="type-caption text-secondary">{m.label}</p>
                      <LinkList
                        links={m.links}
                        active={active}
                        className="flex flex-col items-start gap-12"
                        linkClassName="type-h6 text-primary"
                        onNavigate={closeNow}
                      />
                    </motion.div>,
                    <motion.div
                      key={`${m.id}-r`}
                      className="col-span-5 col-start-4 row-start-1 flex gap-16 desktop:col-span-6 desktop:col-start-7"
                      {...fade(active)}
                    >
                      {m.ring ? (
                        <RingCard />
                      ) : (
                        <>
                          <ImageCard {...m.images[0]} />
                          <ImageCard {...m.images[1]} className="hidden desktop:block" />
                        </>
                      )}
                    </motion.div>,
                  ]
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ---------- Phone sheet ---------- */}
        <AnimatePresence initial={false}>
          {sheetOpen && (
            <motion.div
              key="nav-sheet"
              id="nav-sheet"
              className="absolute inset-x-0 top-full z-1 overflow-clip bg-surface tablet:hidden"
              initial={{ height: 0 }}
              animate={{ height: 'auto' }}
              exit={{ height: 0 }}
              transition={PANEL}
            >
              <div data-lenis-prevent className="flex max-h-[calc(100dvh-54px)] flex-col gap-32 overflow-y-auto px-20 pt-8 pb-24">
                <div ref={tabRowRef} role="tablist" className="relative grid grid-cols-4">
                  {MENUS.map((m) => (
                    <button
                      key={m.id}
                      ref={(node) => (tabRefs.current[m.id] = node)}
                      type="button"
                      role="tab"
                      aria-selected={tab === m.id}
                      aria-controls={`nav-tab-${m.id}`}
                      className={`flex h-36 items-center justify-center rounded-pill type-body3 whitespace-nowrap text-secondary ${FOCUS}`}
                      onClick={() => setTab(m.id)}
                    >
                      {m.label}
                    </button>
                  ))}
                  <a
                    href="/contact"
                    className={`flex h-36 items-center justify-center rounded-pill type-body3 whitespace-nowrap text-secondary ${FOCUS}`}
                  >
                    Contact
                  </a>
                  <motion.div
                    aria-hidden="true"
                    className="pointer-events-none absolute inset-0 grid grid-cols-4 bg-alpha-black-4 text-primary"
                    style={{ clipPath: tabGlide.clipPath, opacity: tabGlide.opacity }}
                  >
                    {['Home', 'Overview', 'Company', 'Contact'].map((t) => (
                      <span key={t} className="flex h-36 items-center justify-center type-body3 whitespace-nowrap">
                        {t}
                      </span>
                    ))}
                  </motion.div>
                </div>

                <div className="grid px-16">
                  {MENUS.map((m) => {
                    const active = tab === m.id
                    return (
                      <motion.div
                        key={m.id}
                        id={`nav-tab-${m.id}`}
                        role="tabpanel"
                        className="col-start-1 row-start-1 flex flex-col gap-32"
                        {...fade(active)}
                      >
                        <div className="flex min-h-250 flex-col gap-24">
                          <p className="type-caption text-secondary">{m.label}</p>
                          <LinkList
                            links={m.links}
                            active={active}
                            className="flex flex-col items-start gap-16"
                            linkClassName="type-h4 text-primary"
                            onNavigate={() => setSheetOpen(false)}
                          />
                        </div>
                        {m.ring ? <RingCard className="flex-none" /> : <ImageCard {...m.images[0]} className="flex-none" />}
                      </motion.div>
                    )
                  })}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {/* Page overlay (z-9, below the header's z-10) */}
      <AnimatePresence>
        {overlayOpen && (
          <motion.div
            key="nav-overlay"
            aria-hidden="true"
            className="fixed inset-0 z-9 bg-alpha-black-20 backdrop-blur-glass"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={OVERLAY}
            onClick={() => {
              closeNow()
              setSheetOpen(false)
            }}
          />
        )}
      </AnimatePresence>
    </>
  )
}
