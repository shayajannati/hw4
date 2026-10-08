import { useEffect, useRef } from 'react'

const PAW = `<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><g fill="#286dc0">
<ellipse cx="12" cy="15.5" rx="5" ry="4.2"/><ellipse cx="5.6" cy="9.6" rx="2.1" ry="2.7"/><ellipse cx="9.6" cy="6" rx="2.1" ry="2.8"/>
<ellipse cx="14.4" cy="6" rx="2.1" ry="2.8"/><ellipse cx="18.4" cy="9.6" rx="2.1" ry="2.7"/></g></svg>`
const SPACING = 42 // px of mouse travel between prints
const LIFETIME = 750 // ms before a print is removed
const MAX_PRINTS = 10

/**
 * Subtle bulldog paw-print trail that follows the mouse and fades quickly.
 * - pointer-events: none, so it can never block a click;
 * - turned off for prefers-reduced-motion and for touch-only devices;
 * - at most 10 prints exist at once.
 */
export function PawTrail() {
  const layer = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)')
    const finePointer = window.matchMedia?.('(pointer: fine)')
    let last: { x: number; y: number } | null = null
    let flip = false

    const onMove = (e: MouseEvent) => {
      const el = layer.current
      if (!el || reduce?.matches || finePointer?.matches === false) return
      if (last && Math.hypot(e.clientX - last.x, e.clientY - last.y) < SPACING) return
      const angle = last ? (Math.atan2(e.clientY - last.y, e.clientX - last.x) * 180) / Math.PI + 90 : 0
      last = { x: e.clientX, y: e.clientY }
      flip = !flip
      const paw = document.createElement('span')
      paw.className = 'paw-print'
      paw.innerHTML = PAW
      paw.style.left = `${e.clientX + (flip ? 6 : -6)}px`
      paw.style.top = `${e.clientY + 10}px`
      paw.style.setProperty('--rot', `${angle}deg`)
      el.appendChild(paw)
      while (el.childElementCount > MAX_PRINTS) el.firstElementChild?.remove()
      window.setTimeout(() => paw.remove(), LIFETIME)
    }
    window.addEventListener('mousemove', onMove, { passive: true })
    return () => window.removeEventListener('mousemove', onMove)
  }, [])

  return <div ref={layer} className="paw-trail" aria-hidden="true" style={{ pointerEvents: 'none' }} />
}
