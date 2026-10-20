/**
 * Mirror — content plus a flipped, masked reflection standing on a soft
 * elliptical "floor" (§2.0).
 *
 * Props
 *  children            the real content (upper)
 *  reflection          node rendered inside the flipped reflection box
 *                      (usually the same layout with the *-reflection image)
 *  overlay             node placed after the reflection inside the lower box
 *                      (position it absolutely yourself, e.g. "absolute inset-x-0 bottom-0 z-5 …")
 *  height              "sm"|"md"|"lg"|"xl" (120/200/260/300) or any CSS length / px number
 *  mask                "soft"|"deep"|"short"|"stage"|"fade"|"wide"|"title"
 *  floor               "light"|"dark"|"none" (default "light")
 *  floorRise           overrides --mirror-floor-rise (default 56px), number = px
 *  blur                true → filter: blur(5px) on the reflection
 *  reserve             optional height for the lower wrapper (CSS length / px)
 *  className           extra classes on the root (root is relative w-full overflow-x-clip)
 *  upperClassName      classes for the upper wrapper (relative z-2 is always applied)
 *  upperStyle          style for the upper wrapper (e.g. motion styles not needed — pass plain)
 *  reflectionClassName extra classes for the flipped box
 *  reflectionStyle     extra style for the flipped box
 */
const len = (v) => (typeof v === 'number' ? `${v}px` : v)

export default function Mirror({
  children,
  reflection,
  overlay,
  height = 'sm',
  mask = 'soft',
  floor = 'light',
  floorRise,
  blur = false,
  reserve,
  className = '',
  upperClassName = '',
  upperStyle,
  reflectionClassName = '',
  reflectionStyle,
}) {
  const h = ['sm', 'md', 'lg', 'xl'].includes(height) ? `var(--mirror-height-${height})` : len(height)
  const rootStyle = floorRise != null ? { '--mirror-floor-rise': len(floorRise) } : undefined

  return (
    <div className={`relative w-full overflow-x-clip ${className}`} style={rootStyle}>
      <div className={`relative z-2 ${upperClassName}`} style={upperStyle}>
        {children}
      </div>
      <div className="relative" style={reserve != null ? { height: len(reserve) } : undefined}>
        {floor !== 'none' && (
          <div
            aria-hidden="true"
            className="pointer-events-none absolute left-1/2 z-1 -translate-x-1/2"
            style={{
              top: 'calc(var(--mirror-floor-rise) * -1)',
              width: 'var(--mirror-floor-width)',
              aspectRatio: 'var(--mirror-floor-aspect)',
              borderRadius: '50%',
              backgroundImage: `var(--mirror-floor-${floor})`,
              boxShadow: `var(--mirror-floor-${floor}-edge)`,
            }}
          />
        )}
        <div
          aria-hidden="true"
          inert=""
          className={`flex -scale-y-100 flex-col justify-end overflow-clip ${reflectionClassName}`}
          style={{
            height: h,
            WebkitMaskImage: `var(--mirror-mask-${mask})`,
            maskImage: `var(--mirror-mask-${mask})`,
            ...(blur ? { filter: 'blur(var(--blur-reveal))' } : null),
            ...reflectionStyle,
          }}
        >
          {reflection}
        </div>
        {overlay}
      </div>
    </div>
  )
}
