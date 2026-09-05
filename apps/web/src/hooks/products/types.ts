export interface Product {
  id: number
  name: string
  sku: string
  price: string
  stock_quantity: number
  created_at: string
}

export interface ProductInput {
  name: string
  sku: string
  price: string
  stock_quantity: number
}
