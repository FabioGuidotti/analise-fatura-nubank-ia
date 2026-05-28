// Componentes de UI reutilizáveis e leves.

export function Spinner({ large }) {
  return <span className={`spinner ${large ? 'spinner-lg' : ''}`} />
}

export function LoadingPage() {
  return (
    <div className="loading-page">
      <Spinner large />
    </div>
  )
}

export function Button({ variant = 'primary', loading, children, className = '', ...props }) {
  const cls = {
    primary: 'btn',
    secondary: 'btn btn-secondary',
    ghost: 'btn btn-ghost',
    danger: 'btn btn-danger',
  }[variant]
  return (
    <button className={`${cls} ${className}`} disabled={loading || props.disabled} {...props}>
      {loading && <Spinner />}
      {children}
    </button>
  )
}

export function Field({ label, error, hint, children }) {
  return (
    <div className="field">
      {label && <label>{label}</label>}
      {children}
      {error && <span className="field-error">{error}</span>}
      {hint && !error && <span className="field-hint">{hint}</span>}
    </div>
  )
}

export function Card({ children, className = '', ...props }) {
  return (
    <div className={`card ${className}`} {...props}>
      {children}
    </div>
  )
}

export function Metric({ label, value, sub }) {
  return (
    <Card className="metric">
      <span className="card-title">{label}</span>
      <span className="metric-value">{value}</span>
      {sub && <span className="metric-sub">{sub}</span>}
    </Card>
  )
}

export function Badge({ children, variant }) {
  return <span className={`badge ${variant ? `badge-${variant}` : ''}`}>{children}</span>
}

export function EmptyState({ icon = '📭', title, message, action }) {
  return (
    <div className="empty">
      <div className="empty-icon">{icon}</div>
      <h3>{title}</h3>
      {message && <p className="muted mt">{message}</p>}
      {action && <div className="mt">{action}</div>}
    </div>
  )
}

// Modal de confirmação — peça-chave do design "anti-burro": ações destrutivas
// sempre exigem confirmação explícita.
export function ConfirmDialog({ open, title, message, confirmLabel = 'Confirmar', danger, onConfirm, onCancel, loading }) {
  if (!open) return null
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>{title}</h3>
        <p className="muted mt">{message}</p>
        <div className="row" style={{ justifyContent: 'flex-end', marginTop: 24 }}>
          <Button variant="ghost" onClick={onCancel}>Cancelar</Button>
          <Button variant={danger ? 'danger' : 'primary'} onClick={onConfirm} loading={loading}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  )
}
