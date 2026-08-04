import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { analyticsApi, type VenueStats } from '../api/analytics.api'
import { featuresApi } from '../api/features.api'
import { newsApi, type CreateNewsPayload } from '../api/news.api'
import { tagsApi } from '../api/tags.api'
import { venuesApi, type CreateVenuePayload } from '../api/venues.api'
import VenueFormFields from '../components/VenueFormFields'
import { useAuth } from '../store/authContext'
import type { NewsItem, Tag, Venue, VenueFeature } from '../types/api'
import { apiErrorMessage } from '../utils/apiError'
import type { PlaceFormPatch } from '../components/PlacesAddressInput'
import { resolveMediaUrl } from '../utils/mediaUrl'
import { displayToWorkTime, workTimeToDisplay } from '../utils/workTime'
import { venueCoordsMismatchWarning } from '../utils/venueValidation'
import {
  canSubmitVenueForModeration,
  venueStatusBadgeClass,
  venueStatusLabel,
} from '../utils/venueStatus'

const emptyVenue: CreateVenuePayload = {
  name: '',
  venue_type: 'bar',
  description: '',
  address: '',
  latitude: '',
  longitude: '',
  phone_number: '',
  email: '',
  avg_check: '',
}

const emptyNews: CreateNewsPayload = {
  venue: 0,
  title: '',
  content: '',
  category: 'general',
  is_paid: false,
  published_at: null,
}

const NEWS_CATEGORIES = [
  { value: 'general', label: 'Загальні' },
  { value: 'promo', label: 'Акції' },
  { value: 'event', label: 'Події' },
]

function venueToForm(v: Venue): CreateVenuePayload {
  return {
    name: v.name,
    venue_type: v.venue_type ?? 'bar',
    description: v.description ?? '',
    address: v.address,
    latitude: String(v.latitude),
    longitude: String(v.longitude),
    phone_number: v.phone_number ?? '',
    email: v.email ?? '',
    website: v.website ?? '',
    avg_check: v.avg_check ?? '',
    work_time: v.work_time ?? {},
    tag_ids: v.tags?.map((t) => t.id) ?? [],
    feature_ids: v.features?.map((f) => f.id) ?? [],
  }
}

export default function ManagerPage() {
  const { user } = useAuth()
  const [tab, setTab] = useState<'venues' | 'news' | 'stats'>('venues')
  const [myVenues, setMyVenues] = useState<Venue[]>([])
  const [myNews, setMyNews] = useState<NewsItem[]>([])
  const [allTags, setAllTags] = useState<Tag[]>([])
  const [allFeatures, setAllFeatures] = useState<VenueFeature[]>([])
  const [workTimeDisplay, setWorkTimeDisplay] = useState('')
  const [statsVenueId, setStatsVenueId] = useState<number | ''>('')
  const [statsFrom, setStatsFrom] = useState('')
  const [statsTo, setStatsTo] = useState('')
  const [venueStats, setVenueStats] = useState<VenueStats | null>(null)
  const [statsError, setStatsError] = useState('')
  const [form, setForm] = useState(emptyVenue)
  const [newsForm, setNewsForm] = useState(emptyNews)
  const [editingVenueId, setEditingVenueId] = useState<number | null>(null)
  const [editingNewsId, setEditingNewsId] = useState<number | null>(null)
  const [publishNow, setPublishNow] = useState(false)
  const [loading, setLoading] = useState(true)
  const [msg, setMsg] = useState('')
  const [showVenueForm, setShowVenueForm] = useState(false)
  const [showNewsForm, setShowNewsForm] = useState(false)
  const [venueImage, setVenueImage] = useState<File | null>(null)
  const [venueImagePreview, setVenueImagePreview] = useState<string | null>(null)
  const [newsImage, setNewsImage] = useState<File | null>(null)
  const [newsImagePreview, setNewsImagePreview] = useState<string | null>(null)

  useEffect(() => {
    tagsApi.list().then((r) => setAllTags(r.data.results)).catch(() => setAllTags([]))
    featuresApi.list().then((r) => setAllFeatures(r.data.results)).catch(() => setAllFeatures([]))
  }, [])

  const load = useCallback(() => {
    if (!user?.username) return
    setLoading(true)
    Promise.all([venuesApi.listMine(), newsApi.list()])
      .then(([venuesRes, newsRes]) => {
        const mine = venuesRes.data.results
        setMyVenues(mine)
        const ids = new Set(mine.map((v) => v.id))
        setMyNews(newsRes.data.results.filter((n) => ids.has(n.venue)))
      })
      .finally(() => setLoading(false))
  }, [user?.username])

  useEffect(() => {
    load()
  }, [load])

  const setVenueField =
    (key: keyof CreateVenuePayload) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setForm((f) => ({ ...f, [key]: e.target.value }))

  const applyPlaceToForm = (patch: PlaceFormPatch) => {
    setForm((f) => ({
      ...f,
      ...patch,
      name: patch.name && !f.name.trim() ? patch.name : f.name || patch.name || f.name,
    }))
  }

  const resetVenueForm = () => {
    setForm(emptyVenue)
    setWorkTimeDisplay('')
    setEditingVenueId(null)
    setShowVenueForm(false)
    setVenueImage(null)
    if (venueImagePreview) URL.revokeObjectURL(venueImagePreview)
    setVenueImagePreview(null)
  }

  const onVenueImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null
    setVenueImage(file)
    if (venueImagePreview) URL.revokeObjectURL(venueImagePreview)
    setVenueImagePreview(file ? URL.createObjectURL(file) : null)
  }

  const resetNewsForm = () => {
    setNewsForm({
      ...emptyNews,
      venue: myVenues[0]?.id ?? 0,
    })
    setEditingNewsId(null)
    setPublishNow(false)
    setShowNewsForm(false)
    setNewsImage(null)
    if (newsImagePreview) URL.revokeObjectURL(newsImagePreview)
    setNewsImagePreview(null)
  }

  const startCreateVenue = () => {
    resetVenueForm()
    setShowVenueForm(true)
  }

  const startEditVenue = (v: Venue) => {
    setEditingVenueId(v.id)
    setForm(venueToForm(v))
    setWorkTimeDisplay(workTimeToDisplay(v.work_time))
    setVenueImage(null)
    setVenueImagePreview(v.main_image_url ? resolveMediaUrl(v.main_image_url) : null)
    setShowVenueForm(true)
    setMsg('')
  }

  const startCreateNews = () => {
    setEditingNewsId(null)
    setNewsForm({ ...emptyNews, venue: myVenues[0]?.id ?? 0 })
    setPublishNow(false)
    setShowNewsForm(true)
    setTab('news')
  }

  const startEditNews = async (n: NewsItem) => {
    setEditingNewsId(n.id)
    setPublishNow(Boolean(n.published_at))
    setTab('news')
    setShowNewsForm(true)
    setNewsImage(null)
    setNewsImagePreview(n.image_url ? resolveMediaUrl(n.image_url) : null)
    try {
      const { data } = await newsApi.get(n.id)
      setNewsForm({
        venue: data.venue,
        title: data.title,
        content: data.content ?? '',
        category: data.category,
        is_paid: data.is_paid,
        published_at: data.published_at,
      })
      if (data.image_url) setNewsImagePreview(resolveMediaUrl(data.image_url))
    } catch {
      setNewsForm({
        venue: n.venue,
        title: n.title,
        content: '',
        category: n.category,
        is_paid: n.is_paid,
        published_at: n.published_at,
      })
    }
  }

  const submitForModeration = async (id: number) => {
    try {
      const { data } = await venuesApi.submit(id)
      setMyVenues((prev) => prev.map((v) => (v.id === id ? { ...v, ...data, status: 'pending' } : v)))
      setMsg('Заклад на модерації.')
      load()
    } catch {
      setMsg('Не вдалося надіслати.')
    }
  }

  const toggleTag = (id: number) => {
    setForm((f) => {
      const ids = f.tag_ids ?? []
      return {
        ...f,
        tag_ids: ids.includes(id) ? ids.filter((t) => t !== id) : [...ids, id],
      }
    })
  }

  const toggleFeature = (id: number) => {
    setForm((f) => {
      const ids = f.feature_ids ?? []
      return {
        ...f,
        feature_ids: ids.includes(id) ? ids.filter((x) => x !== id) : [...ids, id],
      }
    })
  }

  const deleteVenue = async (id: number) => {
    if (!window.confirm('Видалити заклад?')) return
    try {
      await venuesApi.delete(id)
      setMsg('Заклад видалено.')
      load()
    } catch {
      setMsg('Не вдалося видалити заклад.')
    }
  }

  const deleteNews = async (id: number) => {
    if (!window.confirm('Видалити новину?')) return
    try {
      await newsApi.delete(id)
      setMsg('Новину видалено.')
      load()
    } catch {
      setMsg('Не вдалося видалити новину.')
    }
  }

  const loadStats = async () => {
    if (!statsVenueId) return
    setStatsError('')
    setVenueStats(null)
    try {
      const { data } = await analyticsApi.venueStats(Number(statsVenueId), {
        from: statsFrom || undefined,
        to: statsTo || undefined,
      })
      setVenueStats(data)
    } catch {
      setStatsError('Не вдалося завантажити статистику.')
    }
  }

  const coordsWarning = venueCoordsMismatchWarning(form.address, form.latitude, form.longitude)

  const saveVenue = async (e: React.FormEvent) => {
    e.preventDefault()
    setMsg('')
    const mismatch = venueCoordsMismatchWarning(form.address, form.latitude, form.longitude)
    if (mismatch && !window.confirm(`${mismatch}\n\nВсе одно зберегти?`)) {
      return
    }
    const payload: CreateVenuePayload = {
      ...form,
      work_time: displayToWorkTime(workTimeDisplay),
    }
    try {
      if (editingVenueId) {
        await venuesApi.update(editingVenueId, payload, venueImage ?? undefined)
        setMsg('Заклад оновлено.')
      } else {
        await venuesApi.create(payload, venueImage ?? undefined)
        setMsg('Заклад створено. Статус: на модерації.')
      }
      resetVenueForm()
      load()
    } catch (err) {
      setMsg(apiErrorMessage(err, 'Помилка збереження закладу.'))
    }
  }

  const saveNews = async (e: React.FormEvent) => {
    e.preventDefault()
    setMsg('')
    const payload: CreateNewsPayload = {
      ...newsForm,
      published_at: publishNow ? new Date().toISOString() : null,
    }
    try {
      if (editingNewsId) {
        await newsApi.update(editingNewsId, payload, newsImage ?? undefined)
        setMsg('Новину оновлено.')
      } else {
        await newsApi.create(payload, newsImage ?? undefined)
        setMsg('Новину створено.')
      }
      resetNewsForm()
      load()
    } catch (err) {
      setMsg(apiErrorMessage(err, 'Помилка збереження новини.'))
    }
  }

  return (
    <div>
      <h1>Мої заклади</h1>
      <p className="muted">
        Додавай і редагуй свої заклади (після модерації з’являться в каталозі), новини та статистику.
      </p>
      {msg && <p className="muted">{msg}</p>}

      <div className="search-bar" style={{ marginBottom: '1rem' }}>
        <button
          type="button"
          className={`btn ${tab === 'venues' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setTab('venues')}
        >
          Заклади
        </button>
        <button
          type="button"
          className={`btn ${tab === 'news' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setTab('news')}
        >
          Новини
        </button>
        <button
          type="button"
          className={`btn ${tab === 'stats' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setTab('stats')}
        >
          Статистика
        </button>
      </div>

      {tab === 'venues' && (
        <>
          <button type="button" className="btn btn-primary" onClick={startCreateVenue}>
            + Новий заклад
          </button>

          {showVenueForm && (
            <form className="form section" onSubmit={saveVenue}>
              <h2>{editingVenueId ? 'Редагувати заклад' : 'Новий заклад'}</h2>
              <VenueFormFields
                form={form}
                onChange={setVenueField}
                onPlaceResolved={applyPlaceToForm}
                onAddressChange={(address) => setForm((f) => ({ ...f, address }))}
                onCoordinatesChange={(lat, lng) =>
                  setForm((f) => ({ ...f, latitude: lat, longitude: lng }))
                }
                workTimeDisplay={workTimeDisplay}
                onWorkTimeChange={setWorkTimeDisplay}
                tags={allTags}
                features={allFeatures}
                selectedTagIds={form.tag_ids ?? []}
                selectedFeatureIds={form.feature_ids ?? []}
                onToggleTag={toggleTag}
                onToggleFeature={toggleFeature}
              />
              <label>
                Фото закладу
                <input type="file" accept="image/*" onChange={onVenueImageChange} />
              </label>
              {venueImagePreview && (
                <img src={venueImagePreview} alt="" className="venue-form-preview" />
              )}
              {coordsWarning && <p className="error">{coordsWarning}</p>}
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button type="submit" className="btn btn-primary">
                  {editingVenueId ? 'Зберегти' : 'Створити'}
                </button>
                <button type="button" className="btn btn-ghost" onClick={resetVenueForm}>
                  Скасувати
                </button>
              </div>
            </form>
          )}

          {loading && <p className="muted">Завантаження...</p>}

          <div className="card-grid section">
            {myVenues.map((v) => (
              <article key={v.id} className="card">
                <h2>
                  <Link to={`/venues/${v.id}`}>{v.name}</Link>
                </h2>
                <p className="muted">{v.address}</p>
                <p className="muted" style={{ fontSize: '0.85rem' }}>
                  {v.latitude}, {v.longitude}
                </p>
                <span className={`badge ${venueStatusBadgeClass(v.status)}`}>
                  {venueStatusLabel(v.status)}
                </span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.75rem' }}>
                  <button type="button" className="btn btn-ghost" onClick={() => startEditVenue(v)}>
                    Редагувати
                  </button>
                  {canSubmitVenueForModeration(v.status) && (
                    <button type="button" className="btn btn-primary" onClick={() => submitForModeration(v.id)}>
                      На модерацію
                    </button>
                  )}
                  <button type="button" className="btn btn-ghost" onClick={() => deleteVenue(v.id)}>
                    Видалити
                  </button>
                </div>
              </article>
            ))}
          </div>

          {!loading && myVenues.length === 0 && (
            <p className="muted">У тебе ще немає закладів. Створи перший вище.</p>
          )}
        </>
      )}

      {tab === 'news' && (
        <>
          <button
            type="button"
            className="btn btn-primary"
            onClick={startCreateNews}
            disabled={myVenues.length === 0}
          >
            + Нова новина
          </button>
          {myVenues.length === 0 && (
            <p className="muted section">Спочатку створи заклад на вкладці «Заклади».</p>
          )}

          {showNewsForm && myVenues.length > 0 && (
            <form className="form section" onSubmit={saveNews}>
              <h2>{editingNewsId ? 'Редагувати новину' : 'Нова новина'}</h2>
              <label>
                Заклад *
                <select
                  value={newsForm.venue}
                  onChange={(e) => setNewsForm((f) => ({ ...f, venue: Number(e.target.value) }))}
                  required
                >
                  {myVenues.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.name} ({venueStatusLabel(v.status)})
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Заголовок *
                <input
                  value={newsForm.title}
                  onChange={(e) => setNewsForm((f) => ({ ...f, title: e.target.value }))}
                  required
                />
              </label>
              <label>
                Текст *
                <textarea
                  rows={4}
                  value={newsForm.content}
                  onChange={(e) => setNewsForm((f) => ({ ...f, content: e.target.value }))}
                  required
                />
              </label>
              <label>
                Категорія
                <select
                  value={newsForm.category}
                  onChange={(e) => setNewsForm((f) => ({ ...f, category: e.target.value }))}
                >
                  {NEWS_CATEGORIES.map((c) => (
                    <option key={c.value} value={c.value}>
                      {c.label}
                    </option>
                  ))}
                </select>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={publishNow}
                  onChange={(e) => setPublishNow(e.target.checked)}
                />
                Опублікувати зараз (видно на /news)
              </label>
              {(newsForm.category === 'promo' || newsForm.category === 'event') && (
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <input
                    type="checkbox"
                    checked={Boolean(newsForm.is_paid)}
                    onChange={(e) => setNewsForm((f) => ({ ...f, is_paid: e.target.checked }))}
                  />
                  Промо / платне розміщення (потрібно для публікації в каталозі акцій/подій)
                </label>
              )}
              <label>
                Фото новини
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => {
                    const file = e.target.files?.[0] ?? null
                    setNewsImage(file)
                    if (newsImagePreview) URL.revokeObjectURL(newsImagePreview)
                    setNewsImagePreview(file ? URL.createObjectURL(file) : null)
                  }}
                />
              </label>
              {newsImagePreview && (
                <img src={newsImagePreview} alt="" className="venue-form-preview" />
              )}
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button type="submit" className="btn btn-primary">
                  {editingNewsId ? 'Зберегти' : 'Створити'}
                </button>
                <button type="button" className="btn btn-ghost" onClick={resetNewsForm}>
                  Скасувати
                </button>
              </div>
            </form>
          )}

          {loading && <p className="muted">Завантаження...</p>}

          <div className="card-grid section">
            {myNews.map((n) => (
              <article key={n.id} className="card">
                <h2>{n.title}</h2>
                <p className="muted">
                  <span className="badge">{n.category}</span>
                  {n.published_at
                    ? ` · опубліковано ${new Date(n.published_at).toLocaleDateString('uk-UA')}`
                    : ' · чернетка'}
                </p>
                <p className="muted">Заклад #{n.venue}</p>
                <button
                  type="button"
                  className="btn btn-ghost"
                  style={{ marginTop: '0.5rem' }}
                  onClick={() => startEditNews(n)}
                >
                  Редагувати
                </button>
                <button
                  type="button"
                  className="btn btn-ghost"
                  style={{ marginTop: '0.5rem', marginLeft: '0.5rem' }}
                  onClick={() => deleteNews(n.id)}
                >
                  Видалити
                </button>
              </article>
            ))}
          </div>

          {!loading && myNews.length === 0 && myVenues.length > 0 && (
            <p className="muted">Новин ще немає.</p>
          )}
        </>
      )}

      {tab === 'stats' && (
        <section className="section">
          <h2>Перегляди закладів</h2>
          <p className="muted">Статистика за останні 7 днів.</p>
          <div className="filter-row">
            <label className="filter-field">
              <span className="filter-label">Заклад</span>
              <select
                value={statsVenueId}
                onChange={(e) => setStatsVenueId(e.target.value ? Number(e.target.value) : '')}
              >
                <option value="">Оберіть заклад</option>
                {myVenues.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="filter-field">
              <span className="filter-label">Від</span>
              <input type="date" value={statsFrom} onChange={(e) => setStatsFrom(e.target.value)} />
            </label>
            <label className="filter-field">
              <span className="filter-label">До</span>
              <input type="date" value={statsTo} onChange={(e) => setStatsTo(e.target.value)} />
            </label>
            <button type="button" className="btn btn-primary" onClick={loadStats} disabled={!statsVenueId}>
              Показати
            </button>
          </div>
          {statsError && <p className="error">{statsError}</p>}
          {venueStats && (
            <div className="stats-panel">
              <p>
                <strong>{venueStats.venue_name}</strong>
              </p>
              <p className="muted">Всього переглядів: {venueStats.total_views}</p>
              <p className="muted">За 7 днів: {venueStats.views_last_7_days}</p>
              {venueStats.views_in_range != null && (
                <p className="muted">У вибраному діапазоні: {venueStats.views_in_range}</p>
              )}
              <ul className="review-list">
                {venueStats.views_by_day.map((row) => (
                  <li key={row.date}>
                    {row.date}: <strong>{row.count}</strong>
                    <span className="stats-bar" style={{ width: `${Math.min(row.count * 12, 200)}px` }} />
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}
    </div>
  )
}
