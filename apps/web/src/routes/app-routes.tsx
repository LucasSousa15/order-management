import { AuditLogsPage } from '../pages/audit-logs-page'
import { OrdersPage } from '../pages/orders-page'
import { ProductsPage } from '../pages/products-page'
import { PageHeader } from '../components/page-header'
import { paths } from './paths'

export function AppRoutes() {
  switch (window.location.pathname.replace(/\/$/, '') || '/') {
    case '/':
    case paths.products:
      return <ProductsPage />
    case paths.orders:
      return <OrdersPage />
    case paths.auditLogs:
      return <AuditLogsPage />
    default:
      return (
        <section>
          <PageHeader title="Página não encontrada" description="O endereço solicitado não existe." />
          <a href={paths.products}>Ir para produtos</a>
        </section>
      )
  }
}
