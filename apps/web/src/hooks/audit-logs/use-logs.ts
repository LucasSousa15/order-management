import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { axiosInstance } from '../../http/api'
import type { PaginatedResponse, PaginationParams } from '../../http/pagination'
import type { AuditLog } from './types'

export function useLogs({ page = 1, page_size = 20 }: PaginationParams = {}) {
  return useQuery({
    queryKey: ['audit-logs', 'list', { page, page_size }],
    queryFn: async ({ signal }) => {
      const response = await axiosInstance.get<PaginatedResponse<AuditLog>>('/audit-logs', {
        params: { page, page_size },
        signal,
      })
      return response.data
    },
    placeholderData: keepPreviousData,
  })
}
