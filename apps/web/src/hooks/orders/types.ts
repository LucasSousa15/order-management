export interface Order {
  id: number
  created_at: string
  items: {
    id: number
    product_id: number
    quantity: number
    unit_price: string
  }[]
}

export interface OrderInput {
  items: {
    product_id: number
    quantity: number
  }[]
}
