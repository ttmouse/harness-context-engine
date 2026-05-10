import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Settings from './pages/Settings'
import Reports from './pages/Reports'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/reports" element={<Reports />} />
      </Routes>
    </BrowserRouter>
  )
}
