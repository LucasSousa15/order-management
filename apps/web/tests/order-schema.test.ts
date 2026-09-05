import assert from 'node:assert/strict'
import { test } from 'node:test'
import { orderSchema } from '../src/schemas/order-schema.ts'

test('converte múltiplos itens para o contrato da API', () => {
  assert.deepEqual(orderSchema.parse({ items: [{ product_id: '1', quantity: '2' }, { product_id: '2', quantity: '3' }] }), { items: [{ product_id: 1, quantity: 2 }, { product_id: 2, quantity: 3 }] })
})

test('rejeita pedido vazio, duplicatas e quantidades inválidas', () => {
  for (const items of [[], [{ product_id: '1', quantity: '0' }], [{ product_id: '', quantity: '1' }], [{ product_id: '1', quantity: '-1' }], [{ product_id: '1', quantity: '1.5' }], [{ product_id: '1', quantity: '2' }, { product_id: '01', quantity: '3' }]]) {
    assert.equal(orderSchema.safeParse({ items }).success, false)
  }
})
