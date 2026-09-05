export function ActivityIndicator({ label = 'Carregando...' }: { label?: string }) {
  return (
    <span className="inline-flex items-center gap-2">
      <span aria-hidden="true" className="inline-block size-4 shrink-0 animate-spin rounded-full border-2 border-current border-r-transparent motion-reduce:animate-none" />
      <span>{label}</span>
    </span>
  )
}
