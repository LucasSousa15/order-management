import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { axiosInstance } from '../../http/api'
import type { PaginatedResponse, PaginationParams } from '../../http/pagination'
import type { Product, ProductInput } from './types'

export function useProducts({ page = 1, page_size = 20 }: PaginationParams = {}) {
  return useQuery({
    queryKey: ['products', 'list', { page, page_size }],
    queryFn: async ({ signal }) => {
      const response = await axiosInstance.get<PaginatedResponse<Product>>('/products', {
        params: { page, page_size },
        signal,
      })
      return response.data
    },
    placeholderData: keepPreviousData,
  })
}

export function useProduct(id: number) {
  return useQuery({
    queryKey: ['products', 'detail', id],
    enabled: Number.isSafeInteger(id) && id > 0,
    queryFn: async ({ signal }) => {
      const response = await axiosInstance.get<Product>(`/products/${id}`, { signal })
      return response.data
    },
  })
}

export function useCreateProduct() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (input: ProductInput) => {
      const response = await axiosInstance.post<Product>('/products', input)
      return response.data
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['products'] }),
        queryClient.invalidateQueries({ queryKey: ['audit-logs'] }),
      ])
    },
  })
}

export function useUpdateProduct() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, input }: { id: number; input: ProductInput }) => {
      const response = await axiosInstance.put<Product>(`/products/${id}`, input)
      return response.data
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['products'] }),
        queryClient.invalidateQueries({ queryKey: ['audit-logs'] }),
      ])
    },
  })
}

export function useDeleteProduct() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await axiosInstance.delete<void>(`/products/${id}`)
    },
    onSuccess: async (_, id) => {
      queryClient.removeQueries({ queryKey: ['products', 'detail', id], exact: true })
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['products'] }),
        queryClient.invalidateQueries({ queryKey: ['audit-logs'] }),
      ])
    },
  })
}
