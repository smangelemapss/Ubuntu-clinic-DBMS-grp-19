export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="empty-state empty-state--rich">
      {Icon && (
        <div className="empty-state__icon" aria-hidden="true">
          <Icon size={32} strokeWidth={1.75} />
        </div>
      )}
      {title && <h3 className="empty-state__title">{title}</h3>}
      {description && <p className="empty-state__text">{description}</p>}
      {action && <div className="empty-state__action">{action}</div>}
    </div>
  )
}

export default EmptyState
