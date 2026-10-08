/**
 * Decorative Yale-campus-inspired side borders: original line-art (Gothic towers,
 * archways, ivy and shields) in public/decor/campus-border.svg. Fixed to the page edges,
 * hidden from screen readers, never clickable, and removed on narrow screens via CSS.
 */
export function CampusBorders() {
  return (
    <>
      <div className="campus-border campus-border--left" aria-hidden="true" style={{ pointerEvents: 'none' }} />
      <div className="campus-border campus-border--right" aria-hidden="true" style={{ pointerEvents: 'none' }} />
    </>
  )
}
