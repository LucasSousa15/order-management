import { useState } from 'react'
import { Button } from '../../components/button'
import { DataTable } from '../../components/data-table'
import type { TableColumn } from '../../components/data-table'
import { Modal } from '../../components/modal'
import { PageHeader } from '../../components/page-header'
import { useLogs } from '../../hooks/audit-logs/use-logs'
import type { AuditLog } from '../../hooks/audit-logs/types'

const eventLabels: Record<AuditLog['event_type'], string> = {
  PRODUCT_CREATED: 'Produto criado',
  PRODUCT_UPDATED: 'Produto atualizado',
  PRODUCT_DELETED: 'Produto excluído',
  ORDER_CREATED: 'Pedido criado',
  ORDER_UPDATED: 'Pedido atualizado',
  ORDER_DELETED: 'Pedido excluído',
  STOCK_MOVEMENT: 'Movimentação de estoque',
}

const entityLabels: Record<AuditLog['entity_type'], string> = {
  PRODUCT: 'Produto',
  ORDER: 'Pedido',
}

export function AuditLogsSection() {
  const [pagination, setPagination] = useState({ page: 1, page_size: 20 })
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null)
  const logs = useLogs(pagination)
  const columns: TableColumn<AuditLog>[] = [
    { key: 'created_at', header: 'Data', render: (log) => new Date(log.created_at).toLocaleString('pt-BR') },
    { key: 'event_type', header: 'Evento', render: (log) => eventLabels[log.event_type] },
    { key: 'entity', header: 'Entidade', render: (log) => `${entityLabels[log.entity_type]} #${log.entity_id}` },
    {
      key: 'details',
      header: 'Detalhes',
      render: (log) => (
        <Button variant="secondary" aria-label={`Ver detalhes do evento ${log.id}`} onClick={() => setSelectedLog(log)}>
          Ver detalhes
        </Button>
      ),
    },
  ]

  return (
    <section>
      <PageHeader title="Auditoria" description="Acompanhe o histórico de produtos, pedidos e estoque." />
      <DataTable
        caption="Logs de auditoria"
        columns={columns}
        result={logs.data}
        getRowKey={(log) => log.id}
        isLoading={logs.isLoading}
        isFetching={logs.isFetching}
        error={logs.isError ? 'Não foi possível carregar os logs de auditoria.' : null}
        onRetry={() => { void logs.refetch() }}
        onPageChange={(page) => setPagination((current) => ({ ...current, page }))}
        onPageSizeChange={(page_size) => setPagination({ page: 1, page_size })}
        emptyMessage="Nenhum evento de auditoria registrado."
      />
      <Modal
        size="wide"
        open={selectedLog !== null}
        onClose={() => setSelectedLog(null)}
        title={`Detalhes do evento #${selectedLog?.id ?? ''}`}
        description={selectedLog ? `${eventLabels[selectedLog.event_type]} — ${entityLabels[selectedLog.entity_type]} #${selectedLog.entity_id}` : undefined}
      >
        {selectedLog && (
          <pre className="overflow-x-auto rounded-lg bg-slate-950 p-4 text-sm text-slate-100">
            {JSON.stringify(selectedLog.details, null, 2)}
          </pre>
        )}
      </Modal>
    </section>
  )
}
