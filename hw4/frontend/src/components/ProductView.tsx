import type { Product } from '../types'
import { formatPrice } from '../catalogue'

/** Single-item product view. `onBack` returns to wherever the user came from. */
export function ProductView({ product, onBack }: { product: Product; onBack: () => void }) {
  return (
    <article className="product-view" data-product-id={product.product_id}>
      <button type="button" className="back-link" onClick={onBack}>
        ← Back to all products
      </button>
      <div className="product-view__layout">
        <div className="product-view__image">
          <img src={product.image} alt={product.name} />
        </div>
        <div className="product-view__info">
          <p className="product-view__type">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="product-view__price">{formatPrice(product.price)}</p>
          <p className="product-view__description">{product.description}</p>
          <h2>Colors</h2>
          <ul className="chips">
            {product.colors.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
          <h2>Tags</h2>
          <ul className="chips chips--muted">
            {product.search_tags.map((t) => (
              <li key={t}>{t}</li>
            ))}
          </ul>
          <p className="product-view__id">Product ID: {product.product_id}</p>
        </div>
      </div>
    </article>
  )
}
