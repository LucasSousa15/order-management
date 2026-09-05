import { useEffect, useState } from 'react'
import { axiosInstance } from '../http/api'

export function ApiStatus() {
  const [status, setStatus] = useState('Verificando conexão...')

  useEffect(() => {
    const controller = new AbortController()

    async function checkConnection() {
      try {
        await axiosInstance.get<{ message: string }>('/consume-status', {
          signal: controller.signal,
        })
        setStatus('Serviço disponível')
      } catch {
        if (!controller.signal.aborted) {
          setStatus('Não foi possível conectar ao serviço.')
        }
      }
    }

    void checkConnection()
    return () => controller.abort()
  }, [])

  return <p role="status" className="text-sm text-slate-600">{status}</p>
}
