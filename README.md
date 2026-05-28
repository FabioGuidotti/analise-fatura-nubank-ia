# 💸 Finança Fácil

Gestão financeira pessoal inteligente a partir das suas faturas do **Nubank**.
Importe o PDF, deixe a IA categorizar os gastos e receba **análises completas**,
**recomendações automáticas** e um **assistente financeiro** — tudo com foco em
usabilidade e simplicidade.

> **Refatoração 2.0** — o projeto foi totalmente reescrito de um app Streamlit
> monolítico para uma arquitetura moderna: **API FastAPI** + **SPA React**.

---

## ✨ Funcionalidades

- 🔐 **Login seguro** — bcrypt, política de senha forte, JWT (access + refresh),
  rate limiting por IP e bloqueio temporário após tentativas falhas.
- 📥 **Importação inteligente de faturas** — extração via IA (OpenAI) com
  fallback heurístico que funciona **sem chave de API**. Preview obrigatório com
  **detecção de duplicatas** antes de salvar (fluxo "anti-erro").
- 📊 **Análise financeira completa** — resumo, gastos por categoria, evolução
  mensal, por dia da semana, maiores estabelecimentos e detecção de gastos
  recorrentes (assinaturas).
- 💡 **Motor de recomendações** — alertas acionáveis (concentração de gastos,
  tendência de alta, estouro de orçamento, oportunidades de economia), 100%
  offline.
- 🎯 **Orçamentos por categoria** — limites mensais com barras de progresso e
  alertas automáticos.
- 🏷️ **Categorias personalizáveis** — com ícone, cor e exemplos que melhoram a
  classificação automática. Novos usuários já começam com categorias padrão.
- 🤖 **Assistente IA** — chat em linguagem natural sobre seus dados.
- 🎨 **Design de alta qualidade** — interface responsiva, tema claro/escuro,
  feedback visual (toasts) e confirmações para ações destrutivas.

---

## 🏗️ Arquitetura

```
analise-fatura-nubank-ia/
├── backend/                 # API FastAPI
│   └── app/
│       ├── core/            # config, database, security (JWT/bcrypt)
│       ├── models/          # ORM SQLAlchemy (User, Category, Transaction, Budget)
│       ├── schemas/         # Pydantic (validação, política de senha)
│       ├── services/        # pdf, ai, análise, recomendações
│       └── api/routes/      # auth, transactions, categories, invoices, analysis, budgets
├── frontend/                # SPA React + Vite
│   └── src/
│       ├── pages/           # Login, Dashboard, Import, Transações, Análise, etc.
│       ├── components/      # Layout, UI reutilizável
│       ├── context/         # Auth e Toasts
│       └── api/             # cliente axios com refresh automático
└── docker-compose.yml       # Postgres + backend + frontend (nginx)
```

**Stack:** FastAPI · SQLAlchemy 2 · Pydantic v2 · python-jose · React 18 · Vite ·
React Router · Recharts · OpenAI · PostgreSQL/SQLite.

---

## 🚀 Como rodar

### Opção 1 — Docker (recomendado)

```bash
cp .env.example .env
# Gere um SECRET_KEY forte:
python -c "import secrets; print(secrets.token_urlsafe(48))"
# Cole o valor em SECRET_KEY no .env e ajuste a senha do Postgres.

docker compose up --build
```

Acesse **http://localhost:8080**.

### Opção 2 — Desenvolvimento local

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # opcional: SQLite é o padrão
uvicorn app.main:app --reload # http://localhost:8000  (docs em /docs)
```

**Frontend** (em outro terminal)
```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173
```

O Vite faz proxy de `/api` para o backend em `http://localhost:8000`.

---

## 🔑 Configuração

| Variável | Onde | Descrição |
|---|---|---|
| `SECRET_KEY` | backend | **Obrigatória em produção.** Chave de assinatura dos JWT. |
| `DATABASE_URL` | backend | SQLite (padrão) ou `postgresql+psycopg://...`. |
| `OPENAI_API_KEY` | backend | Opcional. Sem ela, usa-se o extrator heurístico e o chat fica desativado. |
| `CORS_ORIGINS` | backend | Origens do frontend permitidas (separadas por vírgula). |
| `APP_PORT` | compose | Porta pública do frontend (padrão 8080). |

---

## 🔒 Segurança

- Senhas com **bcrypt** (nunca em texto puro).
- **Política de senha forte** validada no servidor e refletida na UI em tempo real.
- **JWT** de acesso curto (30 min) + **refresh token** (7 dias) com renovação
  automática e transparente no frontend.
- **Rate limiting** e **bloqueio temporário de conta** contra força bruta.
- Mensagens de erro genéricas no login (não revelam se o e-mail existe).
- Todos os dados são **isolados por usuário** em cada consulta.

> Sem a chave da OpenAI, a importação ainda funciona via extrator heurístico
> (regex para o layout do Nubank) — degradação graciosa, nunca quebra.

---

## 📄 Licença

MIT — veja [LICENSE](LICENSE).
