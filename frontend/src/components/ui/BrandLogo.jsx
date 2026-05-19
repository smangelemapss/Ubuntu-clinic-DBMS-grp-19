import { Activity } from 'lucide-react'
import { APP_NAME, APP_TAGLINE } from '../../constants/brand'

export function BrandLogo({ size = 'md', showTagline = true, className = '' }) {
  const sizes = {
    sm: { box: 36, icon: 18, title: '0.95rem', tag: '0.625rem' },
    md: { box: 44, icon: 22, title: '1.125rem', tag: '0.6875rem' },
    lg: { box: 56, icon: 28, title: '1.5rem', tag: '0.75rem' },
  }
  const s = sizes[size] || sizes.md

  return (
    <div className={`brand-logo ${className}`}>
      <div
        className="brand-logo__icon"
        style={{ width: s.box, height: s.box }}
        aria-hidden="true"
      >
        <Activity size={s.icon} strokeWidth={2.25} />
      </div>
      <div className="brand-logo__text">
        <span className="brand-logo__name" style={{ fontSize: s.title }}>
          {APP_NAME}
        </span>
        {showTagline && (
          <span className="brand-logo__tagline" style={{ fontSize: s.tag }}>
            {APP_TAGLINE}
          </span>
        )}
      </div>
    </div>
  )
}

export default BrandLogo
