import { useEffect, useState } from 'react'

/** Link to the single-item view. Anything (grid, chatbot results) can open a product with this. */
export const productHref = (productId: string) => `#/product/${encodeURIComponent(productId)}`

/** The product_id in the URL hash, or null when showing the grid. */
export function useSelectedProductId(): string | null {
  const read = () => {
    const match = window.location.hash.match(/^#\/product\/(.+)$/)
    return match ? decodeURIComponent(match[1]) : null
  }
  const [id, setId] = useState(read)
  useEffect(() => {
    const onChange = () => {
      setId(read())
      window.scrollTo({ top: 0 })
    }
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])
  return id
}
