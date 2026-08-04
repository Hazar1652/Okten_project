import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { newsApi } from '../api/news.api'
import type { NewsItem } from '../types/api'
import { resolveMediaUrl } from '../utils/mediaUrl'

const CATEGORY_LABELS: Record<string, string> = {
  general: 'Загальні',
  promo: 'Акції',
  event: 'Події',
}

export default function NewsDetailPage() {
  const { id } = useParams()
  const newsId = Number(id)
  const [item, setItem] = useState<NewsItem | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!newsId || Number.isNaN(newsId)) return
    setLoading(true)
    setError('')
    newsApi
      .get(newsId)
      .then((res) => setItem(res.data))
      .catch(() => setError('Новину не знайдено.'))
      .finally(() => setLoading(false))
  }, [newsId])

  if (loading) return <p className="muted">Завантаження...</p>
  if (error || !item) return <p className="error">{error || 'Помилка'}</p>

  const img = resolveMediaUrl(item.image_url)

  return (
    <article className="venue-detail">
      <p>
        <Link to="/news">← Новини</Link>
      </p>
      {img && <img src={img} alt="" className="venue-detail-cover" />}
      <h1>{item.title}</h1>
      <div className="meta">
        <span className="badge">{CATEGORY_LABELS[item.category] ?? item.category}</span>
        {item.published_at && (
          <span>{new Date(item.published_at).toLocaleString('uk-UA')}</span>
        )}
        {item.is_paid && <span className="badge">Платне розміщення</span>}
      </div>
      {item.content && <p style={{ marginTop: '1rem', whiteSpace: 'pre-wrap' }}>{item.content}</p>}
      <p style={{ marginTop: '1.5rem' }}>
        <Link to={`/venues/${item.venue}`} className="btn btn-primary">
          Перейти до закладу{item.venue_name ? `: ${item.venue_name}` : ''}
        </Link>
      </p>
    </article>
  )
}
