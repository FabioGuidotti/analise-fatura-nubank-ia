import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { errorMessage } from '../api/client'
import { Badge, Button, Card, EmptyState } from '../components/ui'
import { useToast } from '../context/ToastContext'
import { formatBRL, formatDate } from '../lib/format'

export default function Import() {
  const toast = useToast()
  const navigate = useNavigate()
  const inputRef = useRef(null)
  const [drag, setDrag] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [preview, setPreview] = useState(null)
  // Controla quais itens serão salvos (duplicatas começam desmarcadas).
  const [selected, setSelected] = useState({})

  const handleFile = async (file) => {
    if (!file) return
    if (file.type !== 'application/pdf') {
      toast.error('Envie um arquivo PDF.')
      return
    }
    setUploading(true)
    setPreview(null)
    const data = new FormData()
    data.append('file', file)
    try {
      const res = await api.post('/invoices/preview', data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setPreview(res.data)
      // Marca todos exceto duplicatas por padrão.
      const initial = {}
      res.data.items.forEach((it, i) => (initial[i] = !it.duplicate))
      setSelected(initial)
      toast.success(`${res.data.items.length} transações encontradas!`)
    } catch (err) {
      toast.error(errorMessage(err, 'Não foi possível ler a fatura.'))
    } finally {
      setUploading(false)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDrag(false)
    handleFile(e.dataTransfer.files?.[0])
  }

  const toggle = (i) => setSelected((s) => ({ ...s, [i]: !s[i] }))
  const selectedItems = preview?.items.filter((_, i) => selected[i]) || []
  const selectedTotal = selectedItems.reduce((sum, it) => sum + it.amount, 0)

  const confirm = async () => {
    if (selectedItems.length === 0) {
      toast.error('Selecione ao menos uma transação.')
      return
    }
    setSaving(true)
    try {
      const payload = selectedItems.map((it) => ({
        date: it.date,
        description: it.description,
        amount: it.amount,
        category: it.category,
        source_file: preview.source_file,
      }))
      await api.post('/transactions', payload)
      toast.success(`${payload.length} transações salvas!`)
      navigate('/transacoes')
    } catch (err) {
      toast.error(errorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <div className="page-head">
        <h1>📥 Importar Fatura</h1>
        <p>Envie o PDF da sua fatura do Nubank. Nada é salvo até você revisar e confirmar.</p>
      </div>

      {!preview && (
        <Card>
          <div
            className={`dropzone ${drag ? 'drag' : ''}`}
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDrag(true) }}
            onDragLeave={() => setDrag(false)}
            onDrop={onDrop}
          >
            <input
              ref={inputRef}
              type="file"
              accept="application/pdf"
              hidden
              onChange={(e) => handleFile(e.target.files?.[0])}
            />
            {uploading ? (
              <div className="col" style={{ alignItems: 'center' }}>
                <span className="spinner spinner-lg" />
                <p className="muted mt">Lendo e analisando a fatura…</p>
              </div>
            ) : (
              <>
                <div className="empty-icon">📄</div>
                <h3>Arraste o PDF aqui ou clique para selecionar</h3>
                <p className="muted mt">Apenas arquivos PDF do Nubank · máx. 10 MB</p>
              </>
            )}
          </div>
        </Card>
      )}

      {preview && (
        <>
          <div className="grid grid-3" style={{ marginBottom: 20 }}>
            <Card className="metric">
              <span className="card-title">Transações</span>
              <span className="metric-value">{preview.items.length}</span>
            </Card>
            <Card className="metric">
              <span className="card-title">Selecionado</span>
              <span className="metric-value">{formatBRL(selectedTotal)}</span>
              <span className="metric-sub">{selectedItems.length} itens</span>
            </Card>
            <Card className="metric">
              <span className="card-title">Possíveis duplicatas</span>
              <span className="metric-value text-warning">{preview.duplicates}</span>
              <span className="metric-sub">desmarcadas automaticamente</span>
            </Card>
          </div>

          <Card>
            <div className="row-between" style={{ marginBottom: 14 }}>
              <h2>Revisar transações</h2>
              <div className="row gap-sm">
                <Button variant="ghost" onClick={() => { setPreview(null); setSelected({}) }}>
                  Cancelar
                </Button>
                <Button onClick={confirm} loading={saving}>
                  ✅ Salvar {selectedItems.length} transações
                </Button>
              </div>
            </div>

            {preview.items.length === 0 ? (
              <EmptyState icon="🔍" title="Nenhuma transação encontrada" />
            ) : (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th></th>
                      <th>Data</th>
                      <th>Descrição</th>
                      <th>Categoria</th>
                      <th style={{ textAlign: 'right' }}>Valor</th>
                    </tr>
                  </thead>
                  <tbody>
                    {preview.items.map((it, i) => (
                      <tr key={i} style={{ opacity: selected[i] ? 1 : 0.5 }}>
                        <td>
                          <input type="checkbox" checked={!!selected[i]} onChange={() => toggle(i)} />
                        </td>
                        <td>{formatDate(it.date)}</td>
                        <td>
                          {it.description}{' '}
                          {it.duplicate && <Badge variant="warning">duplicata</Badge>}
                        </td>
                        <td><Badge>{it.category}</Badge></td>
                        <td style={{ textAlign: 'right' }}>{formatBRL(it.amount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  )
}
