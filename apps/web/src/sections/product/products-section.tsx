import { useState } from 'react'
import { DataTable } from '../../components/data-table'
import type { TableColumn } from '../../components/data-table'
import { Button } from '../../components/button'
import { Modal } from '../../components/modal'
import { PageHeader } from '../../components/page-header'
import { useCreateProduct, useProducts, useUpdateProduct } from '../../hooks/products/use-products'
import type { Product, ProductInput } from '../../hooks/products/types'
import { ProductForm } from './product-form'

const priceFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
})

const columns: TableColumn<Product>[] = [
  { key: 'name', header: 'Nome', render: (product) => product.name },
  { key: 'sku', header: 'SKU', render: (product) => product.sku },
  { key: 'price', header: 'Preço', render: (product) => priceFormatter.format(Number(product.price)) },
  { key: 'stock_quantity', header: 'Estoque', render: (product) => product.stock_quantity },
]

export function ProductsSection() {
  const [pagination, setPagination] = useState({ page: 1, page_size: 20 })
  const products = useProducts(pagination)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const createProduct = useCreateProduct()
  const updateProduct = useUpdateProduct()
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)

  function handleEditClose() {
    if (!updateProduct.isPending) setEditingProduct(null)
  }

  async function handleUpdate(input: ProductInput) {
    if (!editingProduct) return
    const product = await updateProduct.mutateAsync({ id: editingProduct.id, input })
    setEditingProduct(null)
    setSuccessMessage(`Produto "${product.name}" atualizado com sucesso.`)
  }

  const tableColumns: TableColumn<Product>[] = [
    ...columns,
    {
      key: 'actions',
      header: 'Ações',
      render: (product) => (
        <Button
          variant="secondary"
          aria-label={`Atualizar produto ${product.name}`}
          disabled={products.isFetching || products.isError}
          onClick={() => {
            setSuccessMessage('')
            updateProduct.reset()
            setEditingProduct(product)
          }}
        >
          Atualizar
        </Button>
      ),
    },
  ]

  function handleClose() {
    if (!createProduct.isPending) setIsCreateOpen(false)
  }

  async function handleSubmit(input: ProductInput) {
    const product = await createProduct.mutateAsync(input)
    setIsCreateOpen(false)
    setSuccessMessage(`Produto "${product.name}" criado com sucesso.`)
  }

  return (
    <section>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <PageHeader title="Produtos" description="Consulte os produtos e gerencie o estoque." />
        <Button onClick={() => {
          setSuccessMessage('')
          createProduct.reset()
          setIsCreateOpen(true)
        }}>Criar produto</Button>
      </div>
      <p role="status" className={successMessage ? 'mb-4 rounded-md bg-green-50 p-4 text-green-800' : 'sr-only'}>
        {successMessage}
      </p>
      <DataTable
        caption="Produtos"
        columns={tableColumns}
        result={products.data}
        getRowKey={(product) => product.id}
        isLoading={products.isLoading}
        isFetching={products.isFetching}
        error={products.isError ? 'Não foi possível carregar os produtos. Tente novamente.' : null}
        onRetry={() => { void products.refetch() }}
        onPageChange={(page) => setPagination((current) => ({ ...current, page }))}
        onPageSizeChange={(page_size) => setPagination({ page: 1, page_size })}
        emptyMessage="Nenhum produto cadastrado. Clique em Criar produto para começar."
      />
      <Modal
        open={isCreateOpen}
        onClose={handleClose}
        closeDisabled={createProduct.isPending}
        title="Criar produto"
        description="Preencha os dados do produto e a quantidade inicial em estoque."
      >
        {isCreateOpen && (
          <ProductForm onSubmit={handleSubmit} onCancel={handleClose} submitLabel="Criar produto" />
        )}
      </Modal>
      <Modal
        open={editingProduct !== null}
        onClose={handleEditClose}
        closeDisabled={updateProduct.isPending}
        title="Atualizar produto"
        description="Edite os dados do produto e salve as alterações."
      >
        {editingProduct && (
          <ProductForm
            key={editingProduct.id}
            defaultValues={{
              name: editingProduct.name,
              sku: editingProduct.sku,
              price: editingProduct.price,
              stock_quantity: String(editingProduct.stock_quantity),
            }}
            onSubmit={handleUpdate}
            onCancel={handleEditClose}
            submitLabel="Salvar alterações"
          />
        )}
      </Modal>
    </section>
  )
}
