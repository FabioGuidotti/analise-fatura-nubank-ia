import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import api, { errorMessage } from '../api/client'
import { Badge, Button, Card, ConfirmDialog, EmptyState, LoadingPage } from '../components/ui'
import { useToast } from '../context/ToastContext'
import { formatBRL, formatDate } from '../lib/format'

const EMPTY_FILTERS = { category: '', start: '', end: '', min_amount: '', source_file: '' }

export default function Transactions() {
  const toast = useToast()
  const [loading, setLoading] = useState(true)
  const [items, setItems] = useState([])
  const [categories, setCategories] = useState([])
  const [files, setFiles] = useState([])
  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const [editing, setEditing] = useState(null)
  const [deleting, setDeleting] = useState(null)
  const [busy, setBusy] = useState(false)

  const load = async () => {
    setLoading(true)
    const params = Object.fromEntries(
      Object.entries(filters).filter(([, v]) => v !== '')
    )
    try {
      const [tx, cats, fls] = await Promise.all([
        api.get('/transactions', { params }),
        api.get('/categories'),
        api.get('/transactions/source-files'),
      ])
      setItems(tx.data)
      setCategories(cats.data)
      setFiles(fls.data)
    } finally {
      setLoading(false)
    }
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { load() }, [filters])

  const total = useMemo(() => items.reduce((s, t) => s + t.amount, 0), [items])

  const saveEdit = async () => {
    setBusy(true)
    try {
      await api.put(`/transactions/${editing.id}`, {
        date: editing.date,
        description: editing.description,
        amount: Number(editing.amount),
        category: editing.category,
      })
      toast.success('Transação atualizada!')
      setEditing(null)
      load()
    } catch (err) {
      toast.error(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  const confirmDelete = async () => {
    setBusy(true)
    try {
      await api.delete(`/transactions/${deleting.id}`)
      toast.success('Transação excluída.')
      setDeleting(null)
      load()
    } catch (err) {
      toast.error(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  const exportCsv = () => {
    const header = 'Data,Descrição,Categoria,Valor\n'
    const rows = items
      .map((t) => `${t.date},"${t.description.replace(/"/g, '""')}",${t.category},${t.amount}`)
      .join('\n')
    const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `transacoes_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const set = (key) => (e) => setFilters((f) => ({ ...f, [key]: e.target.value }))

  return (
    <div>
      <div className="page-head row-between">
        <div>
          <h1>📋 Transações</h1>
          <p>{items.length} transações · {formatBRL(total)}</p>
        </div>
        <div className="row gap-sm">
          <Button variant="secondary" onClick={exportCsv} disabled={items.length === 0}>📥 Exportar CSV</Button>
          <Link to="/importar"><Button>📥 Importar</Button></Link>
        </div>
      </div>

      <Card style={{ marginBottom: 20 }}>
        <div className="grid grid-4">
          <div className="field" style={{ margin: 0 }}>
            <label>Categoria</label>
            <select className="select" value={filters.category} onChange={set('category')}>
              <option value="">Todas</option>
              {categories.map((c) => <option key={c.id} value={c.name}>{c.name}</option>)}
            </select>
          </div>
          <div className="field" style={{ margin: 0 }}>
            <label>De</label>
            <input className="input" type="date" value={filters.start} onChange={set('start')} />
          </div>
          <div className="field" style={{ margin: 0 }}>
            <label>Até</label>
            <input className="input" type="date" value={filters.end} onChange={set('end')} />
          </div>
          <div className="field" style={{ margin: 0 }}>
            <label>Valor mínimo</label>
            <input className="input" type="number" min="0" step="0.01" value={filters.min_amount} onChange={set('min_amount')} placeholder="R$ 0,00" />
          </div>
        </div>
        <div className="row-between mt">
          <div className="field" style={{ margin: 0, maxWidth: 300, width: '100%' }}>
            <label>Arquivo de origem</label>
            <select className="select" value={filters.source_file} onChange={set('source_file')}>
              <option value="">Todos</option>
              {files.map((f) => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>
          <Button variant="ghost" onClick={() => setFilters(EMPTY_FILTERS)}>Limpar filtros</Button>
        </div>
      </Card>

      {loading ? (
        <LoadingPage />
      ) : items.length === 0 ? (
        <Card>
          <EmptyState icon="📭" title="Nenhuma transação" message="Ajuste os filtros ou importe uma fatura." action={<Link to="/importar"><Button>Importar fatura</Button></Link>} />
        </Card>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Data</th>
                <th>Descrição</th>
                <th>Categoria</th>
                <th style={{ textAlign: 'right' }}>Valor</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map((t) => (
                <tr key={t.id}>
                  <td>{formatDate(t.date)}</td>
                  <td>{t.description}</td>
                  <td><Badge>{t.category}</Badge></td>
                  <td style={{ textAlign: 'right', fontWeight: 600 }}>{formatBRL(t.amount)}</td>
                  <td>
                    <div className="row gap-sm" style={{ justifyContent: 'flex-end' }}>
                      <button className="btn btn-ghost btn-sm" onClick={() => setEditing({ ...t })}>✏️</button>
                      <button className="btn btn-ghost btn-sm" onClick={() => setDeleting(t)}>🗑️</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal de edição */}
      {editing && (
        <div className="modal-overlay" onClick={() => setEditing(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Editar transação</h3>
            <div className="mt">
              <div className="field">
                <label>Data</label>
                <input className="input" type="date" value={editing.date} onChange={(e) => setEditing({ ...editing, date: e.target.value })} />
              </div>
              <div className="field">
                <label>Descrição</label>
                <input className="input" value={editing.description} onChange={(e) => setEditing({ ...editing, description: e.target.value })} />
              </div>
              <div className="field">
                <label>Categoria</label>
                <select className="select" value={editing.category} onChange={(e) => setEditing({ ...editing, category: e.target.value })}>
                  {categories.map((c) => <option key={c.id} value={c.name}>{c.name}</option>)}
                </select>
              </div>
              <div className="field">
                <label>Valor</label>
                <input className="input" type="number" step="0.01" value={editing.amount} onChange={(e) => setEditing({ ...editing, amount: e.target.value })} />
              </div>
            </div>
            <div className="row" style={{ justifyContent: 'flex-end', marginTop: 16 }}>
              <Button variant="ghost" onClick={() => setEditing(null)}>Cancelar</Button>
              <Button onClick={saveEdit} loading={busy}>Salvar</Button>
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={!!deleting}
        title="Excluir transação?"
        message={deleting ? `"${deleting.description}" (${formatBRL(deleting.amount)}) será removida permanentemente.` : ''}
        confirmLabel="Excluir"
        danger
        loading={busy}
        onConfirm={confirmDelete}
        onCancel={() => setDeleting(null)}
      />
    </div>
  )
}
