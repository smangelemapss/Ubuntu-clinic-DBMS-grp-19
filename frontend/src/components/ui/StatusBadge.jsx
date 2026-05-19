const STATUS_MAP = {
  confirmed: 'success',
  pending: 'warning',
  cancelled: 'danger',
  completed: 'info',
}

export function StatusBadge({ status }) {
  const variant = STATUS_MAP[status?.toLowerCase()] || 'neutral'
  return (
    <span className={`badge badge--${variant}`}>
      {status}
    </span>
  )
}

export default StatusBadge
