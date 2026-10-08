import type { Product } from '../types'
import { formatPrice } from '../catalogue'
import { productHref } from '../router'

/** The fields a card needs. Storefront products and chatbot results both provide them. */
export type CardProduct = Pick<Product, 'product_id' | 'name' | 'image' | 'price'>

/**
 * Clickable product card: image, name and price. Opens the single-item view (#/product/<id>).
 * `compact` is the smaller layout used inside the chat panel.
 */
export function ProductCard({ product, compact = false }: { product: CardProduct; compact?: boolean }) {
  return (
    <a
      className={compact ? 'product-card product-card--compact' : 'product-card'}
      href={productHref(product.product_id)}
      data-product-id={product.product_id}
    >
      <div className="product-card__image">
        <img src={product.image} alt={product.name} loading="lazy" />
      </div>
      <div className="product-card__body">
        <h3 className="product-card__name">{product.name}</h3>
        <p className="product-card__price">{formatPrice(product.price)}</p>
      </div>
    </a>
  )
}
