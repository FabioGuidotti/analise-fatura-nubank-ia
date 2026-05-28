import { useEffect, useState } from 'react'
import api, { errorMessage } from '../api/client'
import { Button, Card, ConfirmDialog, EmptyState, LoadingPage } from '../components/ui'
import { useToast } from '../context/ToastContext'
import { formatBRL, formatPercent } from '../lib/format'

export default function Budgets() {
  const toast = useToast()
  const [status, setStatus] = useState([])
  const [categories, setCategories] = useState([])
  const [budgets, setBudgets] = useState([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ category: '', monthly_limit: '' })
  const [deleting, setDeleting] = useState(null)
  const [busy, setBusy] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const [st, cats, bs] = await Promise.all([
        api.get('/budgets/status'),
        api.get('/categories'),
        api.get('/budgets'),
      ])
      setStatus(st.data)
      setCategories(cats.data)
      setBudgets(bs.data)
    } finally {
      setLoading(false)
    }
  }
  useEffect(() => { load() }, [])

  const save = async () => {
    if (!form.category || !form.monthly_limit || Number(form.monthly_limit) <= 0) {
      toast.error('Escolha a categoria e um valor maior que zero.')
      return
    }
    setBusy(true)
    try {
      await api.put('/budgets', { category: form.category, monthly_limit: Number(form.monthly_limit) })
      toast.success('Orçamento salvo!')
      setForm({ category: '', monthly_limit: '' })
      load()
    } catch (err) {
      toast.error(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  const remove = async () => {
    setBusy(true)
    try {
      await api.delete(`/budgets/${deleting.id}`)
      toast.success('Orçamento removido.')
      setDeleting(null)
      load()
    } catch (err) {
      toast.error(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  if (loading) return <LoadingPage />

  const statusColor = (s) => (s === 'exceeded' ? 'var(--danger)' : s === 'warning' ? 'var(--warning)' : undefined)

  return (
    <div>
      <div className="page-head">
        <h1>🎯 Orçamentos</h1>
        <p>Defina limites mensais por categoria e receba alertas automáticos ao se aproximar deles.</p>
      </div>

      <Card style={{ marginBottom: 20 }}>
        <h2>Definir orçamento</h2>
        <div className="row wrap gap-lg mt" style={{ alignItems: 'flex-end' }}>
          <div className="field" style={{ margin: 0, minWidth: 220 }}>
            <label>Categoria</label>
            <select className="select" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              <option value="">Selecione…</option>
              {categories.map((c) => <option key={c.id} value={c.name}>{c.icon} {c.name}</option>)}
            </select>
          </div>
          <div className="field" style={{ margin: 0, minWidth: 180 }}>
            <label>Limite mensal (R$)</label>
            <input className="input" type="number" min="0" step="0.01" value={form.monthly_limit} onChange={(e) => setForm({ ...form, monthly_limit: e.target.value })} placeholder="1000,00" />
          </div>
          <Button onClick={save} loading={busy}>Salvar orçamento</Button>
        </div>
      </Card>

      {status.length === 0 ? (
        <Card>
          <EmptyState icon="🎯" title="Nenhum orçamento definido" message="Crie seu primeiro orçamento acima para começar a acompanhar seus limites." />
        </Card>
      ) : (
        <div className="grid grid-2">
          {status.map((b) => {
            const budgetRow = budgets.find((x) => x.category === b.category)
            return (
              <Card key={b.category}>
                <div className="row-between">
                  <strong>{b.category}</strong>
                  <div className="row gap-sm">
                    <span style={{ color: statusColor(b.status) }}>{formatPercent(b.percentage)}</span>
                    {budgetRow && (
                      <button className="btn btn-ghost btn-sm" onClick={() => setDeleting(budgetRow)}>🗑️</button>
                    )}
                  </div>
                </div>
                <div className="progress mt">
                  <div className="progress-bar" style={{ width: `${Math.min(b.percentage, 100)}%`, background: statusColor(b.status) }} />
                </div>
                <div className="row-between mt">
                  <span className="muted" style={{ fontSize: '0.85rem' }}>Gasto: {formatBRL(b.spent)}</span>
                  <span className="muted" style={{ fontSize: '0.85rem' }}>
                    {b.remaining >= 0 ? `Resta ${formatBRL(b.remaining)}` : `Excedeu ${formatBRL(-b.remaining)}`}
                  </span>
                </div>
              </Card>
            )
          })}
        </div>
      )}

      <ConfirmDialog
        open={!!deleting}
        title="Remover orçamento?"
        message={deleting ? `O orçamento de "${deleting.category}" será removido.` : ''}
        confirmLabel="Remover"
        danger
        loading={busy}
        onConfirm={remove}
        onCancel={() => setDeleting(null)}
      />
    </div>
  )
}
