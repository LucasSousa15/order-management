import { useId } from 'react'
import type { ComponentPropsWithRef } from 'react'

export type InputProps = ComponentPropsWithRef<'input'> & {
  label: string
  error?: string
  hint?: string
}

export function Input({ label, error, hint, id, className = '', ...props }: InputProps) {
  const generatedId = useId()
  const inputId = id ?? generatedId
  const hintId = `${inputId}-hint`
  const errorId = `${inputId}-error`
  const describedBy = [props['aria-describedby'], hint ? hintId : undefined, error ? errorId : undefined]
    .filter(Boolean).join(' ') || undefined

  return (
    <div className="space-y-2">
      <label htmlFor={inputId} className="block text-sm font-medium text-slate-800">
        {label}{props.required && <span aria-hidden="true"> *</span>}
      </label>
      <input
        {...props}
        id={inputId}
        aria-invalid={error ? true : props['aria-invalid']}
        aria-describedby={describedBy}
        className={`block w-full rounded-md border bg-white px-3 py-2 text-slate-900 outline-none focus:ring-2 focus:ring-blue-600 disabled:cursor-not-allowed disabled:bg-slate-100 ${error ? 'border-red-600' : 'border-slate-300'} ${className}`}
      />
      {hint && <p id={hintId} className="text-sm text-slate-500">{hint}</p>}
      {error && <p id={errorId} role="alert" className="text-sm text-red-700">{error}</p>}
    </div>
  )
}
