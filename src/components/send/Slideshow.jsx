import { useCallback, useEffect, useRef, useState } from 'react'
import useEmblaCarousel from 'embla-carousel-react'
import Autoplay from 'embla-carousel-autoplay'
import { ChevronIcon } from '../icons.jsx'
import { usePrefersReducedMotion } from '../motion/hooks.js'

// §2.4 slides (exact copy). Alts from the saved source DOM.
const SLIDES = [
  {
    layout: 'top',
    src: '/images/recipient.2560.webp',
    w: 1982,
    h: 4096,
    alt: 'Charter app recipient list',
    title: 'Pick a recipient. Send in seconds.',
    body: 'Choose a saved contact or add a bank recipient in a few taps. Charter routes payouts to supported banks across the US, EU, MXN, and BRL.',
  },
  {
    layout: 'center',
    src: '/images/virtual-account.2560.webp',
    w: 991,
    h: 2048,
    alt: 'Charter app virtual US bank account details',
    title: 'Your own USD & EUR accounts.',
    body: 'Get paid like a local with virtual USD/EUR details. Receive from clients or employers abroad, then move funds when you’re ready.',
  },
  {
    layout: 'tilt-right',
    src: '/images/currency.2560.webp',
    w: 796,
    h: 2048,
    alt: 'Charter app currency selection',
    title: 'One balance, any currency.',
    body: 'Select a currency to preview what they’ll receive. Send USDC globally, with clear, real-time conversions before you confirm.',
  },
  {
    layout: 'tilt-left',
    src: '/images/amount.2560.webp',
    w: 796,
    h: 2048,
    alt: 'Charter app amount entry',
    title: 'Confirm the total. Move instantly.',
    body: 'Set the amount and see settlement speed upfront, your USDC moves in seconds. Cashing out? ACH and PIX land fast, with clear totals before you send.',
  },
  {
    layout: 'center',
    src: '/images/receipt.2560.webp',
    w: 991,
    h: 2048,
    alt: 'Charter app transaction receipt',
    title: 'A receipt you can trust.',
    body: 'Track every step with timestamps, fees, and status. Supported bank payouts today in the US, EU, Mexico, and Brazil.',
  },
]

const BTN =
  'flex items-center justify-center outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2'

/** §2.4 carousel + §3.8 behaviour (Embla + Autoplay, dimming, dots/arrows). */
export default function Slideshow() {
  const reduced = usePrefersReducedMotion()
  // slideshow token: autoplay 8s, duration 35 (§3.1, §3.8)
  const [autoplay] = useState(() =>
    Autoplay({ delay: 8000, playOnInit: false, stopOnInteraction: false, stopOnMouseEnter: true }),
  )
  const [viewportRef, api] = useEmblaCarousel({ loop: true, align: 'start', duration: 35 }, [autoplay])
  const regionRef = useRef(null)
  const articles = useRef([])
  const [selected, setSelected] = useState(0)

  // Slide dimming (§3.8): opacity = dim + (1 − dim) · visibleFraction, every scroll frame.
  const dimSlides = useCallback(() => {
    if (!api) return
    const vp = api.rootNode()
    const cs = getComputedStyle(vp)
    const dim = parseFloat(cs.getPropertyValue('--slide-dim')) || 1
    const r = vp.getBoundingClientRect()
    const left = r.left + parseFloat(cs.paddingLeft) - 1
    const right = r.right - parseFloat(cs.paddingRight) + 1
    articles.current.forEach((a) => {
      if (!a) return
      const b = a.getBoundingClientRect()
      const vis = b.width ? Math.max(0, Math.min(b.right, right) - Math.max(b.left, left)) / b.width : 0
      a.style.opacity = String(dim + (1 - dim) * Math.min(1, vis))
    })
  }, [api])

  useEffect(() => {
    if (!api) return
    const onSelect = () => setSelected(api.selectedScrollSnap())
    onSelect()
    dimSlides()
    api.on('select', onSelect).on('reInit', onSelect).on('scroll', dimSlides).on('reInit', dimSlides).on('resize', dimSlides)
    window.addEventListener('resize', dimSlides)
    return () => {
      api.off('select', onSelect).off('reInit', onSelect).off('scroll', dimSlides).off('reInit', dimSlides).off('resize', dimSlides)
      window.removeEventListener('resize', dimSlides)
    }
  }, [api, dimSlides])

  // Autoplay only while ≥25% visible; disabled under reduced motion (§3.8).
  useEffect(() => {
    if (!api || !regionRef.current) return
    const ap = api.plugins().autoplay
    if (!ap) return
    if (reduced) {
      ap.stop()
      return
    }
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting && e.intersectionRatio >= 0.25) ap.play()
        else ap.stop()
      },
      { threshold: 0.25 },
    )
    io.observe(regionRef.current)
    return () => {
      io.disconnect()
      ap.stop()
    }
  }, [api, reduced])

  return (
    <div
      ref={regionRef}
      role="region"
      aria-roledescription="carousel"
      aria-labelledby="send-heading"
      className="relative mx-auto h-700 w-full max-w-page"
    >
      <div
        ref={viewportRef}
        data-grid-exempt=""
        className="cursor-grab px-[var(--gutter-x)] [--slide-dim:1] active:cursor-grabbing tablet:[--slide-dim:0.1] desktop:px-page-col"
      >
        <div className="-ml-16 flex touch-pan-y">
          {SLIDES.map((s, i) => {
            const tilt = s.layout === 'tilt-right' || s.layout === 'tilt-left'
            return (
              <div
                key={i}
                role="group"
                aria-roledescription="slide"
                aria-label={`${i + 1} of ${SLIDES.length}`}
                className="min-w-0 shrink-0 grow-0 basis-full pl-16 desktop:basis-1/2"
              >
                <article ref={(el) => (articles.current[i] = el)} className="flex flex-col">
                  <div
                    className={`flex h-500 justify-center overflow-clip rounded-xl bg-gray-50 ${
                      s.layout === 'top' ? 'items-start' : 'items-center'
                    } ${tilt ? '' : 'p-32'}`}
                  >
                    <img
                      src={s.src}
                      alt={s.alt}
                      width={s.w}
                      height={s.h}
                      draggable="false"
                      loading="lazy"
                      decoding="async"
                      className={`h-auto w-full max-w-400 shrink-0 ${
                        s.layout === 'tilt-right' ? 'rotate-[22.5deg]' : s.layout === 'tilt-left' ? '-rotate-[22.5deg]' : ''
                      }`}
                    />
                  </div>
                  <div className="flex flex-col gap-4 px-20 py-24">
                    <h3 className="type-body1-strong text-primary">{s.title}</h3>
                    <p className="max-w-500 type-body1 text-secondary">{s.body}</p>
                  </div>
                </article>
              </div>
            )
          })}
        </div>
      </div>

      {/* Dots (tablet+) */}
      <div className="absolute bottom-0 left-1/2 hidden -translate-x-1/2 items-center rounded-pill bg-alpha-black-20 px-4 tablet:flex">
        {SLIDES.map((_, i) => (
          <button
            key={i}
            type="button"
            aria-label={`Go to slide ${i + 1}`}
            aria-current={selected === i ? 'true' : undefined}
            onClick={() => api?.scrollTo(i)}
            className={`${BTN} h-32 w-24 rounded-pill`}
          >
            <span
              className={`size-10 rounded-pill bg-white transition-opacity duration-300 ease-[cubic-bezier(.4,0,.2,1)] ${
                selected === i ? 'opacity-100' : 'opacity-50'
              }`}
            />
          </button>
        ))}
      </div>

      {/* Arrows (phone) */}
      <div className="absolute bottom-0 right-12 flex gap-8 tablet:hidden">
        <button
          type="button"
          aria-label="Previous slide"
          onClick={() => api?.scrollPrev()}
          className={`${BTN} size-40 rounded-pill bg-alpha-black-20 text-white`}
        >
          <ChevronIcon className="size-16 rotate-180" />
        </button>
        <button
          type="button"
          aria-label="Next slide"
          onClick={() => api?.scrollNext()}
          className={`${BTN} size-40 rounded-pill bg-alpha-black-20 text-white`}
        >
          <ChevronIcon className="size-16" />
        </button>
      </div>
    </div>
  )
}
