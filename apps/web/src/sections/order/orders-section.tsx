import { useState } from 'react'
import { Button } from '../../components/button'
import { DataTable } from '../../components/data-table'
import type { TableColumn } from '../../components/data-table'
import { Modal } from '../../components/modal'
import { PageHeader } from '../../components/page-header'
import { useCreateOrder, useDeleteOrder, useOrders, useUpdateOrder } from '../../hooks/orders/use-orders'
import type { Order, OrderInput } from '../../hooks/orders/types'
import { OrderItems } from './order-items'
import { OrderForm } from './order-form'

export function OrdersSection() {
  const [pagination, setPagination] = useState({ page: 1, page_size: 20 })
  const orders = useOrders(pagination)
  const createOrder = useCreateOrder()
  const updateOrder = useUpdateOrder()
  const deleteOrder = useDeleteOrder()
  const [editor, setEditor] = useState<{ order?: Order } | null>(null)
  const [viewingItems, setViewingItems] = useState<Order | null>(null)
  const [deleting, setDeleting] = useState<Order | null>(null)
  const [message, setMessage] = useState('')
  const [deleteError, setDeleteError] = useState('')
  const saving = createOrder.isPending || updateOrder.isPending

  function closeEditor() { if (!saving) setEditor(null) }
  async function handleSubmit(input: OrderInput) {
    if (editor?.order) {
      await updateOrder.mutateAsync({ id: editor.order.id, input })
      setMessage('Pedido atualizado com sucesso.')
    } else {
      await createOrder.mutateAsync(input)
      setMessage('Pedido criado com sucesso.')
    }
    setEditor(null)
  }
  async function handleDelete() {
    if (!deleting) return
    setDeleteError('')
    try {
      await deleteOrder.mutateAsync(deleting.id)
      if (orders.data?.data.length === 1 && pagination.page > 1) {
        setPagination((current) => ({ ...current, page: current.page - 1 }))
      }
      setDeleting(null)
      setMessage('Pedido excluído e estoque restaurado com sucesso.')
    } catch { setDeleteError('Não foi possível excluir o pedido. Tente novamente.') }
  }
  const columns: TableColumn<Order>[] = [
    { key: 'id', header: 'Pedido', render: (order) => `#${order.id}` },
    { key: 'created_at', header: 'Criado em', render: (order) => new Date(order.created_at).toLocaleString('pt-BR') },
    { key: 'actions', header: 'Ações', render: (order) => <div className="flex flex-wrap gap-2">
      <Button variant="secondary" disabled={orders.isFetching} aria-label={`Ver itens do pedido ${order.id}`} onClick={() => { setMessage(''); setViewingItems(order) }}>Ver itens</Button>
    </div> },
  ]

  return (
    <section>
      <div className="mb-4 flex flex-wrap items-start justify-between gap-4">
        <PageHeader title="Pedidos" description="Organize os pedidos e seus itens." />
        <Button className="shrink-0 whitespace-nowrap" onClick={() => { setMessage(''); setEditor({}) }}>Criar pedido</Button>
      </div>
      <p role="status" className={message ? 'mb-4 rounded bg-green-50 p-4 text-green-800' : 'sr-only'}>{message}</p>
      <DataTable caption="Pedidos" columns={columns} result={orders.data} getRowKey={(order) => order.id}
        isLoading={orders.isLoading} isFetching={orders.isFetching}
        error={orders.isError ? 'Não foi possível carregar os pedidos.' : null}
        onRetry={() => { void orders.refetch() }}
        onPageChange={(page) => setPagination((current) => ({ ...current, page }))}
        onPageSizeChange={(page_size) => setPagination({ page: 1, page_size })}
        emptyMessage="Nenhum pedido cadastrado." />
      <Modal size="wide" open={editor !== null} onClose={closeEditor} closeDisabled={saving} title={editor?.order ? `Atualizar pedido #${editor.order.id}` : 'Criar pedido'}>
        {editor && <OrderForm key={editor.order?.id ?? 'new'} order={editor.order} onSubmit={handleSubmit} onCancel={closeEditor} />}
      </Modal>
      <Modal size="wide" open={viewingItems !== null} onClose={() => { if (!updateOrder.isPending) setViewingItems(null) }} closeDisabled={updateOrder.isPending} title={`Itens do pedido #${viewingItems?.id ?? ''}`}
        footer={viewingItems && <div className="flex flex-wrap gap-3">
          <Button variant="secondary" disabled={updateOrder.isPending} onClick={() => {
            setEditor({ order: viewingItems })
            setViewingItems(null)
          }}>Adicionar produtos ao pedido</Button>
          <Button variant="danger" disabled={updateOrder.isPending} onClick={() => {
            setDeleteError('')
            setDeleting(viewingItems)
            setViewingItems(null)
          }}>Excluir pedido</Button>
        </div>}>
        {viewingItems && <OrderItems key={viewingItems.id} order={viewingItems}
          onCancel={() => { if (!updateOrder.isPending) setViewingItems(null) }}
          onSave={async (input) => {
            await updateOrder.mutateAsync({ id: viewingItems.id, input })
            setViewingItems(null)
            setMessage('Itens do pedido atualizados com sucesso.')
          }} />}
      </Modal>
      <Modal open={deleting !== null} onClose={() => { if (!deleteOrder.isPending) setDeleting(null) }} closeDisabled={deleteOrder.isPending} title="Excluir pedido">
        <p>Excluir o pedido #{deleting?.id}? As quantidades dos itens serão devolvidas ao estoque.</p>
        {deleteError && <p role="alert" className="mt-4 text-red-700">{deleteError}</p>}
        <div className="mt-4 flex justify-end gap-3">
          <Button variant="secondary" disabled={deleteOrder.isPending} onClick={() => setDeleting(null)}>Cancelar</Button>
          <Button variant="danger" isLoading={deleteOrder.isPending} loadingLabel="Excluindo..." onClick={() => { void handleDelete() }}>Excluir pedido</Button>
        </div>
      </Modal>
    </section>
  )
}
