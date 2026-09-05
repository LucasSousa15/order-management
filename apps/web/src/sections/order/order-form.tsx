import { zodResolver } from '@hookform/resolvers/zod'
import { isAxiosError } from 'axios'
import { useFieldArray, useForm, useWatch } from 'react-hook-form'
import { ActivityIndicator } from '../../components/activity-indicator'
import { Button } from '../../components/button'
import { Input } from '../../components/input'
import { useProductOptions } from '../../hooks/products/use-product-options'
import type { Order, OrderInput } from '../../hooks/orders/types'
import { orderSchema } from '../../schemas/order-schema'
import type { OrderFormData, OrderFormValues } from '../../schemas/order-schema'

export function OrderForm({ order, onSubmit, onCancel }: {
  order?: Order
  onSubmit: (input: OrderInput) => Promise<void>
  onCancel: () => void
}) {
  const products = useProductOptions()
  const { control, register, handleSubmit, setError, formState: { errors, isSubmitting } } = useForm<OrderFormValues, unknown, OrderFormData>({
    resolver: zodResolver(orderSchema),
    defaultValues: { items: order ? order.items.map((item) => ({ product_id: String(item.product_id), quantity: String(item.quantity) })) : [{ product_id: '', quantity: '1' }] },
  })
  const { fields, append, remove } = useFieldArray({ control, name: 'items' })
  const selectedItems = useWatch({ control, name: 'items' })
  function available(productId: number) {
    const product = products.data?.find((entry) => entry.id === productId)
    return product ? product.stock_quantity + (order?.items.find((item) => item.product_id === productId)?.quantity ?? 0) : 0
  }
  const exceedsStock = selectedItems.some((item) => Number(item.quantity) > available(Number(item.product_id)))
  const submit = handleSubmit(async (input) => {
    if (!products.isSuccess || products.isFetching) return
    let invalid = false
    input.items.forEach((item, index) => {
      if (item.quantity > available(item.product_id)) {
        setError(`items.${index}.quantity`, { message: `Máximo disponível: ${available(item.product_id)}.` })
        invalid = true
      }
    })
    if (invalid) return
    try { await onSubmit(input) } catch (error) {
      setError('root', { message: isAxiosError(error) && error.response?.status === 409
        ? 'Estoque insuficiente. Revise os produtos e as quantidades.'
        : 'Não foi possível salvar o pedido. Confira os dados e tente novamente.' })
    }
  })

  return (
    <form onSubmit={submit} noValidate className="space-y-4">
      {products.isLoading && <p role="status"><ActivityIndicator label="Carregando produtos..." /></p>}
      {products.isError && <div role="alert">Não foi possível carregar os produtos. <Button variant="secondary" onClick={() => { void products.refetch() }}>Tentar novamente</Button></div>}
      {products.isSuccess && !products.data.length && <p>Cadastre um produto antes de criar um pedido.</p>}
      <fieldset disabled={isSubmitting || !products.isSuccess || !products.data?.length} className="space-y-4">
        <legend className="sr-only">Itens do pedido</legend>
        {fields.map((field, index) => (
          <div key={field.id} className="space-y-3 rounded border border-slate-200 p-3">
            <label className="block text-sm font-medium">
              Produto {index + 1}
              <select {...register(`items.${index}.product_id`)} aria-invalid={Boolean(errors.items?.[index]?.product_id)} className="mt-2 w-full cursor-pointer rounded border border-slate-300 p-2 disabled:cursor-not-allowed">
                <option value="">Selecione um produto</option>
                {products.data?.map((product) => <option key={product.id} value={product.id}>{product.name} ({product.sku}) — estoque: {product.stock_quantity}</option>)}
              </select>
            </label>
            {errors.items?.[index]?.product_id && <p role="alert" className="text-sm text-red-700">Selecione um produto válido.</p>}
            <Input label="Quantidade" type="number" min={1} max={available(Number(selectedItems[index]?.product_id))} step={1} inputMode="numeric" required
              hint={`Máximo disponível para este pedido: ${available(Number(selectedItems[index]?.product_id))}.`} {...register(`items.${index}.quantity`)} error={Number(selectedItems[index]?.quantity) > available(Number(selectedItems[index]?.product_id)) ? 'Quantidade acima do estoque disponível.' : errors.items?.[index]?.quantity?.message} />
            <Button variant="secondary" onClick={() => remove(index)} disabled={fields.length === 1}>Remover item {index + 1}</Button>
          </div>
        ))}
        <Button variant="secondary" onClick={() => append({ product_id: '', quantity: '1' })}>Adicionar item</Button>
      </fieldset>
      {(errors.items?.root?.message || errors.items?.message) && <p role="alert" className="text-red-700">{errors.items?.root?.message || errors.items?.message}</p>}
      {errors.root && <p role="alert" className="text-red-700">{errors.root.message}</p>}
      <div className="flex justify-end gap-3">
        <Button variant="secondary" onClick={onCancel} disabled={isSubmitting}>Cancelar</Button>
        <Button type="submit" isLoading={isSubmitting} disabled={!products.isSuccess || products.isFetching || !products.data?.length || exceedsStock} loadingLabel="Salvando...">{order ? 'Salvar alterações' : 'Criar pedido'}</Button>
      </div>
    </form>
  )
}
