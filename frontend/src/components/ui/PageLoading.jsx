import { Loader2 } from 'lucide-react'

export function PageLoading({ message = 'Loading...' }) {
  return (
    <div className="page-loading" role="status" aria-live="polite">
      <Loader2 className="spin-icon" size={28} strokeWidth={2} aria-hidden="true" />
      <span>{message}</span>
    </div>
  )
}

export default PageLoading
