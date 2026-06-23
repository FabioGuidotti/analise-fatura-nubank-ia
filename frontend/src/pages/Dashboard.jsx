import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import { Button, Card, EmptyState, LoadingPage, Metric } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { formatBRL, formatPercent } from '../lib/format'

export default function Dashboard() {
  const { user } = useAuth()
  const [analysis, setAnalysis] = useState(null)
  const [budgets, setBudgets] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.get('/analysis'), api.get('/budgets/status')])
      .then(([a, b]) => {
        setAnalysis(a.data)
        setBudgets(b.data)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingPage />

  const s = analysis?.summary
  const hasData = s && s.transaction_count > 0

  return (
    <div>
      <div className="page-head">
        <h1>Olá, {user?.name?.split(' ')[0]} 👋</h1>
        <p>Aqui está o panorama das suas finanças.</p>
      </div>

      {!hasData ? (
        <Card>
          <EmptyState
            icon="🚀"
            title="Vamos começar!"
            message="Importe sua primeira fatura do Nubank em PDF para desbloquear análises, recomendações e o assistente de IA."
            action={
              <Link to="/importar">
                <Button>📥 Importar minha primeira fatura</Button>
              </Link>
            }
          />
        </Card>
      ) : (
        <>
          <div className="grid grid-4">
            <Metric label="Total gasto" value={formatBRL(s.total_spent)} sub={`${s.transaction_count} transações`} />
            <Metric label="Ticket médio" value={formatBRL(s.average_transaction)} sub="por transação" />
            <Metric label="Maior gasto" value={formatBRL(s.largest_transaction)} />
            <Metric label="Média diária" value={formatBRL(s.daily_average)} sub="no período" />
          </div>

          <div className="grid grid-2 mt-lg">
            <Card>
              <div className="row-between">
                <h2>💡 Recomendações</h2>
                <Link to="/analise" className="muted" style={{ fontSize: '0.85rem' }}>Ver análise →</Link>
              </div>
              <div className="col mt">
                {analysis.recommendations.slice(0, 4).map((r, i) => (
                  <div key={i} className={`rec rec-${r.severity}`}>
                    <span className="rec-icon">{r.icon}</span>
                    <div>
                      <h4>{r.title}</h4>
                      <p>{r.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <div className="row-between">
                <h2>🎯 Orçamentos do mês</h2>
                <Link to="/orcamentos" className="muted" style={{ fontSize: '0.85rem' }}>Gerenciar →</Link>
              </div>
              {budgets.length === 0 ? (
                <EmptyState
                  icon="🎯"
                  title="Sem orçamentos definidos"
                  message="Defina limites mensais por categoria para receber alertas."
                  action={<Link to="/orcamentos"><Button variant="secondary">Definir orçamentos</Button></Link>}
                />
              ) : (
                <div className="col mt">
                  {budgets.map((b) => (
                    <div key={b.category} className="col gap-sm">
                      <div className="row-between">
                        <strong style={{ fontSize: '0.9rem' }}>{b.category}</strong>
                        <span className={b.status === 'exceeded' ? 'text-danger' : b.status === 'warning' ? 'text-warning' : 'muted'} style={{ fontSize: '0.85rem' }}>
                          {formatBRL(b.spent)} / {formatBRL(b.monthly_limit)} ({formatPercent(b.percentage)})
                        </span>
                      </div>
                      <div className="progress">
                        <div
                          className="progress-bar"
                          style={{
                            width: `${Math.min(b.percentage, 100)}%`,
                            background: b.status === 'exceeded' ? 'var(--danger)' : b.status === 'warning' ? 'var(--warning)' : undefined,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>

          <Card className="mt-lg">
            <h2>🏷️ Top categorias</h2>
            <div className="col mt">
              {analysis.by_category.slice(0, 5).map((c) => (
                <div key={c.category} className="row-between">
                  <span>{c.category}</span>
                  <div className="row gap-sm" style={{ flex: 1, maxWidth: 420 }}>
                    <div className="progress grow">
                      <div className="progress-bar" style={{ width: `${c.percentage}%` }} />
                    </div>
                    <span className="muted" style={{ fontSize: '0.85rem', minWidth: 130, textAlign: 'right' }}>
                      {formatBRL(c.total)} ({formatPercent(c.percentage)})
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  )
}
