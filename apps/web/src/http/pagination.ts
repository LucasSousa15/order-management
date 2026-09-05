export interface PaginationParams {
  page?: number
  page_size?: number
}

export interface PaginatedResponse<T> {
  data: T[]
  meta: {
    page: number
    page_size: number
    total_items: number
    total_pages: number
    has_next_page: boolean
    has_previous_page: boolean
  }
}
