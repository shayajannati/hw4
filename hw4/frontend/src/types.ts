/** One product from the `catalogue` table of data/campus_customs.db. */
export interface Product {
  product_id: string // primary key in the database; links to inventory and chatbot results
  name: string
  garment_type: string
  description: string
  colors: string[]
  search_tags: string[]
  image: string // served from /products/<product_id>.jpg
  price: number
}
