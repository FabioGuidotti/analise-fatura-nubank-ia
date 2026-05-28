import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { errorMessage } from '../api/client'
import { Button, Field } from '../components/ui'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (user) return <Navigate to="/" replace />

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/')
    } catch (err) {
      setError(errorMessage(err, 'Não foi possível entrar.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrap">
      <form className="auth-card" onSubmit={submit}>
        <div className="auth-logo">💸</div>
        <h1 className="center">Bem-vindo de volta</h1>
        <p className="center muted" style={{ marginBottom: 24 }}>
          Entre para acompanhar suas finanças
        </p>

        {error && (
          <div className="rec rec-critical" style={{ marginBottom: 16 }}>
            <span className="rec-icon">⚠️</span>
            <p>{error}</p>
          </div>
        )}

        <Field label="E-mail">
          <input
            className="input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="voce@email.com"
            required
            autoComplete="email"
          />
        </Field>
        <Field label="Senha">
          <input
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            autoComplete="current-password"
          />
        </Field>

        <Button type="submit" className="btn-block" loading={loading}>
          Entrar
        </Button>

        <p className="center muted mt-lg">
          Não tem uma conta? <Link to="/registro" style={{ color: 'var(--brand-300)' }}>Criar conta</Link>
        </p>
      </form>
    </div>
  )
}
