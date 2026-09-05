import { useEffect, useId, useRef } from 'react'
import type { ReactNode } from 'react'
import { Button } from './button'

export interface ModalProps {
  open: boolean
  onClose: () => void
  title: string
  description?: string
  children: ReactNode
  footer?: ReactNode
  closeDisabled?: boolean
  size?: 'default' | 'wide'
}

const modalSizes = {
  default: 'max-w-lg',
  wide: 'max-w-3xl',
}

export function Modal({ open, onClose, title, description, children, footer, closeDisabled = false, size = 'default' }: ModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const titleId = useId()
  const descriptionId = useId()

  useEffect(() => {
    const dialog = dialogRef.current
    if (!open || !dialog) return

    const previouslyFocused = document.activeElement
    const previousOverflow = document.body.style.overflow
    dialog.showModal()
    document.body.style.overflow = 'hidden'

    return () => {
      dialog.close()
      document.body.style.overflow = previousOverflow
      if (previouslyFocused instanceof HTMLElement && previouslyFocused.isConnected) {
        previouslyFocused.focus()
      }
    }
  }, [open])

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby={titleId}
      aria-describedby={description ? descriptionId : undefined}
      onCancel={(event) => {
        event.preventDefault()
        if (!closeDisabled) onClose()
      }}
      className={`fixed inset-0 m-auto max-h-[90dvh] w-[calc(100%-2rem)] ${modalSizes[size]} overflow-y-auto rounded-xl border-0 bg-white p-0 text-slate-700 shadow-xl backdrop:bg-slate-900/50`}
    >
      <header className="flex items-start justify-between gap-4 border-b border-slate-200 p-6">
        <div>
          <h2 id={titleId} className="text-xl font-semibold text-slate-900">{title}</h2>
          {description && <p id={descriptionId} className="mt-2 text-sm">{description}</p>}
        </div>
        <Button variant="secondary" onClick={onClose} disabled={closeDisabled} aria-label="Fechar modal">Fechar</Button>
      </header>
      <div className="p-6">{children}</div>
      {footer && <footer className="flex flex-wrap justify-end gap-3 border-t border-slate-200 p-6">{footer}</footer>}
    </dialog>
  )
}
