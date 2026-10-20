import { forwardRef } from 'react'
import { motion } from 'framer-motion'

/**
 * Appear — fade/rise/un-tilt entrance (§3.3). Renders a motion element with a
 * `data-appear` marker (reduced motion forces it to rest via CSS).
 *
 * Props
 *  as        motion tag (default "div")
 *  x, y      start offsets in px (default 0, 100)
 *  rotateX   start tilt in deg (default 50; applied without perspective)
 *  duration  spring duration in s (default 1, bounce 0 = critically damped)
 *  delay     seconds (default 0)
 *  onMount   animate on mount instead of when in view (default false)
 *  amount    in-view threshold (default 0.5), fires once
 *  ...rest   className, style, children, etc.
 */
const Appear = forwardRef(function Appear(
  { as = 'div', x = 0, y = 100, rotateX = 50, duration = 1, delay = 0, onMount = false, amount = 0.5, children, ...rest },
  ref,
) {
  const Tag = motion[as]
  const to = { opacity: 1, x: 0, y: 0, rotateX: 0 }
  const trigger = onMount ? { animate: to } : { whileInView: to, viewport: { once: true, amount } }
  return (
    <Tag
      ref={ref}
      data-appear=""
      initial={{ opacity: 0, x, y, rotateX }}
      transition={{ type: 'spring', duration, bounce: 0, delay }}
      {...trigger}
      {...rest}
    >
      {children}
    </Tag>
  )
})

export default Appear
