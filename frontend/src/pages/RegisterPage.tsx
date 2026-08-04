import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import OAuthButtons from '../components/OAuthButtons'
import { useAuth } from '../store/authContext'

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
  })
  const [error, setError] = useState('')
  const [oauthError, setOauthError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(form)
      navigate('/')
    } catch (err: unknown) {
      const data = (err as { response?: { data?: Record<string, string[]> } })?.response?.data
      if (data) {
        const msg = Object.entries(data)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
          .join('; ')
        setError(msg)
      } else {
        setError('Помилка реєстрації.')
      }
    } finally {
      setLoading(false)
    }
  }

  const set = (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }))

  return (
    <div className="auth-page">
      <h1>Реєстрація</h1>
      <form className="form" onSubmit={handleSubmit}>
        <label>
          Логін
          <input value={form.username} onChange={set('username')} required />
        </label>
        <label>
          Email
          <input type="email" value={form.email} onChange={set('email')} required />
        </label>
        <label>
          Ім&apos;я
          <input value={form.first_name} onChange={set('first_name')} />
        </label>
        <label>
          Пароль
          <input type="password" value={form.password} onChange={set('password')} required />
        </label>
        <label>
          Підтвердження пароля
          <input
            type="password"
            value={form.password_confirm}
            onChange={set('password_confirm')}
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? '...' : 'Зареєструватись'}
        </button>
      </form>

      <OAuthButtons
        disabled={loading}
        onSuccess={() => navigate('/')}
        onError={setOauthError}
      />
      {oauthError && <p className="error">{oauthError}</p>}

      <p className="muted auth-page-footer">
        Вже є акаунт? <Link to="/login">Увійти</Link>
      </p>
    </div>
  )
}
