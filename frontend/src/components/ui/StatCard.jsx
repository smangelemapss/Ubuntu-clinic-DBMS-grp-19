export function StatCard({ icon: Icon, value, label, tone = 'teal' }) {
  return (
    <article className={`stat-card stat-card--${tone}`}>
      {Icon && (
        <div className="stat-card__icon-wrap" aria-hidden="true">
          <Icon size={22} strokeWidth={2} />
        </div>
      )}
      <p className="stat-card__value">{value}</p>
      <p className="stat-card__label">{label}</p>
    </article>
  )
}

export default StatCard
