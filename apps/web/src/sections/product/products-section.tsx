import { PageHeader } from '../../components/page-header'

export function ProductsSection() {
  return (
    <section>
      <PageHeader title="Produtos" description="Consulte os produtos e gerencie o estoque." />
      <p className="rounded-lg border border-slate-200 bg-white p-6 text-slate-600">
        Esta funcionalidade estará disponível em breve.
      </p>
    </section>
  )
}
