import { useProductOptions } from '../../hooks/products/use-product-options'
import { ActivityIndicator } from '../../components/activity-indicator'
import { useState } from 'react'
import { isAxiosError } from 'axios'
import { Button } from '../../components/button'
import { Input } from '../../components/input'
import type { Order, OrderInput } from '../../hooks/orders/types'

const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

export function OrderItems({ order, onSave, onCancel }: {
  order: Order
  onSave: (input: OrderInput) => Promise<void>
  onCancel: () => void
}) {
  const products = useProductOptions()
  const [items, setItems] = useState(() => order.items.map((item) => ({ ...item, quantity: String(item.quantity) })))
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const dirty = items.length !== order.items.length || items.some((item) => item.quantity !== String(order.items.find((original) => original.id === item.id)?.quantity))

  function available(productId: number) {
    const product = products.data?.find((entry) => entry.id === productId)
    return product ? product.stock_quantity + (order.items.find((item) => item.product_id === productId)?.quantity ?? 0) : 0
  }
  const exceedsStock = items.some((item) => Number(item.quantity) > available(item.product_id))

  async function handleSave() {
    if (!products.isSuccess || products.isFetching || exceedsStock) return
    setError('')
    if (items.some((item) => !/^\d+$/.test(item.quantity) || !Number.isSafeInteger(Number(item.quantity)) || Number(item.quantity) <= 0)) {
      setError('Informe quantidades inteiras maiores que zero.')
      return
    }
    setSaving(true)
    try {
      await onSave({ items: items.map((item) => ({ product_id: item.product_id, quantity: Number(item.quantity) })) })
    } catch (cause) {
      setError(isAxiosError(cause) && cause.response?.status === 409 ? 'Estoque insuficiente para as quantidades informadas.' : 'Não foi possível salvar os itens. Tente novamente.')
    } finally { setSaving(false) }
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-600">Altere as quantidades ou remova itens e clique em Salvar alterações para confirmar.</p>
      {products.isFetching && <p role="status"><ActivityIndicator label="Consultando estoque..." /></p>}
      {products.isError && <div role="alert">Não foi possível consultar o estoque. <Button variant="secondary" onClick={() => { void products.refetch() }}>Tentar novamente</Button></div>}
      <ul className="space-y-3">
        {items.map((item) => <li key={item.id} className="space-y-3 rounded-lg border border-slate-200 p-4">
          <h3 className="font-semibold">Produto #{item.product_id}</h3>
          <p className="text-sm">Preço unitário do pedido: {currency.format(Number(item.unit_price))}</p>
          <Input label={`Quantidade do produto #${item.product_id}`} type="number" min={1} max={available(item.product_id)} step={1} inputMode="numeric" value={item.quantity} disabled={saving || !products.isSuccess}
            hint={products.isSuccess ? `Máximo disponível para este pedido: ${available(item.product_id)}.` : undefined}
            error={products.isSuccess && Number(item.quantity) > available(item.product_id) ? 'Quantidade acima do estoque disponível.' : undefined}
            onChange={(event) => setItems((current) => current.map((entry) => entry.id === item.id ? { ...entry, quantity: event.target.value } : entry))} />
          <Button variant="danger" disabled={saving || items.length === 1} onClick={() => setItems((current) => current.filter((entry) => entry.id !== item.id))}>Remover item</Button>
        </li>)}
      </ul>
      {items.length === 1 && <p className="text-sm text-slate-600">O pedido precisa manter pelo menos um item. Para remover todos, exclua o pedido.</p>}
      {error && <p role="alert" className="text-red-700">{error}</p>}
      <div className="flex flex-wrap justify-end gap-3">
        <Button variant="secondary" disabled={saving} onClick={onCancel}>Cancelar</Button>
        <Button disabled={!dirty || !products.isSuccess || products.isFetching || exceedsStock} isLoading={saving} loadingLabel="Salvando..." onClick={() => { void handleSave() }}>Salvar alterações</Button>
      </div>
    </div>
  )
}
