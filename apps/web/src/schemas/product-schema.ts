import { z } from 'zod'

export const productSchema = z.object({
  name: z.string().trim().min(1, 'Informe o nome.').max(120, 'Use no máximo 120 caracteres.'),
  sku: z.string().trim().toUpperCase().min(1, 'Informe o SKU.').max(64, 'Use no máximo 64 caracteres.'),
  price: z.string().trim()
    .transform((value) => value.replace(',', '.'))
    .pipe(z.string().regex(/^\d+(\.\d{1,2})?$/, 'Informe um preço com até duas casas decimais.'))
    .refine((value) => /[1-9]/.test(value), 'O preço deve ser maior que zero.')
    .refine((value) => value.split('.')[0].replace(/^0+/, '').length <= 10, 'O preço máximo é 9999999999,99.'),
  stock_quantity: z.string().trim()
    .regex(/^\d+$/, 'Informe um estoque inteiro maior ou igual a zero.')
    .transform(Number)
    .pipe(z.number().int().min(0).max(2147483647, 'O estoque máximo é 2147483647.')),
})

export type ProductFormValues = z.input<typeof productSchema>
export type ProductFormData = z.output<typeof productSchema>

export const productDefaultValues: ProductFormValues = {
  name: '',
  sku: '',
  price: '',
  stock_quantity: '0',
}
