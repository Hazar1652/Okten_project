import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div>
      <h1>404</h1>
      <p className="muted">Сторінку не знайдено.</p>
      <Link to="/">На головну</Link>
    </div>
  )
}
