import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PageHeader from '../components/PageHeader'
import { newsApi } from '../api/news.api'
import type { NewsItem } from '../types/api'
import { resolveMediaUrl } from '../utils/mediaUrl'

const CATEGORIES = [
  { value: '', label: 'Усі' },
  { value: 'general', label: 'Загальні' },
  { value: 'promo', label: 'Акції' },
  { value: 'event', label: 'Події' },
]

export default function NewsPage() {
  const [news, setNews] = useState<NewsItem[]>([])
  const [category, setCategory] = useState('')
  const [loading, setLoading] = useState(true)
  const [nextUrl, setNextUrl] = useState<string | null>(null)
  const [page, setPage] = useState(1)

  const load = useCallback(
    (pageNum: number, append: boolean) => {
      setLoading(true)
      const params: Record<string, string | number> = { page: pageNum }
      if (category) params.category = category
      newsApi
        .list(params)
        .then((res) => {
          setNews((prev) => (append ? [...prev, ...res.data.results] : res.data.results))
          setNextUrl(res.data.next)
          setPage(pageNum)
        })
        .finally(() => setLoading(false))
    },
    [category],
  )

  useEffect(() => {
    load(1, false)
  }, [load])

  return (
    <div>
      <PageHeader title="Новини" lead="Акції, події та оновлення від закладів." />
      <div className="search-bar">
        {CATEGORIES.map((c) => (
          <button
            key={c.value}
            type="button"
            className={`btn ${category === c.value ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setCategory(c.value)}
          >
            {c.label}
          </button>
        ))}
      </div>
      {loading && news.length === 0 && <p className="muted">Завантаження...</p>}
      <div className="card-grid">
        {news.map((n) => {
          const img = resolveMediaUrl(n.image_url)
          return (
            <article key={n.id} className="card card-news">
              {img && <img src={img} alt="" className="card-cover" />}
              <h2>
                <Link to={`/news/${n.id}`}>{n.title}</Link>
              </h2>
              <p className="muted">
                <span className={`badge badge-${n.category === 'promo' ? 'pending' : 'published'}`}>
                  {n.category}
                </span>
                {n.is_paid && <span className="badge">промо</span>}
                {n.published_at && ` · ${new Date(n.published_at).toLocaleDateString('uk-UA')}`}
              </p>
              <Link to={`/venues/${n.venue}`}>{n.venue_name ?? `Заклад #${n.venue}`}</Link>
            </article>
          )
        })}
      </div>
      {!loading && news.length === 0 && <p className="muted">Новин немає.</p>}
      {nextUrl && (
        <button
          type="button"
          className="btn btn-ghost"
          style={{ marginTop: '1rem' }}
          disabled={loading}
          onClick={() => load(page + 1, true)}
        >
          {loading ? '...' : 'Ще новини'}
        </button>
      )}
    </div>
  )
}
