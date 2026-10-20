import { createElement, useLayoutEffect, useRef } from 'react'
import { REDUCED_MOTION_QUERY } from './hooks.js'

// revealMask token (§3.1): yPercent 110 → 0, 1s, expo-out, 0.06s per line.
const DURATION = 1000
const EASE = 'cubic-bezier(.16,1,.3,1)'
const STAGGER = 0.06

/**
 * Split `el`'s current children into masked lines (same DOM as the source's
 * SplitText `mask:"lines"`). Original child nodes are detached and returned so
 * they can be put back untouched (keeps React's node references valid).
 */
function split(el) {
  const original = Array.from(el.childNodes)
  const align = getComputedStyle(el).textAlign

  // 1. Tokenise into measurable inline units (words keep their trailing space).
  const tokens = []
  const walk = (nodes) => {
    for (const n of nodes) {
      if (n.nodeType === Node.TEXT_NODE) {
        for (const w of n.textContent.match(/\S+\s*|\s+/g) || []) tokens.push({ text: w })
      } else if (n.nodeName === 'BR') {
        tokens.push({ br: true })
      } else if (n.nodeType === Node.ELEMENT_NODE) {
        tokens.push({ node: n })
      }
    }
  }
  walk(original)

  // 2. Lay them out as spans and group by offsetTop.
  original.forEach((n) => el.removeChild(n))
  const spans = tokens.map((t) => {
    if (t.br) return document.createElement('br')
    const s = document.createElement('span')
    if (t.node) s.appendChild(t.node.cloneNode(true))
    else s.textContent = t.text
    return s
  })
  spans.forEach((s) => el.appendChild(s))

  const lines = []
  let top = null
  spans.forEach((s, i) => {
    if (tokens[i].br) {
      top = null
      lines.push([])
      return
    }
    const t = s.offsetTop
    if (top === null || Math.abs(t - top) > 1) {
      if (!(lines.length && lines[lines.length - 1].length === 0)) lines.push([])
      top = t
    }
    lines[lines.length - 1].push(i)
  })
  spans.forEach((s) => el.removeChild(s))

  // 3. Build mask + line wrappers.
  const lineEls = []
  for (const idxs of lines) {
    if (!idxs.length) continue
    const mask = document.createElement('div')
    mask.className = 'reveal-line-mask'
    mask.style.cssText = `position:relative;display:block;text-align:${align};overflow:clip`
    const line = document.createElement('div')
    line.className = 'reveal-line'
    line.style.cssText = `position:relative;display:block;text-align:${align};will-change:transform;transform:translateY(110%)`
    for (const i of idxs) {
      const t = tokens[i]
      if (t.node) line.appendChild(t.node.cloneNode(true))
      else line.appendChild(document.createTextNode(t.text))
    }
    mask.appendChild(line)
    el.appendChild(mask)
    lineEls.push(line)
  }

  const revert = () => {
    while (el.firstChild) el.removeChild(el.firstChild)
    original.forEach((n) => el.appendChild(n))
  }
  return { lines: lineEls, revert }
}

/**
 * Reveal — line-by-line text mask reveal (§3.2).
 *
 * Props
 *  as        tag to render (default "div"; use "h1"/"h2"/"p"...)
 *  delay     seconds before line 1 (line i starts at delay + 0.06·i)
 *  amount    IntersectionObserver threshold (default 0.5; most sections pass 0)
 *  onMount   start on mount instead of on view (hero). Default false.
 *  ...rest   passed to the element (className, id, style…)
 *
 * Children should be plain text (inline elements / <br> are supported).
 * Lifecycle: data-reveal="pending" → "ready" (split, lines hidden) → "done"
 * (split reverted). Reduced motion: no split, shown immediately.
 */
export default function Reveal({ as = 'div', delay = 0, amount = 0.5, onMount = false, children, ...rest }) {
  const ref = useRef(null)

  useLayoutEffect(() => {
    const el = ref.current
    if (!el) return
    if (window.matchMedia(REDUCED_MOTION_QUERY).matches) {
      el.dataset.reveal = 'done'
      return
    }

    let state = split(el)
    el.dataset.reveal = 'ready'
    let started = false
    let finished = false
    let anims = []
    let io
    let raf = 0

    const resplit = () => {
      if (started || finished) return
      state.revert()
      state = split(el)
    }

    // `at`: timeline time to anchor the animations to (skips the pending
    // phase, which otherwise delays the first movement by a frame).
    const start = (at) => {
      if (started) return
      started = true
      io?.disconnect()
      anims = state.lines.map((line, i) => {
        const a = line.animate([{ transform: 'translateY(110%)' }, { transform: 'translateY(0%)' }], {
          duration: DURATION,
          delay: (delay + STAGGER * i) * 1000,
          easing: EASE,
          fill: 'both',
        })
        if (at != null) a.startTime = at
        return a
      })
      const last = anims[anims.length - 1]
      if (!last) return finish()
      last.finished.then(finish, () => {})
    }

    const finish = () => {
      if (finished) return
      finished = true
      anims.forEach((a) => a.cancel())
      state.revert()
      el.dataset.reveal = 'done'
    }

    // Re-split when fonts settle or the box resizes (autoSplit), until started.
    document.fonts?.ready.then(resplit)
    let lastWidth = el.offsetWidth
    const ro = new ResizeObserver(() => {
      if (el.offsetWidth !== lastWidth) {
        lastWidth = el.offsetWidth
        resplit()
      }
    })
    ro.observe(el)

    if (onMount) {
      start()
    } else {
      io = new IntersectionObserver(
        (entries) => {
          if (!entries.some((e) => e.isIntersecting)) return
          io.disconnect()
          // Start on the next frame, anchored to that frame's time, so the
          // first movement is painted one frame after the crossing (as on
          // the source). A pending WAAPI start would add another frame.
          raf = requestAnimationFrame(() => start(document.timeline.currentTime ?? undefined))
        },
        { threshold: amount },
      )
      io.observe(el)
    }

    return () => {
      cancelAnimationFrame(raf)
      io?.disconnect()
      ro.disconnect()
      anims.forEach((a) => a.cancel())
      if (!finished) state.revert()
    }
    // Runs once per mount; text is static.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return createElement(as, { ref, 'data-reveal': 'pending', ...rest }, children)
}
