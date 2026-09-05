import type { Key, ReactNode } from 'react'
import type { PaginatedResponse } from '../http/pagination'
import { ActivityIndicator } from './activity-indicator'
import { Button } from './button'

export interface TableColumn<T> {
  key: string
  header: string
  render: (row: T) => ReactNode
  className?: string
}

export interface DataTableProps<T> {
  caption: string
  columns: TableColumn<T>[]
  result?: PaginatedResponse<T>
  getRowKey: (row: T) => Key
  onPageChange: (page: number) => void
  onPageSizeChange?: (pageSize: number) => void
  isLoading?: boolean
  isFetching?: boolean
  error?: string | null
  onRetry?: () => void
  emptyMessage?: string
}

export function DataTable<T>({
  caption,
  columns,
  result,
  getRowKey,
  onPageChange,
  onPageSizeChange,
  isLoading = false,
  isFetching = false,
  error,
  onRetry,
  emptyMessage = 'Nenhum registro encontrado.',
}: DataTableProps<T>) {
  const rows = result?.data ?? []
  const meta = result?.meta
  const busy = isLoading || isFetching
  const firstItem = meta && rows.length ? (meta.page - 1) * meta.page_size + 1 : 0
  const lastItem = meta && rows.length ? Math.min(firstItem + rows.length - 1, meta.total_items) : 0

  return (
    <section aria-label={caption} className="overflow-hidden rounded-lg border border-slate-200 bg-white">
      {error && (
        <div role="alert" className="flex flex-wrap items-center justify-between gap-3 border-b border-red-200 bg-red-50 p-4 text-red-800">
          <p>{error}</p>
          {onRetry && <Button variant="secondary" onClick={onRetry} disabled={busy}>Tentar novamente</Button>}
        </div>
      )}
      <p role="status" className={busy ? 'p-4 text-sm text-slate-600' : 'sr-only'}>
        {busy && <ActivityIndicator label={isLoading ? 'Carregando registros...' : 'Atualizando registros...'} />}
      </p>
      <div className="overflow-x-auto">
        <table aria-busy={busy} className="w-full text-left text-sm">
          <caption className="sr-only">{caption}</caption>
          <thead className="border-b border-slate-200 bg-slate-50 text-slate-700">
            <tr>{columns.map((column) => (
              <th key={column.key} scope="col" className={`px-4 py-3 font-semibold ${column.className ?? ''}`}>{column.header}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {rows.map((row) => (
              <tr key={getRowKey(row)}>{columns.map((column) => (
                <td key={column.key} className={`px-4 py-3 ${column.className ?? ''}`}>{column.render(row)}</td>
              ))}</tr>
            ))}
            {!rows.length && !busy && !error && (
              <tr><td colSpan={columns.length} className="p-8 text-center text-slate-500">{emptyMessage}</td></tr>
            )}
          </tbody>
        </table>
      </div>
      {meta && (
        <nav aria-label={`Paginação de ${caption}`} className="flex flex-wrap items-center justify-between gap-4 border-t border-slate-200 p-4 text-sm">
          <p>{firstItem}–{lastItem} de {meta.total_items} registros</p>
          {onPageSizeChange && (
            <label className="flex items-center gap-2">
              Por página
              <select
                value={meta.page_size}
                disabled={busy || Boolean(error)}
                onChange={(event) => onPageSizeChange(Number(event.target.value))}
                className="cursor-pointer rounded border border-slate-300 bg-white p-2 disabled:cursor-not-allowed"
              >
                {[...new Set([10, 20, 50, 100, meta.page_size])].sort((a, b) => a - b).map((size) => (
                  <option key={size} value={size}>{size}</option>
                ))}
              </select>
            </label>
          )}
          <div className="flex items-center gap-3">
            <Button variant="secondary" disabled={busy || !meta.has_previous_page} onClick={() => onPageChange(meta.page - 1)}>Anterior</Button>
            <span>Página {meta.total_pages === 0 ? 0 : meta.page} de {meta.total_pages}</span>
            <Button variant="secondary" disabled={busy || Boolean(error) || !meta.has_next_page} onClick={() => onPageChange(meta.page + 1)}>Próxima</Button>
          </div>
        </nav>
      )}
    </section>
  )
}
