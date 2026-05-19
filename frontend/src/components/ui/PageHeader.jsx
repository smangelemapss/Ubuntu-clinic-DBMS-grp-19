export function PageHeader({ title, subtitle, eyebrow, icon: Icon, action }) {
  return (
    <header className="page-hero-card">
      <div className="page-hero-card__body">
        {eyebrow && (
          <p className="page-hero-card__eyebrow">
            {Icon && <Icon size={13} strokeWidth={2.25} aria-hidden="true" />}
            {eyebrow}
          </p>
        )}
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="page-subtitle">{subtitle}</p>}
      </div>
      {action && <div className="page-hero-card__action">{action}</div>}
    </header>
  )
}

export default PageHeader
