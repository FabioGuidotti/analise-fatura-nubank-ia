import { useMemo, useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { errorMessage } from '../api/client'
import { Button, Field } from '../components/ui'
import { useAuth } from '../context/AuthContext'

// Regras de senha espelham a política do backend, com feedback visual.
const rules = [
  { label: 'Ao menos 8 caracteres', test: (v) => v.length >= 8 },
  { label: 'Uma letra maiúscula', test: (v) => /[A-Z]/.test(v) },
  { label: 'Uma letra minúscula', test: (v) => /[a-z]/.test(v) },
  { label: 'Um número', test: (v) => /\d/.test(v) },
]

export default function Register() {
  const { user, register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const passwordChecks = useMemo(
    () => rules.map((r) => ({ ...r, ok: r.test(form.password) })),
    [form.password]
  )
  const passwordValid = passwordChecks.every((c) => c.ok)
  const passwordsMatch = form.password && form.password === form.confirm
  const canSubmit = form.name.trim().length >= 2 && form.email && passwordValid && passwordsMatch

  if (user) return <Navigate to="/" replace />

  const update = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    if (!canSubmit) return
    setError('')
    setLoading(true)
    try {
      await register(form.name.trim(), form.email, form.password)
      navigate('/')
    } catch (err) {
      setError(errorMessage(err, 'Não foi possível criar a conta.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrap">
      <form className="auth-card" onSubmit={submit}>
        <div className="auth-logo">💸</div>
        <h1 className="center">Criar conta</h1>
        <p className="center muted" style={{ marginBottom: 24 }}>
          Comece a organizar suas finanças hoje
        </p>

        {error && (
          <div className="rec rec-critical" style={{ marginBottom: 16 }}>
            <span className="rec-icon">⚠️</span>
            <p>{error}</p>
          </div>
        )}

        <Field label="Nome">
          <input className="input" value={form.name} onChange={update('name')} placeholder="Seu nome" required />
        </Field>
        <Field label="E-mail">
          <input className="input" type="email" value={form.email} onChange={update('email')} placeholder="voce@email.com" required autoComplete="email" />
        </Field>
        <Field label="Senha">
          <input className="input" type="password" value={form.password} onChange={update('password')} placeholder="••••••••" required autoComplete="new-password" />
        </Field>

        {form.password && (
          <div className="col gap-sm" style={{ marginBottom: 16 }}>
            {passwordChecks.map((c) => (
              <span key={c.label} className={c.ok ? 'text-success' : 'faint'} style={{ fontSize: '0.8rem' }}>
                {c.ok ? '✓' : '○'} {c.label}
              </span>
            ))}
          </div>
        )}

        <Field
          label="Confirmar senha"
          error={form.confirm && !passwordsMatch ? 'As senhas não coincidem' : ''}
        >
          <input className="input" type="password" value={form.confirm} onChange={update('confirm')} placeholder="••••••••" required autoComplete="new-password" />
        </Field>

        <Button type="submit" className="btn-block" loading={loading} disabled={!canSubmit}>
          Criar conta
        </Button>

        <p className="center muted mt-lg">
          Já tem conta? <Link to="/login" style={{ color: 'var(--brand-300)' }}>Entrar</Link>
        </p>
      </form>
    </div>
  )
}
