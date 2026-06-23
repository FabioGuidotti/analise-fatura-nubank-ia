import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Analysis from './pages/Analysis'
import Budgets from './pages/Budgets'
import Categories from './pages/Categories'
import Chat from './pages/Chat'
import Dashboard from './pages/Dashboard'
import Import from './pages/Import'
import Login from './pages/Login'
import Register from './pages/Register'
import Transactions from './pages/Transactions'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<Register />} />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/importar" element={<Import />} />
        <Route path="/transacoes" element={<Transactions />} />
        <Route path="/analise" element={<Analysis />} />
        <Route path="/orcamentos" element={<Budgets />} />
        <Route path="/categorias" element={<Categories />} />
        <Route path="/assistente" element={<Chat />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
