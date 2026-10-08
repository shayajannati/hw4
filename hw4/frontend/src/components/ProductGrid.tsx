import type { Product } from '../types'
import { ProductCard } from './ProductCard'

/** Responsive grid of product cards. */
export function ProductGrid({ products }: { products: Product[] }) {
  if (products.length === 0) return <p className="empty">No products match your search.</p>
  return (
    <div className="product-grid">
      {products.map((p) => (
        <ProductCard key={p.product_id} product={p} />
      ))}
    </div>
  )
}
