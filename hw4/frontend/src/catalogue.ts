import { useEffect, useState } from 'react'
import type { Product } from './types'

/** Loads the catalogue exported from the database (public/catalogue.json). */
export function useCatalogue() {
  const [products, setProducts] = useState<Product[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/catalogue.json')
      .then((res) => {
        if (!res.ok) throw new Error(`Could not load the catalogue (${res.status})`)
        return res.json() as Promise<Product[]>
      })
      .then(setProducts)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return { products, error, loading }
}

export const formatPrice = (price: number) =>
  price.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
