import assert from 'node:assert/strict'
import { test } from 'node:test'
import { productSchema } from '../src/schemas/product-schema.ts'

const valid = { name: ' Produto ', sku: ' abc ', price: '12,50', stock_quantity: '3' }

test('normaliza campos e gera o payload esperado pela API', () => {
  assert.deepEqual(productSchema.parse(valid), {
    name: 'Produto', sku: 'ABC', price: '12.50', stock_quantity: 3,
  })
})

test('aceita limites de preço e estoque e estoque zero', () => {
  for (const stock_quantity of ['0', '2147483647']) {
    assert.equal(productSchema.safeParse({ ...valid, price: '9999999999.99', stock_quantity }).success, true)
  }
})

test('rejeita campos vazios, preços inválidos e estoque fora do contrato', () => {
  for (const fields of [
    { name: ' ' }, { name: 'a'.repeat(121) }, { sku: ' ' }, { sku: 'a'.repeat(65) },
    { price: '' }, { price: '0' }, { price: '-1' }, { price: '1.234' },
    { price: '10000000000' }, { price: 'NaN' }, { price: '1.234,56' },
    { stock_quantity: '' }, { stock_quantity: '-1' }, { stock_quantity: '1.5' },
    { stock_quantity: '2147483648' },
  ]) {
    assert.equal(productSchema.safeParse({ ...valid, ...fields }).success, false, JSON.stringify(fields))
  }
})
