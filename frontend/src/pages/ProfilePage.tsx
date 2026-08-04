import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { favoritesApi } from '../api/favorites.api'
import { reviewsApi } from '../api/reviews.api'
import { usersApi } from '../api/users.api'
import { useAuth } from '../store/authContext'
import type { Review } from '../types/api'
import { resolveMediaUrl } from '../utils/mediaUrl'

export default function ProfilePage() {
  const { user, refreshUser } = useAuth()
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [phone, setPhone] = useState('')
  const [avatarFile, setAvatarFile] = useState<File | null>(null)
  const [msg, setMsg] = useState('')
  const [favorites, setFavorites] = useState<{ id: number; venue: { id: number; name: string } }[]>(
    [],
  )
  const [myReviews, setMyReviews] = useState<Review[]>([])

  useEffect(() => {
    if (user) {
      setFirstName(user.first_name ?? '')
      setLastName(user.last_name ?? '')
      setPhone(user.phone_number ?? '')
    }
  }, [user])

  const loadFavorites = () => {
    favoritesApi
      .list()
      .then((res) => setFavorites(res.data.results))
      .catch(() => setFavorites([]))
  }

  useEffect(() => {
    loadFavorites()
    reviewsApi
      .listMine()
      .then((res) => setMyReviews(res.data.results))
      .catch(() => setMyReviews([]))
  }, [])

  const save = async (e: React.FormEvent) => {
    e.preventDefault()
    setMsg('')
    try {
      if (avatarFile) {
        const fd = new FormData()
        fd.append('first_name', firstName)
        fd.append('last_name', lastName)
        if (phone) fd.append('phone_number', phone)
        fd.append('avatar', avatarFile)
        await usersApi.updateMe(fd)
      } else {
        await usersApi.updateMe({
          first_name: firstName,
          last_name: lastName,
          phone_number: phone || null,
        })
      }
      await refreshUser()
      setAvatarFile(null)
      setMsg('Збережено.')
    } catch {
      setMsg('Не вдалося зберегти.')
    }
  }

  const removeFavorite = async (id: number) => {
    await favoritesApi.remove(id)
    loadFavorites()
  }

  if (!user) return null

  const avatarSrc = user.avatar ? resolveMediaUrl(user.avatar) : null

  return (
    <div>
      <h1>Профіль</h1>
      <p className="muted">
        {user.username} · {user.email} · роль: {user.role}
        {user.role === 'critic' && (
          <span className="badge badge-pending" style={{ marginLeft: '0.5rem' }}>
            Критик
          </span>
        )}
      </p>
      {avatarSrc && (
        <img
          src={avatarSrc}
          alt=""
          style={{ width: 72, height: 72, borderRadius: '50%', objectFit: 'cover', marginBottom: '1rem' }}
        />
      )}
      <form className="form" onSubmit={save}>
        <label>
          Ім&apos;я
          <input value={firstName} onChange={(e) => setFirstName(e.target.value)} />
        </label>
        <label>
          Прізвище
          <input value={lastName} onChange={(e) => setLastName(e.target.value)} />
        </label>
        <label>
          Телефон
          <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+380..." />
        </label>
        <label>
          Аватар
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setAvatarFile(e.target.files?.[0] ?? null)}
          />
        </label>
        {msg && <p className="muted">{msg}</p>}
        <button type="submit" className="btn btn-primary">
          Зберегти
        </button>
      </form>

      <p style={{ marginTop: '1rem' }}>
        <Link to="/manager" className="btn btn-ghost">
          Мої заклади
        </Link>
      </p>

      <section className="section">
        <h2>Мої оцінки</h2>
        {myReviews.length === 0 ? (
          <p className="muted">Ще немає оцінок.</p>
        ) : (
          <ul className="review-list">
            {myReviews.map((r) => (
              <li key={`rating-${r.id}`}>
                <Link to={`/venues/${r.venue}`}>
                  <strong>{r.venue_name ?? `Заклад #${r.venue}`}</strong>
                </Link>
                {' — '}★{r.rating}
                {r.check_amount && <span className="muted"> · чек {r.check_amount} грн</span>}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="section">
        <h2>Мої коментарі</h2>
        {myReviews.length === 0 ? (
          <p className="muted">Ще немає коментарів.</p>
        ) : (
          <ul className="review-list">
            {myReviews.map((r) => (
              <li key={`comment-${r.id}`}>
                <Link to={`/venues/${r.venue}`}>
                  <strong>{r.venue_name ?? `Заклад #${r.venue}`}</strong>
                </Link>
                <p>{r.text}</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="section">
        <h2>Улюблені</h2>
        {favorites.length === 0 ? (
          <p className="muted">Порожньо.</p>
        ) : (
          <ul className="review-list">
            {favorites.map((f) => (
              <li key={f.id} style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
                <Link to={`/venues/${f.venue.id}`}>{f.venue.name}</Link>
                <button type="button" className="btn btn-ghost" onClick={() => removeFavorite(f.id)}>
                  Прибрати
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
