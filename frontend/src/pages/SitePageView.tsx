import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { cmsApi, type SitePage } from '../api/cms.api'

export default function SitePageView() {
  const { slug } = useParams()
  const [page, setPage] = useState<SitePage | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!slug) return
    setLoading(true)
    cmsApi
      .getPage(slug)
      .then((res) => setPage(res.data))
      .catch(() => setError('Сторінку не знайдено.'))
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) return <p className="muted">Завантаження...</p>
  if (error || !page) return <p className="error">{error || 'Помилка'}</p>

  return (
    <article className="venue-detail">
      <h1>{page.title}</h1>
      <p style={{ whiteSpace: 'pre-wrap', marginTop: '1rem' }}>{page.content}</p>
      <p style={{ marginTop: '2rem' }}>
        <Link to="/">← На головну</Link>
      </p>
    </article>
  )
}
