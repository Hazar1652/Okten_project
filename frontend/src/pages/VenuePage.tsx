import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { complaintsApi } from '../api/complaints.api'
import { favoritesApi } from '../api/favorites.api'
import { messagingApi } from '../api/messaging.api'
import { newsApi } from '../api/news.api'
import { reviewsApi } from '../api/reviews.api'
import { venuesApi } from '../api/venues.api'
import { useAuth } from '../store/authContext'
import type { NewsItem, Review, Venue } from '../types/api'
import VenueLocationMap from '../components/VenueLocationMap'
import {
  buildGmailComposeUrl,
  buildOutlookComposeUrl,
  copyToClipboard,
} from '../utils/emailContact'
import { apiErrorMessage } from '../utils/apiError'
import { buildMapsDirectionsUrl } from '../utils/maps'
import { resolveMediaUrl } from '../utils/mediaUrl'
import { venueTypeLabel } from '../utils/venueTypes'
import { formatWorkTime } from '../utils/workTime'

export default function VenuePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const venueId = Number(id)
  const { isAuthenticated, isSuperAdmin, user } = useAuth()

  const [venue, setVenue] = useState<Venue | null>(null)
  const [reviews, setReviews] = useState<Review[]>([])
  const [venueNews, setVenueNews] = useState<NewsItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [favoriteMsg, setFavoriteMsg] = useState('')

  const [rating, setRating] = useState(5)
  const [text, setText] = useState('')
  const [checkAmount, setCheckAmount] = useState('')
  const [reviewError, setReviewError] = useState('')
  const [complaintReviewId, setComplaintReviewId] = useState<number | null>(null)
  const [complaintReason, setComplaintReason] = useState('')
  const [complaintMsg, setComplaintMsg] = useState('')
  const [managerMsg, setManagerMsg] = useState('')
  const [managerNote, setManagerNote] = useState('')
  const [chatBusy, setChatBusy] = useState(false)

  useEffect(() => {
    if (!venueId || Number.isNaN(venueId)) return
    setVenue(null)
    setReviews([])
    setVenueNews([])
    setError('')
    setReviewError('')
    setLoading(true)
    Promise.all([
      venuesApi.get(venueId),
      reviewsApi.list({ venue: venueId }),
      newsApi.list({ venue: venueId }),
    ])
      .then(([v, r, n]) => {
        setVenue(v.data)
        setReviews(r.data.results)
        setVenueNews(n.data.results)
      })
      .catch(() => setError('Заклад не знайдено.'))
      .finally(() => setLoading(false))
  }, [venueId])

  const mapsUrl = venue ? buildMapsDirectionsUrl(venue) : null
  const workHours = venue ? formatWorkTime(venue.work_time) : null

  const openManagerChat = async (withNote = false) => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    setManagerMsg('')
    setChatBusy(true)
    try {
      const { data: conversation } = await messagingApi.create({
        kind: 'venue',
        venue_id: venueId,
      })
      const note = managerNote.trim()
      if (withNote && note) {
        await messagingApi.send(conversation.id, note)
        setManagerNote('')
      }
      navigate(`/messages/${conversation.id}`)
    } catch (err) {
      setManagerMsg(apiErrorMessage(err, 'Не вдалося відкрити чат.'))
    } finally {
      setChatBusy(false)
    }
  }

  const submitManagerMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    await openManagerChat(true)
  }

  const addFavorite = async () => {
    setFavoriteMsg('')
    try {
      await favoritesApi.add(venueId)
      setFavoriteMsg('Додано в улюблені!')
    } catch {
      setFavoriteMsg('Не вдалося (можливо вже в улюблених).')
    }
  }

  const submitComplaint = async (e: React.FormEvent) => {
    e.preventDefault()
    if (complaintReviewId == null) return
    setComplaintMsg('')
    try {
      await complaintsApi.create(complaintReviewId, complaintReason)
      setComplaintMsg('Скаргу надіслано.')
      setComplaintReviewId(null)
      setComplaintReason('')
    } catch {
      setComplaintMsg('Не вдалося надіслати скаргу.')
    }
  }

  const submitReview = async (e: React.FormEvent) => {
    e.preventDefault()
    setReviewError('')
    try {
      const payload: { venue: number; rating: number; text: string; check_amount?: string } = {
        venue: venueId,
        rating,
        text,
      }
      if (checkAmount.trim()) {
        payload.check_amount = checkAmount.trim()
      }
      await reviewsApi.create(payload)
      const { data } = await reviewsApi.list({ venue: venueId })
      setReviews(data.results)
      setText('')
      setCheckAmount('')
    } catch (err: unknown) {
      const data = (err as { response?: { data?: { non_field_errors?: string[] } } })?.response
        ?.data
      setReviewError(data?.non_field_errors?.[0] ?? 'Помилка відгуку.')
    }
  }

  if (loading) return <p className="muted">Завантаження...</p>
  if (error || !venue) return <p className="error">{error || 'Помилка'}</p>

  const coverSrc = resolveMediaUrl(venue.main_image_url)
  // За ТЗ скаргу на відгук залишають лише адміни або власник закладу (ресторатор).
  const canComplain = isSuperAdmin || user?.username === venue.owner

  return (
    <div className="venue-detail">
      <p>
        <Link to="/">← Каталог</Link>
      </p>
      {coverSrc && (
        <img src={coverSrc} alt="" className="venue-detail-cover" />
      )}
      <h1>{venue.name}</h1>
      {venue.tags && venue.tags.length > 0 && (
        <div className="card-tags" style={{ marginBottom: '0.75rem' }}>
          {venue.tags.map((t) => (
            <Link key={t.id} to={`/?tag=${t.id}#catalog`} className="badge badge-link">
              {t.name}
            </Link>
          ))}
        </div>
      )}
      {venue.features && venue.features.length > 0 && (
        <div className="card-tags" style={{ marginBottom: '0.75rem' }}>
          {venue.features.map((f) => (
            <span key={f.id} className="badge badge-published">
              {f.name}
            </span>
          ))}
        </div>
      )}
      <div className="meta">
        {venue.venue_type && <span>{venueTypeLabel(venue.venue_type)}</span>}
        <span>{venue.address}</span>
        {workHours && <span>🕐 {workHours}</span>}
        {venue.rating_avg != null && <span>★ {venue.rating_avg.toFixed(1)}</span>}
        {venue.avg_check && <span>~{venue.avg_check} грн</span>}
        {venue.phone_number && <span>📞 {venue.phone_number}</span>}
        {venue.email && <span>✉ {venue.email}</span>}
        {venue.website && (
          <a href={venue.website} target="_blank" rel="noreferrer">
            Сайт
          </a>
        )}
      </div>
      {venue.description && <p>{venue.description}</p>}

      <VenueLocationMap latitude={venue.latitude} longitude={venue.longitude} label="Розташування" />

      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '1rem' }}>
        {mapsUrl && (
          <a href={mapsUrl} target="_blank" rel="noreferrer" className="btn btn-primary">
            Маршрут (Google Maps)
          </a>
        )}
        {isAuthenticated && (
          <>
            <button type="button" className="btn btn-ghost" onClick={addFavorite}>
              В улюблені
            </button>
            <Link to={`/hangout?venue=${venueId}`} className="btn btn-ghost">
              Пиячок тут
            </Link>
          </>
        )}
      </div>
      {favoriteMsg && <p className="muted">{favoriteMsg}</p>}

      <section className="section contact-section">
        <h2>Контакти та повідомлення</h2>
        <p className="muted">
          Питання або скарга щодо закладу — напишіть менеджеру в чаті Okten. Email залишається як
          запасний канал.
        </p>
        {isAuthenticated && user?.username !== venue.owner ? (
          <div style={{ marginBottom: '0.85rem' }}>
            <button
              type="button"
              className="btn btn-primary"
              disabled={chatBusy}
              onClick={() => void openManagerChat(false)}
            >
              Написати менеджеру в чат
            </button>
          </div>
        ) : !isAuthenticated ? (
          <p className="muted" style={{ marginBottom: '0.85rem' }}>
            <Link to="/login">Увійди</Link>, щоб написати менеджеру в чаті.
          </p>
        ) : (
          <p className="muted" style={{ marginBottom: '0.85rem' }}>
            Це ваш заклад — відповіді на повідомлення дивіться в розділі «Повідомлення».
          </p>
        )}
        {venue.email && (
          <p className="contact-actions" style={{ marginBottom: '0.75rem' }}>
            <span className="muted">✉ {venue.email}</span>
            <span className="contact-actions-btns">
              <button
                type="button"
                className="btn btn-ghost"
                onClick={async () => {
                  const ok = await copyToClipboard(venue.email)
                  setManagerMsg(ok ? 'Email скопійовано.' : 'Не вдалося скопіювати.')
                }}
              >
                Копіювати
              </button>
              <a
                className="btn btn-ghost"
                href={buildGmailComposeUrl(venue.email)}
                target="_blank"
                rel="noreferrer"
              >
                Gmail
              </a>
              <a
                className="btn btn-ghost"
                href={buildOutlookComposeUrl(venue.email)}
                target="_blank"
                rel="noreferrer"
              >
                Outlook
              </a>
            </span>
          </p>
        )}
        {isAuthenticated && user?.username !== venue.owner && (
          <form className="form" onSubmit={submitManagerMessage}>
            <label>
              Перше повідомлення менеджеру
              <textarea
                rows={3}
                value={managerNote}
                onChange={(e) => setManagerNote(e.target.value)}
                placeholder="Питання, бронювання, скарга…"
                required
              />
            </label>
            {managerMsg && <p className="muted">{managerMsg}</p>}
            <button type="submit" className="btn btn-ghost" disabled={chatBusy}>
              Надіслати в чат
            </button>
          </form>
        )}
        {managerMsg && user?.username === venue.owner && <p className="muted">{managerMsg}</p>}
      </section>

      {venueNews.length > 0 && (
        <section className="section">
          <h2>Новини закладу</h2>
          <ul className="review-list">
            {venueNews.map((n) => (
              <li key={n.id}>
                <Link to={`/news/${n.id}`}>
                  <strong>{n.title}</strong>
                </Link>
                <span className="muted"> · {n.category}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="section">
        <h2>Відгуки ({reviews.length})</h2>
        <ul className="review-list">
          {reviews.map((r) => (
            <li key={r.id}>
              <strong>{r.user}</strong>
              {r.author_role === 'critic' && (
                <span className="badge badge-pending" style={{ marginLeft: '0.35rem' }}>
                  Критик
                </span>
              )}
              {' — '}★{r.rating}
              {r.check_amount && <span className="muted"> · чек {r.check_amount} грн</span>}
              <p>{r.text}</p>
              {canComplain && complaintReviewId !== r.id && (
                <button
                  type="button"
                  className="btn btn-ghost"
                  style={{ marginTop: '0.5rem' }}
                  onClick={() => setComplaintReviewId(r.id)}
                  title="Поскаржитись на нечесний або оманливий відгук"
                >
                  Поскаржитись
                </button>
              )}
            </li>
          ))}
        </ul>
        {reviews.length === 0 && <p className="muted">Ще немає відгуків.</p>}

        {complaintReviewId != null && canComplain && (
          <form className="form" onSubmit={submitComplaint} style={{ marginTop: '1rem' }}>
            <h3>Скарга на відгук #{complaintReviewId}</h3>
            <label>
              Причина
              <textarea
                rows={2}
                value={complaintReason}
                onChange={(e) => setComplaintReason(e.target.value)}
                required
              />
            </label>
            {complaintMsg && <p className="muted">{complaintMsg}</p>}
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button type="submit" className="btn btn-primary">
                Надіслати скаргу
              </button>
              <button
                type="button"
                className="btn btn-ghost"
                onClick={() => setComplaintReviewId(null)}
              >
                Скасувати
              </button>
            </div>
          </form>
        )}

        {isAuthenticated ? (
          <form className="form" onSubmit={submitReview} style={{ marginTop: '1rem' }}>
            <h3>Залишити відгук</h3>
            <label>
              Оцінка (1–5)
              <input
                type="number"
                min={1}
                max={5}
                value={rating}
                onChange={(e) => setRating(Number(e.target.value))}
              />
            </label>
            <label>
              Текст
              <textarea rows={3} value={text} onChange={(e) => setText(e.target.value)} required />
            </label>
            <label>
              Сума чека (грн), необовʼязково
              <input
                type="number"
                min={0}
                step="0.01"
                value={checkAmount}
                onChange={(e) => setCheckAmount(e.target.value)}
                placeholder="напр. 450"
              />
            </label>
            {reviewError && <p className="error">{reviewError}</p>}
            <button type="submit" className="btn btn-primary">
              Надіслати
            </button>
          </form>
        ) : (
          <p className="muted">
            <Link to="/login">Увійди</Link>, щоб залишити відгук.
          </p>
        )}
      </section>
    </div>
  )
}
