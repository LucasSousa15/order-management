import { z } from 'zod'

const positiveInteger = z.string().regex(/^\d+$/, 'Informe um inteiro positivo.')
  .transform(Number).pipe(z.number().int().positive('O valor deve ser maior que zero.').max(Number.MAX_SAFE_INTEGER))

export const orderSchema = z.object({
  items: z.array(z.object({ product_id: positiveInteger, quantity: positiveInteger }))
    .min(1, 'Adicione pelo menos um produto.')
    .refine((items) => new Set(items.map((item) => item.product_id)).size === items.length, 'Selecione cada produto apenas uma vez.'),
})

export type OrderFormValues = z.input<typeof orderSchema>
export type OrderFormData = z.output<typeof orderSchema>
