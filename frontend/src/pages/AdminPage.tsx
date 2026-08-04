import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { analyticsApi, type VenueStats } from '../api/analytics.api'
import { cmsApi, type SitePage, type TopCategory } from '../api/cms.api'
import { complaintsApi, type Complaint } from '../api/complaints.api'
import { featuresApi } from '../api/features.api'
import { newsApi, type CreateNewsPayload } from '../api/news.api'
import { reviewsApi } from '../api/reviews.api'
import { tagsApi } from '../api/tags.api'
import { usersApi, type AdminUser } from '../api/users.api'
import { venuesApi, type CreateVenuePayload } from '../api/venues.api'
import VenueFormFields from '../components/VenueFormFields'
import type { NewsItem, Review, Tag, Venue, VenueFeature } from '../types/api'
import { apiErrorMessage } from '../utils/apiError'
import { displayToWorkTime, workTimeToDisplay } from '../utils/workTime'
import { resolveMediaUrl } from '../utils/mediaUrl'
import { venueStatusBadgeClass, venueStatusLabel } from '../utils/venueStatus'

const COMPLAINT_STATUSES = ['new', 'in_progress', 'resolved', 'rejected'] as const
const ROLES = ['user', 'venue_manager', 'critic', 'super_admin'] as const
const NEWS_CATEGORIES = [
  { value: 'general', label: 'Загальні' },
  { value: 'promo', label: 'Акції' },
  { value: 'event', label: 'Події' },
]
type Tab = 'moderation' | 'venues' | 'news' | 'reviews' | 'users' | 'analytics' | 'content'

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
    status: v.status,
  }
}

export default function AdminPage() {
  const [tab, setTab] = useState<Tab>('moderation')
  const [pending, setPending] = useState<Venue[]>([])
  const [allVenues, setAllVenues] = useState<Venue[]>([])
  const [allNews, setAllNews] = useState<NewsItem[]>([])
  const [allReviews, setAllReviews] = useState<Review[]>([])
  const [users, setUsers] = useState<AdminUser[]>([])
  const [complaints, setComplaints] = useState<Complaint[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [features, setFeatures] = useState<VenueFeature[]>([])
  const [pages, setPages] = useState<SitePage[]>([])
  const [topCategories, setTopCategories] = useState<TopCategory[]>([])
  const [loading, setLoading] = useState(true)
  const [msg, setMsg] = useState('')
  const [venueSearch, setVenueSearch] = useState('')
  const [venueStatus, setVenueStatus] = useState('')
  const [statsVenueId, setStatsVenueId] = useState('')
  const [statsFrom, setStatsFrom] = useState('')
  const [statsTo, setStatsTo] = useState('')
  const [stats, setStats] = useState<VenueStats | null>(null)
  const [ownerPick, setOwnerPick] = useState<Record<number, string>>({})
  const [editPage, setEditPage] = useState<SitePage | null>(null)
  const [newCatName, setNewCatName] = useState('')
  const [editUserId, setEditUserId] = useState<number | null>(null)
  const [userEdit, setUserEdit] = useState({
    email: '',
    first_name: '',
    last_name: '',
    phone_number: '',
  })
  const [newCatTag, setNewCatTag] = useState('')

  const [editingVenueId, setEditingVenueId] = useState<number | null>(null)
  const [venueForm, setVenueForm] = useState<CreateVenuePayload | null>(null)
  const [workTimeDisplay, setWorkTimeDisplay] = useState('')
  const [venueImage, setVenueImage] = useState<File | null>(null)

  const [editingNews, setEditingNews] = useState<CreateNewsPayload & { id: number } | null>(null)
  const [editingReview, setEditingReview] = useState<{
    id: number
    rating: number
    text: string
    check_amount: string
  } | null>(null)

  const loadModeration = useCallback(() => {
    setLoading(true)
    Promise.all([venuesApi.list({ status: 'pending' }), complaintsApi.list()])
      .then(([venuesRes, complaintsRes]) => {
        setPending(venuesRes.data.results)
        setComplaints(complaintsRes.data.results)
      })
      .catch(() => setMsg('Не вдалося завантажити модерацію.'))
      .finally(() => setLoading(false))
  }, [])

  const loadVenues = useCallback(() => {
    setLoading(true)
    const params: { search?: string; status?: string } = {}
    if (venueSearch.trim()) params.search = venueSearch.trim()
    if (venueStatus) params.status = venueStatus
    venuesApi
      .list(params)
      .then((res) => setAllVenues(res.data.results))
      .catch(() => setMsg('Не вдалося завантажити заклади.'))
      .finally(() => setLoading(false))
  }, [venueSearch, venueStatus])

  const loadNews = useCallback(() => {
    setLoading(true)
    newsApi
      .list()
      .then((res) => setAllNews(res.data.results))
      .catch(() => setMsg('Не вдалося завантажити новини.'))
      .finally(() => setLoading(false))
  }, [])

  const loadReviews = useCallback(() => {
    setLoading(true)
    reviewsApi
      .list()
      .then((res) => setAllReviews(res.data.results))
      .catch(() => setMsg('Не вдалося завантажити відгуки.'))
      .finally(() => setLoading(false))
  }, [])

  const loadUsers = useCallback(() => {
    setLoading(true)
    usersApi
      .adminList()
      .then((res) => setUsers(res.data.results))
      .catch(() => setMsg('Не вдалося завантажити користувачів.'))
      .finally(() => setLoading(false))
  }, [])

  const loadContent = useCallback(() => {
    setLoading(true)
    Promise.all([cmsApi.listPages(), cmsApi.listTopCategories(), tagsApi.list()])
      .then(([p, t, tagsRes]) => {
        setPages(p.data.results)
        setTopCategories(t.data.results)
        setTags(tagsRes.data.results)
      })
      .catch(() => setMsg('Не вдалося завантажити контент.'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    tagsApi.list().then((r) => setTags(r.data.results)).catch(() => undefined)
    featuresApi.list().then((r) => setFeatures(r.data.results)).catch(() => undefined)
  }, [])

  useEffect(() => {
    if (tab === 'moderation') loadModeration()
    if (tab === 'venues') {
      loadVenues()
      usersApi.adminList().then((r) => setUsers(r.data.results)).catch(() => undefined)
    }
    if (tab === 'news') loadNews()
    if (tab === 'reviews') loadReviews()
    if (tab === 'users') loadUsers()
    if (tab === 'content') loadContent()
  }, [tab, loadModeration, loadVenues, loadNews, loadReviews, loadUsers, loadContent])

  const moderate = async (id: number, action: 'approve' | 'reject') => {
    setMsg('')
    try {
      if (action === 'approve') await venuesApi.approve(id)
      else await venuesApi.reject(id)
      setMsg(action === 'approve' ? 'Заклад опубліковано.' : 'Заклад відхилено.')
      loadModeration()
    } catch {
      setMsg('Помилка модерації.')
    }
  }

  const updateComplaint = async (id: number, status: string) => {
    try {
      await complaintsApi.updateStatus(id, status)
      setComplaints((prev) => prev.map((c) => (c.id === id ? { ...c, status } : c)))
    } catch {
      setMsg('Не вдалося оновити скаргу.')
    }
  }

  const reassignOwner = async (venueId: number) => {
    const ownerId = Number(ownerPick[venueId])
    if (!ownerId) return
    try {
      await venuesApi.update(venueId, { owner_id: ownerId })
      setMsg('Власника оновлено.')
      loadVenues()
    } catch {
      setMsg('Не вдалося призначити власника.')
    }
  }

  const deleteVenue = async (id: number) => {
    if (!window.confirm('Видалити заклад?')) return
    try {
      await venuesApi.delete(id)
      setMsg('Заклад видалено.')
      setEditingVenueId(null)
      setVenueForm(null)
      loadVenues()
    } catch {
      setMsg('Не вдалося видалити.')
    }
  }

  const startEditVenue = async (v: Venue) => {
    setMsg('')
    try {
      const { data } = await venuesApi.get(v.id)
      setEditingVenueId(data.id)
      setVenueForm(venueToForm(data))
      setWorkTimeDisplay(workTimeToDisplay(data.work_time))
      setVenueImage(null)
    } catch {
      setMsg('Не вдалося відкрити заклад для редагування.')
    }
  }

  const setVenueField =
    (key: keyof CreateVenuePayload) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setVenueForm((f) => (f ? { ...f, [key]: e.target.value } : f))

  const toggleTag = (id: number) => {
    setVenueForm((f) => {
      if (!f) return f
      const ids = f.tag_ids ?? []
      return {
        ...f,
        tag_ids: ids.includes(id) ? ids.filter((t) => t !== id) : [...ids, id],
      }
    })
  }

  const toggleFeature = (id: number) => {
    setVenueForm((f) => {
      if (!f) return f
      const ids = f.feature_ids ?? []
      return {
        ...f,
        feature_ids: ids.includes(id) ? ids.filter((x) => x !== id) : [...ids, id],
      }
    })
  }

  const saveVenueEdit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingVenueId || !venueForm) return
    setMsg('')
    try {
      await venuesApi.update(
        editingVenueId,
        {
          ...venueForm,
          work_time: displayToWorkTime(workTimeDisplay),
        },
        venueImage ?? undefined,
      )
      setMsg('Заклад оновлено.')
      setEditingVenueId(null)
      setVenueForm(null)
      loadVenues()
    } catch (err) {
      setMsg(apiErrorMessage(err, 'Помилка збереження закладу.'))
    }
  }

  const changeRole = async (id: number, role: string) => {
    try {
      await usersApi.adminUpdate(id, { role })
      setUsers((prev) => prev.map((u) => (u.id === id ? { ...u, role } : u)))
    } catch {
      setMsg('Не вдалося змінити роль.')
    }
  }

  const deactivateUser = async (id: number) => {
    if (!window.confirm('Деактивувати користувача?')) return
    try {
      await usersApi.adminDeactivate(id)
      setMsg('Користувача деактивовано.')
      loadUsers()
    } catch {
      setMsg('Не вдалося деактивувати.')
    }
  }

  const startEditUser = (u: AdminUser) => {
    setEditUserId(u.id)
    setUserEdit({
      email: u.email ?? '',
      first_name: u.first_name ?? '',
      last_name: u.last_name ?? '',
      phone_number: u.phone_number ?? '',
    })
  }

  const saveUserEdit = async (id: number) => {
    try {
      const { data } = await usersApi.adminUpdate(id, {
        email: userEdit.email,
        first_name: userEdit.first_name,
        last_name: userEdit.last_name,
        phone_number: userEdit.phone_number || null,
      })
      setUsers((prev) => prev.map((u) => (u.id === id ? { ...u, ...data } : u)))
      setEditUserId(null)
      setMsg('Користувача оновлено.')
    } catch (err) {
      setMsg(apiErrorMessage(err, 'Не вдалося оновити користувача.'))
    }
  }

  const deleteUser = async (id: number) => {
    if (!window.confirm('Видалити користувача НАЗАВЖДИ? Дію не можна скасувати.')) return
    try {
      await usersApi.adminDelete(id)
      setUsers((prev) => prev.filter((u) => u.id !== id))
      setMsg('Користувача видалено.')
    } catch (err) {
      setMsg(apiErrorMessage(err, 'Не вдалося видалити користувача.'))
    }
  }

  const loadStats = async () => {
    const id = Number(statsVenueId)
    if (!id) return
    setStats(null)
    try {
      const { data } = await analyticsApi.venueStats(id, {
        from: statsFrom || undefined,
        to: statsTo || undefined,
      })
      setStats(data)
    } catch {
      setMsg('Статистика недоступна для цього id.')
    }
  }

  const savePage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editPage) return
    try {
      await cmsApi.updatePage(editPage.slug, {
        title: editPage.title,
        content: editPage.content,
      })
      setMsg('Сторінку збережено.')
      setEditPage(null)
      loadContent()
    } catch {
      setMsg('Не вдалося зберегти сторінку.')
    }
  }

  const addTopCategory = async () => {
    if (!newCatName.trim()) return
    try {
      await cmsApi.createTopCategory({
        name: newCatName.trim(),
        tag_id: newCatTag ? Number(newCatTag) : null,
        order: topCategories.length + 1,
        is_active: true,
      })
      setNewCatName('')
      setNewCatTag('')
      loadContent()
    } catch {
      setMsg('Не вдалося додати категорію.')
    }
  }

  const saveNews = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingNews) return
    try {
      const { id, ...payload } = editingNews
      await newsApi.update(id, payload)
      setMsg('Новину оновлено.')
      setEditingNews(null)
      loadNews()
    } catch (err) {
      setMsg(apiErrorMessage(err, 'Помилка збереження новини.'))
    }
  }

  const deleteNews = async (id: number) => {
    if (!window.confirm('Видалити новину?')) return
    try {
      await newsApi.delete(id)
      setMsg('Новину видалено.')
      loadNews()
    } catch {
      setMsg('Не вдалося видалити новину.')
    }
  }

  const saveReview = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingReview) return
    try {
      await reviewsApi.update(editingReview.id, {
        rating: editingReview.rating,
        text: editingReview.text,
        check_amount: editingReview.check_amount || undefined,
      })
      setMsg('Відгук оновлено.')
      setEditingReview(null)
      loadReviews()
    } catch (err) {
      setMsg(apiErrorMessage(err, 'Помилка збереження відгуку.'))
    }
  }

  const deleteReview = async (id: number) => {
    if (!window.confirm('Видалити відгук?')) return
    try {
      await reviewsApi.delete(id)
      setMsg('Відгук видалено.')
      loadReviews()
    } catch {
      setMsg('Не вдалося видалити відгук.')
    }
  }

  const tabs: { id: Tab; label: string }[] = [
    { id: 'moderation', label: 'Модерація' },
    { id: 'venues', label: 'Заклади' },
    { id: 'news', label: 'Новини' },
    { id: 'reviews', label: 'Відгуки' },
    { id: 'users', label: 'Користувачі' },
    { id: 'analytics', label: 'Аналітика' },
    { id: 'content', label: 'Контент' },
  ]

  return (
    <div>
      <h1>Панель адміна</h1>
      <p className="muted">
        Модерація, заклади, новини, відгуки, користувачі, аналітика та тексти сайту.
      </p>
      {msg && <p className={msg.includes('Помилка') || msg.includes('Не ') ? 'error' : 'muted'}>{msg}</p>}

      <div className="search-bar" style={{ marginBottom: '1rem', flexWrap: 'wrap' }}>
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            className={`btn ${tab === t.id ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading && tab !== 'analytics' && <p className="muted">Завантаження...</p>}

      {tab === 'moderation' && (
        <>
          <section className="section" style={{ marginTop: 0, borderTop: 'none', paddingTop: 0 }}>
            <h2>Заклади на модерації ({pending.length})</h2>
            {pending.length === 0 && !loading && (
              <p className="muted">Немає закладів на модерації.</p>
            )}
            <div className="card-grid">
              {pending.map((v) => (
                <article key={v.id} className="card">
                  <h2>
                    <Link to={`/venues/${v.id}`}>{v.name}</Link>
                  </h2>
                  <p className="muted">{v.address}</p>
                  <p className="muted">Власник: {v.owner}</p>
                  <span className={`badge ${venueStatusBadgeClass(v.status)}`}>
                    {venueStatusLabel(v.status)}
                  </span>
                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
                    <button type="button" className="btn btn-primary" onClick={() => moderate(v.id, 'approve')}>
                      Схвалити
                    </button>
                    <button type="button" className="btn btn-ghost" onClick={() => moderate(v.id, 'reject')}>
                      Відхилити
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>
          <section className="section">
            <h2>Скарги ({complaints.length})</h2>
            {complaints.length === 0 && !loading && <p className="muted">Скарг немає.</p>}
            <ul className="review-list">
              {complaints.map((c) => (
                <li key={c.id}>
                  <p>
                    <strong>#{c.id}</strong> · відгук #{c.review} · {c.author}
                  </p>
                  <p>{c.reason}</p>
                  <label className="muted" style={{ fontSize: '0.85rem' }}>
                    Статус{' '}
                    <select
                      value={c.status}
                      onChange={(e) => updateComplaint(c.id, e.target.value)}
                      style={{ marginLeft: '0.5rem' }}
                    >
                      {COMPLAINT_STATUSES.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
                  </label>
                </li>
              ))}
            </ul>
          </section>
        </>
      )}

      {tab === 'venues' && (
        <section className="section" style={{ marginTop: 0, borderTop: 'none', paddingTop: 0 }}>
          <h2>Усі заклади</h2>
          <form
            className="search-bar"
            onSubmit={(e) => {
              e.preventDefault()
              loadVenues()
            }}
          >
            <input
              placeholder="Пошук..."
              value={venueSearch}
              onChange={(e) => setVenueSearch(e.target.value)}
            />
            <select value={venueStatus} onChange={(e) => setVenueStatus(e.target.value)}>
              <option value="">Будь-який статус</option>
              <option value="pending">pending</option>
              <option value="published">published</option>
              <option value="rejected">rejected</option>
            </select>
            <button type="submit" className="btn btn-primary">
              Застосувати
            </button>
          </form>

          {venueForm && editingVenueId && (
            <form className="form section" onSubmit={saveVenueEdit}>
              <h3>Редагувати заклад #{editingVenueId}</h3>
              <VenueFormFields
                form={venueForm}
                onChange={setVenueField}
                onAddressChange={(address) => setVenueForm((f) => (f ? { ...f, address } : f))}
                onCoordinatesChange={(lat, lng) =>
                  setVenueForm((f) => (f ? { ...f, latitude: lat, longitude: lng } : f))
                }
                workTimeDisplay={workTimeDisplay}
                onWorkTimeChange={setWorkTimeDisplay}
                tags={tags}
                features={features}
                selectedTagIds={venueForm.tag_ids ?? []}
                selectedFeatureIds={venueForm.feature_ids ?? []}
                onToggleTag={toggleTag}
                onToggleFeature={toggleFeature}
              />
              <label>
                Статус
                <select
                  value={venueForm.status ?? 'pending'}
                  onChange={(e) => setVenueForm((f) => (f ? { ...f, status: e.target.value } : f))}
                >
                  <option value="pending">pending</option>
                  <option value="published">published</option>
                  <option value="rejected">rejected</option>
                  <option value="archived">archived</option>
                </select>
              </label>
              <label>
                Фото
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setVenueImage(e.target.files?.[0] ?? null)}
                />
              </label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button type="submit" className="btn btn-primary">
                  Зберегти
                </button>
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => {
                    setEditingVenueId(null)
                    setVenueForm(null)
                  }}
                >
                  Скасувати
                </button>
              </div>
            </form>
          )}

          <div className="card-grid">
            {allVenues.map((v) => (
              <article key={v.id} className="card">
                <h2>
                  <Link to={`/venues/${v.id}`}>{v.name}</Link>
                </h2>
                <p className="muted">
                  {venueStatusLabel(v.status)} · owner: {v.owner}
                </p>
                {v.main_image_url && (
                  <img
                    src={resolveMediaUrl(v.main_image_url) ?? ''}
                    alt=""
                    className="venue-form-preview"
                  />
                )}
                <label className="muted" style={{ display: 'block', marginTop: '0.5rem' }}>
                  Новий власник
                  <select
                    value={ownerPick[v.id] ?? ''}
                    onChange={(e) => setOwnerPick((p) => ({ ...p, [v.id]: e.target.value }))}
                  >
                    <option value="">—</option>
                    {users.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.username} ({u.role})
                      </option>
                    ))}
                  </select>
                </label>
                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
                  <button type="button" className="btn btn-primary" onClick={() => startEditVenue(v)}>
                    Редагувати
                  </button>
                  <button type="button" className="btn btn-ghost" onClick={() => reassignOwner(v.id)}>
                    Призначити owner
                  </button>
                  <button type="button" className="btn btn-ghost" onClick={() => deleteVenue(v.id)}>
                    Видалити
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}

      {tab === 'news' && (
        <section className="section" style={{ marginTop: 0, borderTop: 'none', paddingTop: 0 }}>
          <h2>Новини ({allNews.length})</h2>
          {editingNews && (
            <form className="form" onSubmit={saveNews} style={{ marginBottom: '1.5rem' }}>
              <h3>Редагувати новину #{editingNews.id}</h3>
              <label>
                Заголовок
                <input
                  value={editingNews.title}
                  onChange={(e) => setEditingNews({ ...editingNews, title: e.target.value })}
                  required
                />
              </label>
              <label>
                Текст
                <textarea
                  rows={4}
                  value={editingNews.content}
                  onChange={(e) => setEditingNews({ ...editingNews, content: e.target.value })}
                  required
                />
              </label>
              <label>
                Категорія
                <select
                  value={editingNews.category}
                  onChange={(e) => setEditingNews({ ...editingNews, category: e.target.value })}
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
                  checked={Boolean(editingNews.is_paid)}
                  onChange={(e) => setEditingNews({ ...editingNews, is_paid: e.target.checked })}
                />
                Платне розміщення
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={Boolean(editingNews.published_at)}
                  onChange={(e) =>
                    setEditingNews({
                      ...editingNews,
                      published_at: e.target.checked ? new Date().toISOString() : null,
                    })
                  }
                />
                Опубліковано
              </label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button type="submit" className="btn btn-primary">
                  Зберегти
                </button>
                <button type="button" className="btn btn-ghost" onClick={() => setEditingNews(null)}>
                  Скасувати
                </button>
              </div>
            </form>
          )}
          <ul className="review-list">
            {allNews.map((n) => (
              <li key={n.id}>
                <strong>{n.title}</strong>{' '}
                <span className="badge">{n.category}</span>
                {n.is_paid && <span className="badge">paid</span>}
                <span className="muted"> · заклад #{n.venue}</span>
                <div style={{ marginTop: '0.35rem', display: 'flex', gap: '0.5rem' }}>
                  <button
                    type="button"
                    className="btn btn-ghost"
                    onClick={async () => {
                      try {
                        const { data } = await newsApi.get(n.id)
                        setEditingNews({
                          id: data.id,
                          venue: data.venue,
                          title: data.title,
                          content: data.content ?? '',
                          category: data.category,
                          is_paid: data.is_paid,
                          published_at: data.published_at,
                        })
                      } catch {
                        setMsg('Не вдалося відкрити новину.')
                      }
                    }}
                  >
                    Редагувати
                  </button>
                  <button type="button" className="btn btn-ghost" onClick={() => deleteNews(n.id)}>
                    Видалити
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}

      {tab === 'reviews' && (
        <section className="section" style={{ marginTop: 0, borderTop: 'none', paddingTop: 0 }}>
          <h2>Відгуки ({allReviews.length})</h2>
          {editingReview && (
            <form className="form" onSubmit={saveReview} style={{ marginBottom: '1.5rem' }}>
              <h3>Редагувати відгук #{editingReview.id}</h3>
              <label>
                Рейтинг (1–5)
                <input
                  type="number"
                  min={1}
                  max={5}
                  value={editingReview.rating}
                  onChange={(e) =>
                    setEditingReview({ ...editingReview, rating: Number(e.target.value) })
                  }
                />
              </label>
              <label>
                Текст
                <textarea
                  rows={3}
                  value={editingReview.text}
                  onChange={(e) => setEditingReview({ ...editingReview, text: e.target.value })}
                  required
                />
              </label>
              <label>
                Чек (грн)
                <input
                  value={editingReview.check_amount}
                  onChange={(e) =>
                    setEditingReview({ ...editingReview, check_amount: e.target.value })
                  }
                />
              </label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button type="submit" className="btn btn-primary">
                  Зберегти
                </button>
                <button type="button" className="btn btn-ghost" onClick={() => setEditingReview(null)}>
                  Скасувати
                </button>
              </div>
            </form>
          )}
          <ul className="review-list">
            {allReviews.map((r) => (
              <li key={r.id}>
                <strong>{r.user}</strong> · {r.venue_name ?? `заклад #${r.venue}`} · ★{r.rating}
                {r.check_amount && <span className="muted"> · чек {r.check_amount}</span>}
                <p>{r.text}</p>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    type="button"
                    className="btn btn-ghost"
                    onClick={() =>
                      setEditingReview({
                        id: r.id,
                        rating: r.rating,
                        text: r.text,
                        check_amount: r.check_amount ?? '',
                      })
                    }
                  >
                    Редагувати
                  </button>
                  <button type="button" className="btn btn-ghost" onClick={() => deleteReview(r.id)}>
                    Видалити
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}

      {tab === 'users' && (
        <section className="section" style={{ marginTop: 0, borderTop: 'none', paddingTop: 0 }}>
          <h2>Користувачі ({users.length})</h2>
          <ul className="review-list">
            {users.map((u) => (
              <li key={u.id}>
                <strong>{u.username}</strong> · {u.email}{' '}
                {(u.first_name || u.last_name) && (
                  <span className="muted">
                    ({[u.first_name, u.last_name].filter(Boolean).join(' ')})
                  </span>
                )}{' '}
                {!u.is_active && <span className="badge">неактивний</span>}
                <div style={{ marginTop: '0.35rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <select value={u.role} onChange={(e) => changeRole(u.id, e.target.value)}>
                    {ROLES.map((r) => (
                      <option key={r} value={r}>
                        {r}
                      </option>
                    ))}
                  </select>
                  {editUserId !== u.id && (
                    <button type="button" className="btn btn-ghost" onClick={() => startEditUser(u)}>
                      Редагувати
                    </button>
                  )}
                  {u.is_active && (
                    <button type="button" className="btn btn-ghost" onClick={() => deactivateUser(u.id)}>
                      Деактивувати
                    </button>
                  )}
                  <button type="button" className="btn btn-ghost" onClick={() => deleteUser(u.id)}>
                    Видалити
                  </button>
                </div>
                {editUserId === u.id && (
                  <form
                    className="form"
                    style={{ marginTop: '0.6rem' }}
                    onSubmit={(e) => {
                      e.preventDefault()
                      void saveUserEdit(u.id)
                    }}
                  >
                    <label>
                      Email
                      <input
                        type="email"
                        value={userEdit.email}
                        onChange={(e) => setUserEdit((s) => ({ ...s, email: e.target.value }))}
                      />
                    </label>
                    <label>
                      Ім'я
                      <input
                        value={userEdit.first_name}
                        onChange={(e) => setUserEdit((s) => ({ ...s, first_name: e.target.value }))}
                      />
                    </label>
                    <label>
                      Прізвище
                      <input
                        value={userEdit.last_name}
                        onChange={(e) => setUserEdit((s) => ({ ...s, last_name: e.target.value }))}
                      />
                    </label>
                    <label>
                      Телефон
                      <input
                        value={userEdit.phone_number}
                        onChange={(e) => setUserEdit((s) => ({ ...s, phone_number: e.target.value }))}
                      />
                    </label>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button type="submit" className="btn btn-primary">
                        Зберегти
                      </button>
                      <button type="button" className="btn btn-ghost" onClick={() => setEditUserId(null)}>
                        Скасувати
                      </button>
                    </div>
                  </form>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {tab === 'analytics' && (
        <section className="section" style={{ marginTop: 0, borderTop: 'none', paddingTop: 0 }}>
          <h2>Аналітика переглядів</h2>
          <div className="filter-row">
            <label className="filter-field">
              <span className="filter-label">ID закладу</span>
              <input
                type="number"
                value={statsVenueId}
                onChange={(e) => setStatsVenueId(e.target.value)}
              />
            </label>
            <label className="filter-field">
              <span className="filter-label">Від</span>
              <input type="date" value={statsFrom} onChange={(e) => setStatsFrom(e.target.value)} />
            </label>
            <label className="filter-field">
              <span className="filter-label">До</span>
              <input type="date" value={statsTo} onChange={(e) => setStatsTo(e.target.value)} />
            </label>
            <button type="button" className="btn btn-primary" onClick={loadStats}>
              Показати
            </button>
          </div>
          {stats && (
            <div className="stats-panel">
              <h3>{stats.venue_name}</h3>
              <p>Всього: {stats.total_views}</p>
              <p>За 7 днів: {stats.views_last_7_days}</p>
              {stats.views_in_range != null && <p>У діапазоні: {stats.views_in_range}</p>}
              <ul>
                {stats.views_by_day.map((d) => (
                  <li key={d.date} className="muted">
                    {d.date}: {d.count}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {tab === 'content' && (
        <>
          <section className="section" style={{ marginTop: 0, borderTop: 'none', paddingTop: 0 }}>
            <h2>Сторінки сайту</h2>
            <ul className="review-list">
              {pages.map((p) => (
                <li key={p.slug}>
                  <strong>{p.title}</strong> <span className="muted">/{p.slug}</span>
                  <button
                    type="button"
                    className="btn btn-ghost"
                    style={{ marginLeft: '0.5rem' }}
                    onClick={() => setEditPage({ ...p })}
                  >
                    Редагувати
                  </button>
                </li>
              ))}
            </ul>
            {editPage && (
              <form className="form" onSubmit={savePage}>
                <h3>{editPage.slug}</h3>
                <label>
                  Заголовок
                  <input
                    value={editPage.title}
                    onChange={(e) => setEditPage({ ...editPage, title: e.target.value })}
                  />
                </label>
                <label>
                  Текст
                  <textarea
                    rows={6}
                    value={editPage.content}
                    onChange={(e) => setEditPage({ ...editPage, content: e.target.value })}
                  />
                </label>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button type="submit" className="btn btn-primary">
                    Зберегти
                  </button>
                  <button type="button" className="btn btn-ghost" onClick={() => setEditPage(null)}>
                    Скасувати
                  </button>
                </div>
              </form>
            )}
          </section>
          <section className="section">
            <h2>Топ-категорії</h2>
            <ul className="review-list">
              {topCategories.map((c) => (
                <li key={c.id}>
                  {c.name} {c.tag_name && <span className="muted">· {c.tag_name}</span>}
                  <button
                    type="button"
                    className="btn btn-ghost"
                    style={{ marginLeft: '0.5rem' }}
                    onClick={async () => {
                      await cmsApi.updateTopCategory(c.id, { is_active: !c.is_active })
                      loadContent()
                    }}
                  >
                    {c.is_active ? 'Вимкнути' : 'Увімкнути'}
                  </button>
                  <button
                    type="button"
                    className="btn btn-ghost"
                    onClick={async () => {
                      if (window.confirm('Видалити?')) {
                        await cmsApi.deleteTopCategory(c.id)
                        loadContent()
                      }
                    }}
                  >
                    Видалити
                  </button>
                </li>
              ))}
            </ul>
            <div className="filter-row" style={{ marginTop: '1rem' }}>
              <label className="filter-field">
                <span className="filter-label">Назва</span>
                <input value={newCatName} onChange={(e) => setNewCatName(e.target.value)} />
              </label>
              <label className="filter-field">
                <span className="filter-label">Тег</span>
                <select value={newCatTag} onChange={(e) => setNewCatTag(e.target.value)}>
                  <option value="">—</option>
                  {tags.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name}
                    </option>
                  ))}
                </select>
              </label>
              <button type="button" className="btn btn-primary" onClick={addTopCategory}>
                Додати
              </button>
            </div>
          </section>
        </>
      )}

      <p style={{ marginTop: '2rem' }}>
        <Link to="/">← На головну</Link>
      </p>
    </div>
  )
}
