import { useMemo, useState } from 'react'
import { useCatalogue } from './catalogue'
import { useSelectedProductId } from './router'
import { ProductGrid } from './components/ProductGrid'
import { ProductView } from './components/ProductView'
import { AccountMenu } from './components/AccountMenu'
import { ChatWidget } from './components/ChatWidget'
import { NoResults } from './components/NoResults'
import { HandsomeDan } from './components/HandsomeDan'
import { CampusBorders } from './components/CampusBorders'
import { PawTrail } from './components/PawTrail'

export default function App() {
  const { products, error, loading } = useCatalogue()
  const selectedId = useSelectedProductId()
  const [query, setQuery] = useState('')

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return products
    return products.filter((p) =>
      [p.name, p.garment_type, p.description, ...p.colors, ...p.search_tags].join(' ').toLowerCase().includes(q),
    )
  }, [products, query])

  const selected = selectedId ? products.find((p) => p.product_id === selectedId) : undefined
  const goHome = () => {
    window.location.hash = ''
  }

  return (
    <>
      <CampusBorders />
      <PawTrail />
      <header className="site-header">
        <a className="brand" href="#" onClick={goHome}>
          <span className="brand__mark">
            <HandsomeDan size={40} />
          </span>
          <span>
            Campus Customs
            <small>Yale apparel &amp; gear</small>
          </span>
        </a>
        <AccountMenu />
      </header>

      <main className="container">
        {loading && <p className="status">Loading products…</p>}
        {error && <p className="status status--error">{error}</p>}

        {!loading && !error && selectedId && !selected && (
          <div className="status">
            <p>We couldn't find that product.</p>
            <button type="button" className="back-link" onClick={goHome}>
              ← Back to all products
            </button>
          </div>
        )}

        {selected && <ProductView product={selected} onBack={goHome} />}

        {!loading && !error && !selectedId && (
          <>
            <section className="hero">
              <div className="hero__text">
              <p className="hero__eyebrow">Boola Boola! Go Bulldogs</p>
              <h1>Shop Campus Customs</h1>
              <p>Hoodies, crewnecks, tees and more for Yale students, families and fans.</p>
              <div className="search-row">
              <input
                className="search"
                type="search"
                placeholder="Search products (e.g. hoodie, navy, Berkeley)"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                aria-label="Search products"
              />
              {query && (
                <button type="button" className="search-clear" onClick={() => setQuery('')} aria-label="Clear search">
                  Clear
                </button>
              )}
              </div>
              <p className="count">
                {filtered.length} of {products.length} products
              </p>
              </div>
              <HandsomeDan size={170} className="hero__mascot" />
            </section>
            {filtered.length === 0 ? (
              <NoResults query={query} products={products} onSearch={setQuery} />
            ) : (
              <ProductGrid products={filtered} />
            )}
          </>
        )}
      </main>

      <footer className="site-footer">
        <span className="site-footer__crest" aria-hidden="true">Y</span> Campus Customs · Yale merchandise · Lux et Veritas
      </footer>
      <ChatWidget />
    </>
  )
}
