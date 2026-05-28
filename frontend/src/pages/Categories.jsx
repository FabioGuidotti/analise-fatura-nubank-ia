import { useEffect, useState } from 'react'
import api, { errorMessage } from '../api/client'
import { Button, Card, ConfirmDialog, LoadingPage } from '../components/ui'
import { useToast } from '../context/ToastContext'

const EMOJIS = ['🍽️', '🛒', '🚗', '🏠', '💊', '🎬', '🛍️', '📚', '🔧', '💰', '✈️', '🎮', '🐾', '🏷️']
const PALETTE = ['#8b5cf6', '#06b6d4', '#f59e0b', '#22c55e', '#ef4444', '#ec4899', '#3b82f6', '#64748b']

const BLANK = { name: '', icon: '🏷️', color: '#8b5cf6', examples: '' }

export default function Categories() {
  const toast = useToast()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(null) // objeto (com id) ou BLANK (novo)
  const [deleting, setDeleting] = useState(null)
  const [busy, setBusy] = useState(false)

  const load = () => {
    setLoading(true)
    api.get('/categories').then((res) => setItems(res.data)).finally(() => setLoading(false))
  }
  useEffect(load, [])

  const save = async () => {
    if (!editing.name.trim()) {
      toast.error('Informe o nome da categoria.')
      return
    }
    setBusy(true)
    try {
      const payload = {
        name: editing.name.trim(),
        icon: editing.icon,
        color: editing.color,
        examples: editing.examples,
      }
      if (editing.id) await api.put(`/categories/${editing.id}`, payload)
      else await api.post('/categories', payload)
      toast.success('Categoria salva!')
      setEditing(null)
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
      await api.delete(`/categories/${deleting.id}`)
      toast.success('Categoria excluída.')
      setDeleting(null)
      load()
    } catch (err) {
      toast.error(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  if (loading) return <LoadingPage />

  return (
    <div>
      <div className="page-head row-between">
        <div>
          <h1>🏷️ Categorias</h1>
          <p>Personalize categorias e dê exemplos para a IA classificar melhor.</p>
        </div>
        <Button onClick={() => setEditing({ ...BLANK })}>+ Nova categoria</Button>
      </div>

      <div className="grid grid-3">
        {items.map((c) => (
          <Card key={c.id}>
            <div className="row-between">
              <div className="row gap-sm">
                <div style={{ width: 40, height: 40, borderRadius: 12, background: c.color, display: 'grid', placeItems: 'center', fontSize: '1.3rem' }}>
                  {c.icon}
                </div>
                <strong>{c.name}</strong>
              </div>
              <div className="row gap-sm">
                <button className="btn btn-ghost btn-sm" onClick={() => setEditing({ ...c })}>✏️</button>
                <button className="btn btn-ghost btn-sm" onClick={() => setDeleting(c)}>🗑️</button>
              </div>
            </div>
            {c.examples && <p className="faint mt" style={{ fontSize: '0.82rem' }}>Ex.: {c.examples}</p>}
          </Card>
        ))}
      </div>

      {editing && (
        <div className="modal-overlay" onClick={() => setEditing(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>{editing.id ? 'Editar categoria' : 'Nova categoria'}</h3>
            <div className="mt">
              <div className="field">
                <label>Nome</label>
                <input className="input" value={editing.name} onChange={(e) => setEditing({ ...editing, name: e.target.value })} placeholder="Ex.: Alimentação" />
              </div>
              <div className="field">
                <label>Ícone</label>
                <div className="row wrap gap-sm">
                  {EMOJIS.map((e) => (
                    <button key={e} type="button" className="chip" style={{ borderColor: editing.icon === e ? 'var(--brand-500)' : undefined }} onClick={() => setEditing({ ...editing, icon: e })}>{e}</button>
                  ))}
                </div>
              </div>
              <div className="field">
                <label>Cor</label>
                <div className="row wrap gap-sm">
                  {PALETTE.map((color) => (
                    <button key={color} type="button" onClick={() => setEditing({ ...editing, color })} style={{ width: 28, height: 28, borderRadius: 8, background: color, border: editing.color === color ? '3px solid var(--text)' : '1px solid var(--border)', cursor: 'pointer' }} />
                  ))}
                </div>
              </div>
              <div className="field">
                <label>Exemplos (ajudam a IA)</label>
                <textarea className="input" rows={2} value={editing.examples || ''} onChange={(e) => setEditing({ ...editing, examples: e.target.value })} placeholder="Supermercado, Padaria, iFood…" />
              </div>
            </div>
            <div className="row" style={{ justifyContent: 'flex-end', marginTop: 8 }}>
              <Button variant="ghost" onClick={() => setEditing(null)}>Cancelar</Button>
              <Button onClick={save} loading={busy}>Salvar</Button>
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={!!deleting}
        title="Excluir categoria?"
        message={deleting ? `A categoria "${deleting.name}" será removida. As transações não serão apagadas.` : ''}
        confirmLabel="Excluir"
        danger
        loading={busy}
        onConfirm={remove}
        onCancel={() => setDeleting(null)}
      />
    </div>
  )
}
