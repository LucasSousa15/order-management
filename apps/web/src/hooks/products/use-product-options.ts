import { useQuery } from '@tanstack/react-query'
import { axiosInstance } from '../../http/api'
import type { PaginatedResponse } from '../../http/pagination'
import type { Product } from './types'

export function useProductOptions() {
  return useQuery({
    queryKey: ['products', 'options'],
    queryFn: async ({ signal }) => {
      const products: Product[] = []
      let page = 1
      while (true) {
        const { data } = await axiosInstance.get<PaginatedResponse<Product>>('/products', {
          params: { page, page_size: 100 }, signal,
        })
        products.push(...data.data)
        if (!data.meta.has_next_page) return products
        page += 1
      }
    },
  })
}
