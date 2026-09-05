import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { axiosInstance } from '../../http/api'
import type { PaginatedResponse, PaginationParams } from '../../http/pagination'
import type { Order, OrderInput } from './types'

export function useOrders({ page = 1, page_size = 20 }: PaginationParams = {}) {
  return useQuery({
    queryKey: ['orders', 'list', { page, page_size }],
    queryFn: async ({ signal }) => {
      const response = await axiosInstance.get<PaginatedResponse<Order>>('/orders', {
        params: { page, page_size },
        signal,
      })
      return response.data
    },
    placeholderData: keepPreviousData,
  })
}

export function useOrder(id: number) {
  return useQuery({
    queryKey: ['orders', 'detail', id],
    enabled: Number.isSafeInteger(id) && id > 0,
    queryFn: async ({ signal }) => {
      const response = await axiosInstance.get<Order>(`/orders/${id}`, { signal })
      return response.data
    },
  })
}

export function useCreateOrder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (input: OrderInput) => {
      const response = await axiosInstance.post<Order>('/orders', input)
      return response.data
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['orders'] }),
        queryClient.invalidateQueries({ queryKey: ['products'] }),
        queryClient.invalidateQueries({ queryKey: ['audit-logs'] }),
      ])
    },
  })
}

export function useUpdateOrder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, input }: { id: number; input: OrderInput }) => {
      const response = await axiosInstance.put<Order>(`/orders/${id}`, input)
      return response.data
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['orders'] }),
        queryClient.invalidateQueries({ queryKey: ['products'] }),
        queryClient.invalidateQueries({ queryKey: ['audit-logs'] }),
      ])
    },
  })
}

export function useDeleteOrder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await axiosInstance.delete<void>(`/orders/${id}`)
    },
    onSuccess: async (_, id) => {
      queryClient.removeQueries({ queryKey: ['orders', 'detail', id], exact: true })
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['orders'] }),
        queryClient.invalidateQueries({ queryKey: ['products'] }),
        queryClient.invalidateQueries({ queryKey: ['audit-logs'] }),
      ])
    },
  })
}
