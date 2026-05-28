// Utilitários de formatação (pt-BR) — centralizados para consistência.

export const formatBRL = (value) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(
    Number(value || 0)
  )

export const formatDate = (value) => {
  if (!value) return ''
  const d = typeof value === 'string' ? new Date(value + 'T00:00:00') : value
  return new Intl.DateTimeFormat('pt-BR').format(d)
}

export const formatPercent = (value) => `${Number(value || 0).toFixed(1)}%`

// Iniciais para o avatar.
export const initials = (name = '') =>
  name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((n) => n[0]?.toUpperCase())
    .join('')
