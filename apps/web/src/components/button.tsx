import { ActivityIndicator } from './activity-indicator'
import type { ComponentPropsWithoutRef } from 'react'

export type ButtonProps = ComponentPropsWithoutRef<'button'> & {
  variant?: 'primary' | 'secondary' | 'danger'
  isLoading?: boolean
  loadingLabel?: string
}

const variants = {
  primary: 'bg-blue-700 text-white hover:bg-blue-800',
  secondary: 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-100',
  danger: 'bg-red-700 text-white hover:bg-red-800',
}

export function Button({
  variant = 'primary',
  type = 'button',
  isLoading = false,
  loadingLabel = 'Aguarde...',
  disabled,
  className = '',
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      {...props}
      type={type}
      disabled={disabled || isLoading}
      aria-busy={isLoading || undefined}
      className={`inline-flex cursor-pointer items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${variants[variant]} ${className}`}
    >
      {isLoading ? <ActivityIndicator label={loadingLabel} /> : children}
    </button>
  )
}
