import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Button } from '../../components/button'
import { Input } from '../../components/input'
import type { ProductInput } from '../../hooks/products/types'
import { productDefaultValues, productSchema } from '../../schemas/product-schema'
import type { ProductFormData, ProductFormValues } from '../../schemas/product-schema'

export interface ProductFormProps {
  onSubmit: (product: ProductInput) => void | Promise<void>
  onCancel?: () => void
  defaultValues?: ProductFormValues
  submitLabel?: string
}

export function ProductForm({
  onSubmit,
  onCancel,
  defaultValues = productDefaultValues,
  submitLabel = 'Salvar produto',
}: ProductFormProps) {
  const { register, handleSubmit, setError, clearErrors, formState: { errors, isSubmitting } } = useForm<ProductFormValues, unknown, ProductFormData>({
    resolver: zodResolver(productSchema),
    defaultValues,
  })

  const submit = handleSubmit(async (values) => {
    clearErrors('root')
    try {
      await onSubmit(values)
    } catch {
      setError('root', { message: 'Não foi possível salvar o produto. Confira os dados e tente novamente.' })
    }
  })

  return (
    <form onSubmit={submit} noValidate className="space-y-5">
      <fieldset disabled={isSubmitting} className="space-y-5">
        <legend className="sr-only">Dados do produto</legend>
        <Input label="Nome" required maxLength={120} autoComplete="off" {...register('name')} error={errors.name?.message} />
        <Input label="SKU" required maxLength={64} autoComplete="off" hint="Código único do produto." {...register('sku')} error={errors.sku?.message} />
        <Input label="Preço" required inputMode="decimal" placeholder="0,00" {...register('price')} error={errors.price?.message} />
        <Input label="Quantidade em estoque" required inputMode="numeric" {...register('stock_quantity')} error={errors.stock_quantity?.message} />
      </fieldset>
      {errors.root && <p role="alert" className="text-sm text-red-700">{errors.root.message}</p>}
      <div className="flex flex-wrap justify-end gap-3">
        {onCancel && <Button variant="secondary" onClick={onCancel} disabled={isSubmitting}>Cancelar</Button>}
        <Button type="submit" isLoading={isSubmitting} loadingLabel="Salvando...">{submitLabel}</Button>
      </div>
    </form>
  )
}
