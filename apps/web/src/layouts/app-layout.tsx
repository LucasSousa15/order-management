import type { ReactNode } from 'react'
import { paths } from '../routes/paths'

const navigation = [
  { href: paths.products, label: 'Produtos' },
  { href: paths.orders, label: 'Pedidos' },
  { href: paths.auditLogs, label: 'Auditoria' },
]

export function AppLayout({ children }: { children: ReactNode }) {
  const pathname = window.location.pathname.replace(/\/$/, '') || paths.products

  return (
    <div className="min-h-screen">
      <a href="#main-content" className="sr-only focus:not-sr-only">Pular para o conteúdo</a>
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-5">
          <a href={paths.products} className="font-semibold text-slate-900">Order Management</a>
          <nav aria-label="Navegação principal" className="flex flex-wrap gap-2">
            {navigation.map(({ href, label }) => (
              <a
                key={href}
                href={href}
                aria-current={pathname === href ? 'page' : undefined}
                className="rounded-md px-3 py-2 text-sm hover:bg-slate-100 aria-[current=page]:bg-blue-50 aria-[current=page]:text-blue-700"
              >
                {label}
              </a>
            ))}
          </nav>
        </div>
      </header>
      <main id="main-content" tabIndex={-1} className="mx-auto max-w-6xl px-6 py-8">{children}</main>
    </div>
  )
}
