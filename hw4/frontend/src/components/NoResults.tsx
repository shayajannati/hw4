import type { Product } from '../types'

/** Storefront no-results state: explains what happened and offers a way back to the full catalogue. */
export function NoResults({
  query,
  products,
  onSearch,
}: {
  query: string
  products: Product[]
  onSearch: (q: string) => void
}) {
  // Suggestions come from the real catalogue: its most common garment types.
  const counts = new Map<string, number>()
  for (const p of products) counts.set(p.garment_type.toLowerCase(), (counts.get(p.garment_type.toLowerCase()) ?? 0) + 1)
  const suggestions = [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 4).map(([g]) => g)

  return (
    <div className="no-results" role="status">
      <h2>No products match “{query.trim()}”</h2>
      <p>Try a shorter or more general word, check the spelling, or browse everything we carry.</p>
      <button type="button" className="btn btn--primary no-results__clear" onClick={() => onSearch('')}>
        Clear search &amp; show all {products.length} products
      </button>
      {suggestions.length > 0 && (
        <p className="no-results__suggest">
          Popular categories:{' '}
          {suggestions.map((s, i) => (
            <span key={s}>
              {i > 0 && ' · '}
              <button type="button" onClick={() => onSearch(s)}>
                {s}
              </button>
            </span>
          ))}
        </p>
      )}
    </div>
  )
}
