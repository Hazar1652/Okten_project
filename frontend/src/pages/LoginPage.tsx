import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import OAuthButtons from '../components/OAuthButtons'
import { useAuth } from '../store/authContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [oauthError, setOauthError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login({ username, password })
      navigate('/')
    } catch {
      setError('Невірний логін або пароль.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <h1>Увійти</h1>
      <form className="form" onSubmit={handleSubmit}>
        <label>
          Email або логін
          <input
            type="text"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="user_demo або email"
            required
          />
        </label>
        <label>
          Пароль
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Вхід...' : 'Увійти'}
        </button>
      </form>

      <OAuthButtons
        disabled={loading}
        onSuccess={() => navigate('/')}
        onError={setOauthError}
      />
      {oauthError && <p className="error">{oauthError}</p>}

      <p className="muted auth-page-footer">
        Немає акаунта? <Link to="/register">Зареєструватись</Link>
      </p>
      <p className="muted auth-page-hint">Демо: user_demo / DemoPass123!</p>
    </div>
  )
}
