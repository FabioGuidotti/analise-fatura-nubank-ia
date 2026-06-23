import { useEffect, useRef, useState } from 'react'
import api, { errorMessage } from '../api/client'
import { Button, Card } from '../components/ui'

const SUGGESTIONS = [
  'Me dê um resumo dos meus gastos',
  'Onde posso economizar?',
  'Quais são meus maiores gastos?',
  'Como estão meus gastos por categoria?',
  'Quais padrões você identifica?',
]

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      content:
        'Olá! Sou seu assistente financeiro. Pergunte qualquer coisa sobre seus gastos — '
        + 'posso resumir, comparar categorias e sugerir economias. 💬',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const ask = async (question) => {
    const q = (question ?? input).trim()
    if (!q || loading) return
    setInput('')
    setMessages((m) => [...m, { role: 'user', content: q }])
    setLoading(true)
    try {
      const res = await api.post('/analysis/chat', { question: q })
      setMessages((m) => [...m, { role: 'ai', content: res.data.answer }])
    } catch (err) {
      setMessages((m) => [...m, { role: 'ai', content: errorMessage(err, 'Não consegui responder agora.') }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="page-head">
        <h1>🤖 Assistente IA</h1>
        <p>Converse sobre suas finanças em linguagem natural.</p>
      </div>

      <Card>
        <div className="chat-window">
          {messages.map((m, i) => (
            <div key={i} className={`bubble ${m.role === 'user' ? 'bubble-user' : 'bubble-ai'}`}>
              {m.content}
            </div>
          ))}
          {loading && (
            <div className="bubble bubble-ai row gap-sm">
              <span className="spinner" /> Pensando…
            </div>
          )}
          <div ref={endRef} />
        </div>

        <div className="row wrap gap-sm mt">
          {SUGGESTIONS.map((s) => (
            <button key={s} className="chip" onClick={() => ask(s)} disabled={loading}>{s}</button>
          ))}
        </div>

        <form
          className="row gap-sm mt"
          onSubmit={(e) => { e.preventDefault(); ask() }}
        >
          <input
            className="input grow"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite sua pergunta…"
            disabled={loading}
          />
          <Button type="submit" loading={loading} disabled={!input.trim()}>Enviar</Button>
        </form>
      </Card>
    </div>
  )
}
