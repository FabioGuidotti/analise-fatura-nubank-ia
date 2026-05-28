import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { initials } from '../lib/format'

const NAV = [
  { to: '/', icon: '🏠', label: 'Visão Geral', end: true },
  { to: '/importar', icon: '📥', label: 'Importar Fatura' },
  { to: '/transacoes', icon: '📋', label: 'Transações' },
  { to: '/analise', icon: '📊', label: 'Análise' },
  { to: '/orcamentos', icon: '🎯', label: 'Orçamentos' },
  { to: '/categorias', icon: '🏷️', label: 'Categorias' },
  { to: '/assistente', icon: '🤖', label: 'Assistente IA' },
]

function useTheme() {
  const [theme, setTheme] = useState(() => localStorage.getItem('ff_theme') || 'dark')
  const toggle = () => {
    const next = theme === 'dark' ? 'light' : 'dark'
    setTheme(next)
    localStorage.setItem('ff_theme', next)
    document.documentElement.setAttribute('data-theme', next)
  }
  // Aplica no primeiro render.
  if (document.documentElement.getAttribute('data-theme') !== theme) {
    document.documentElement.setAttribute('data-theme', theme)
  }
  return { theme, toggle }
}

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const { theme, toggle } = useTheme()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="app-shell">
      {open && <div className="backdrop" onClick={() => setOpen(false)} />}
      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <div className="brand">
          <div className="brand-logo">💸</div>
          <span className="brand-name">Finança Fácil</span>
        </div>
        <nav className="nav">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setOpen(false)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="nav-item" onClick={toggle}>
            <span className="nav-icon">{theme === 'dark' ? '🌙' : '☀️'}</span>
            Tema {theme === 'dark' ? 'escuro' : 'claro'}
          </div>
          <div className="nav-item" onClick={handleLogout}>
            <span className="nav-icon">🚪</span>
            Sair
          </div>
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <button className="btn btn-ghost btn-sm menu-toggle" onClick={() => setOpen(true)}>
            ☰
          </button>
          <div className="grow" />
          <div className="row gap-sm">
            <div className="col" style={{ gap: 0, alignItems: 'flex-end' }}>
              <strong style={{ fontSize: '0.9rem' }}>{user?.name}</strong>
              <span className="faint" style={{ fontSize: '0.78rem' }}>{user?.email}</span>
            </div>
            <div className="avatar">{initials(user?.name)}</div>
          </div>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
