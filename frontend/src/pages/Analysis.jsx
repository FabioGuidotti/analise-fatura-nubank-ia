import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart,
  Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import api from '../api/client'
import { Button, Card, EmptyState, LoadingPage, Metric } from '../components/ui'
import { formatBRL } from '../lib/format'

const COLORS = ['#8b5cf6', '#06b6d4', '#f59e0b', '#22c55e', '#ef4444', '#ec4899', '#3b82f6', '#64748b', '#10b981', '#a855f7']

const tooltipStyle = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 10,
  color: 'var(--text)',
}

export default function Analysis() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/analysis').then((res) => setData(res.data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingPage />

  const s = data?.summary
  if (!s || s.transaction_count === 0) {
    return (
      <Card>
        <EmptyState icon="📊" title="Sem dados para analisar" message="Importe uma fatura para ver gráficos e recomendações." action={<Link to="/importar"><Button>Importar fatura</Button></Link>} />
      </Card>
    )
  }

  return (
    <div>
      <div className="page-head">
        <h1>📊 Análise Financeira</h1>
        <p>Insights detalhados sobre seus padrões de gasto.</p>
      </div>

      <div className="grid grid-4">
        <Metric label="Total" value={formatBRL(s.total_spent)} sub={`${s.transaction_count} transações`} />
        <Metric label="Ticket médio" value={formatBRL(s.average_transaction)} />
        <Metric label="Maior gasto" value={formatBRL(s.largest_transaction)} />
        <Metric label="Período" value={`${s.period_start?.slice(5)} → ${s.period_end?.slice(5)}`} sub={`Média ${formatBRL(s.daily_average)}/dia`} />
      </div>

      {/* Recomendações */}
      <Card className="mt-lg">
        <h2>💡 Recomendações personalizadas</h2>
        <div className="grid grid-2 mt">
          {data.recommendations.map((r, i) => (
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

      <div className="grid grid-2 mt-lg">
        <Card>
          <h2>Gastos por categoria</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={data.by_category} dataKey="total" nameKey="category" cx="50%" cy="50%" outerRadius={100} innerRadius={55}>
                {data.by_category.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} formatter={(v) => formatBRL(v)} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h2>Evolução mensal</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.by_month}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="period" stroke="var(--text-muted)" fontSize={12} />
              <YAxis stroke="var(--text-muted)" fontSize={12} />
              <Tooltip contentStyle={tooltipStyle} formatter={(v) => formatBRL(v)} />
              <Line type="monotone" dataKey="total" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h2>Gastos por dia da semana</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.by_weekday}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="period" stroke="var(--text-muted)" fontSize={11} />
              <YAxis stroke="var(--text-muted)" fontSize={12} />
              <Tooltip contentStyle={tooltipStyle} formatter={(v) => formatBRL(v)} cursor={{ fill: 'var(--surface-2)' }} />
              <Bar dataKey="total" fill="#06b6d4" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h2>Maiores estabelecimentos</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.top_merchants.slice(0, 8)} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis type="number" stroke="var(--text-muted)" fontSize={12} />
              <YAxis type="category" dataKey="description" width={120} stroke="var(--text-muted)" fontSize={11} />
              <Tooltip contentStyle={tooltipStyle} formatter={(v) => formatBRL(v)} cursor={{ fill: 'var(--surface-2)' }} />
              <Bar dataKey="total" fill="#f59e0b" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {data.recurring.length > 0 && (
        <Card className="mt-lg">
          <h2>🔁 Gastos recorrentes detectados</h2>
          <div className="table-wrap mt">
            <table>
              <thead>
                <tr>
                  <th>Estabelecimento</th>
                  <th style={{ textAlign: 'center' }}>Ocorrências</th>
                  <th style={{ textAlign: 'right' }}>Valor médio</th>
                  <th style={{ textAlign: 'right' }}>Estimado/mês</th>
                </tr>
              </thead>
              <tbody>
                {data.recurring.map((r, i) => (
                  <tr key={i}>
                    <td>{r.description}</td>
                    <td style={{ textAlign: 'center' }}>{r.occurrences}x</td>
                    <td style={{ textAlign: 'right' }}>{formatBRL(r.average_amount)}</td>
                    <td style={{ textAlign: 'right', fontWeight: 600 }}>{formatBRL(r.estimated_monthly)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}
