import { useEffect, useRef, useState } from 'react'
import { animate, motion, useMotionValue } from 'framer-motion'
import { ArrowIcon, Spinner } from './icons.jsx'
import { useIsPhone } from './motion/hooks.js'

// waitlist + press tokens (§3.1)
const PRESS = { type: 'spring', stiffness: 80, damping: 20, mass: 1 }
const CLOSED_WIDTH = 150
const MESSAGE_WIDTH = 230
const CLOSE_AFTER = 20000
const MESSAGE_HOLD = 2500
const FOCUS_AFTER = 250
// Local clone: no real endpoint. Submissions never leave the browser; this
// fakes a short round-trip so the pending and "Thank you" states still show.
const FAKE_SUBMIT_MS = 600
const fakeSubmit = () =>
  new Promise((resolve) => setTimeout(() => resolve({ ok: true }), FAKE_SUBMIT_MS))

/**
 * Waitlist pill form (§2.1.1). Closed: black 150×50 "Join Waitlist" pill.
 * Click → `--open` springs 0→1 (80/20/1), pill widens to the container, input
 * focuses after 250ms. Phone (<810) is always open via [data-phone-open].
 */
export default function Waitlist() {
  const isPhone = useIsPhone()
  const open = useMotionValue(0)
  const [isOpen, setIsOpen] = useState(false)
  const [status, setStatus] = useState('idle') // idle | pending
  const [message, setMessage] = useState(null) // { text, error }
  const [invalid, setInvalid] = useState(false)
  const inputRef = useRef(null)
  const timers = useRef({})

  useEffect(() => () => Object.values(timers.current).forEach(clearTimeout), [])

  const openForm = () => {
    setIsOpen(true)
    animate(open, 1, PRESS)
    clearTimeout(timers.current.focus)
    timers.current.focus = setTimeout(() => inputRef.current?.focus(), FOCUS_AFTER)
  }
  const closeForm = () => {
    clearTimeout(timers.current.close)
    setIsOpen(false)
    setInvalid(false)
    animate(open, 0, PRESS)
  }
  const showMessage = (text, error) => {
    setMessage({ text, error })
    clearTimeout(timers.current.message)
    timers.current.message = setTimeout(() => setMessage(null), MESSAGE_HOLD)
  }

  const onSubmit = async (e) => {
    e.preventDefault()
    const input = inputRef.current
    if (!input.checkValidity()) {
      setInvalid(true)
      input.focus()
      return
    }
    setInvalid(false)
    setStatus('pending')
    try {
      const res = await fakeSubmit()
      if (!res.ok) throw new Error(String(res.status))
      input.value = ''
      closeForm()
      showMessage('Thank you', false)
    } catch {
      closeForm()
      showMessage('Something went wrong', true)
    } finally {
      setStatus('idle')
    }
  }

  // Phone shows the field unless a status message is on the label.
  const phoneOpen = isPhone && !message
  const fieldActive = isOpen || phoneOpen

  return (
    <motion.form
      noValidate
      data-phone-open={message ? undefined : ''}
      className="waitlist relative h-50 w-full"
      style={{ '--pill-width': `${message?.error ? MESSAGE_WIDTH : CLOSED_WIDTH}px`, '--open': open }}
      onSubmit={onSubmit}
      onKeyDown={(e) => e.key === 'Escape' && isOpen && closeForm()}
      onPointerEnter={() => clearTimeout(timers.current.close)}
      onPointerLeave={() => {
        if (!isOpen) return
        clearTimeout(timers.current.close)
        timers.current.close = setTimeout(() => {
          if (!inputRef.current?.value) closeForm()
        }, CLOSE_AFTER)
      }}
    >
      <span
        aria-hidden="true"
        className="waitlist-pill pointer-events-none absolute inset-y-0 left-1/2 -translate-x-1/2 rounded-pill max-tablet:left-0 max-tablet:translate-x-0"
      />
      <button
        type="button"
        data-waitlist-trigger=""
        aria-expanded={isOpen}
        disabled={isOpen || !!message}
        tabIndex={isOpen ? -1 : 0}
        className={`waitlist-label absolute inset-y-0 left-1/2 flex w-[var(--pill-width)] -translate-x-1/2 items-center justify-center rounded-pill type-button whitespace-nowrap outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 ${
          message ? '' : 'max-tablet:hidden'
        }`}
        style={message?.error ? { color: 'var(--color-status-error)' } : undefined}
        onClick={openForm}
      >
        {message ? message.text : 'Join Waitlist'}
      </button>
      <div className={`waitlist-field absolute inset-0 ${fieldActive ? '' : 'pointer-events-none'}`} inert={fieldActive ? undefined : ''}>
        <label>
          <span className="sr-only">Email</span>
          <input
            ref={inputRef}
            required
            type="email"
            name="email"
            placeholder="Email"
            autoComplete="email"
            aria-invalid={invalid || undefined}
            onInput={() => invalid && setInvalid(false)}
            className="size-full rounded-pill bg-transparent pr-56 pl-24 type-body2 text-primary outline-none placeholder:text-disabled focus:shadow-[inset_0_0_0_1px_var(--tone-text-primary)] aria-[invalid=true]:shadow-[inset_0_0_0_1px_var(--color-status-error)]"
          />
        </label>
        <button
          type="submit"
          aria-label="Join waitlist"
          disabled={status === 'pending'}
          className="absolute top-3 right-3 bottom-3 flex aspect-square items-center justify-center rounded-pill bg-solid text-on-solid outline-none transition-opacity duration-200 ease-standard hover:opacity-80 focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
        >
          {status === 'pending' ? <Spinner /> : <ArrowIcon />}
        </button>
      </div>
      <p role="status" aria-live="polite" className="sr-only">
        {message?.text ?? ''}
      </p>
    </motion.form>
  )
}
