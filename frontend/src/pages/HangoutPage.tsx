import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { hangoutApi } from '../api/hangout.api'
import { messagingApi } from '../api/messaging.api'
import { venuesApi } from '../api/venues.api'
import EmailContactActions from '../components/EmailContactActions'
import MeetingDateTimePicker from '../components/MeetingDateTimePicker'
import { useAuth } from '../store/authContext'
import type { Hangout, Venue } from '../types/api'
import { apiErrorMessage } from '../utils/apiError'

/** Локальна дата у форматі YYYY-MM-DD для значення за замовчуванням. */
function localDateStr(d = new Date()): string {
  const tzOffset = d.getTimezoneOffset() * 60000
  return new Date(d.getTime() - tzOffset).toISOString().slice(0, 10)
}

export default function HangoutPage() {
  const { isAuthenticated, user } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const preselectVenue = searchParams.get('venue')
  const [open, setOpen] = useState<Hangout[]>([])
  const [mine, setMine] = useState<Hangout[]>([])
  const [venues, setVenues] = useState<Venue[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [msg, setMsg] = useState('')
  const [warnings, setWarnings] = useState<string[]>([])
  const [chatBusyId, setChatBusyId] = useState<number | null>(null)

  const today = localDateStr()
  const [venueId, setVenueId] = useState('')
  const [date, setDate] = useState(today)
  const [time, setTime] = useState('19:00')
  const [goal, setGoal] = useState('')
  const [contact, setContact] = useState('')
  const [gender, setGender] = useState('будь-які')
  const [people, setPeople] = useState(2)
  const [payer, setPayer] = useState('split')
  const [budgetMin, setBudgetMin] = useState('')
  const [budgetMax, setBudgetMax] = useState('')

  const load = useCallback(() => {
    setLoading(true)
    const promises: Promise<unknown>[] = [hangoutApi.listOpen(), venuesApi.list()]
    if (isAuthenticated) promises.push(hangoutApi.listMine())
    Promise.all(promises)
      .then(([openRes, venuesRes, mineRes]) => {
        setOpen((openRes as { data: { results: Hangout[] } }).data.results)
        const published = (venuesRes as { data: { results: Venue[] } }).data.results.filter(
          (v) => v.status === 'published',
        )
        setVenues(published)
        setMine((mineRes as { data: { results: Hangout[] } } | undefined)?.data.results ?? [])
      })
      .finally(() => setLoading(false))
  }, [isAuthenticated])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    if (user?.email) setContact(user.email)
  }, [user])

  useEffect(() => {
    if (preselectVenue && venues.some((v) => v.id === Number(preselectVenue))) {
      setVenueId(preselectVenue)
      setShowForm(true)
    }
  }, [preselectVenue, venues])

  const createHangout = async (e: React.FormEvent) => {
    e.preventDefault()
    setMsg('')
    setWarnings([])
    const meetingDate = `${date}T${time}:00`
    if (new Date(meetingDate).getTime() < Date.now()) {
      setMsg('Оберіть дату й час у майбутньому.')
      return
    }
    try {
      const { data } = await hangoutApi.create({
        venue: Number(venueId),
        meeting_date: meetingDate,
        meeting_time: time.length === 5 ? `${time}:00` : time,
        goal_description: goal,
        contact_me: contact,
        gender_preferences: gender,
        people_count: people,
        payer_type: payer,
        budget_min: budgetMin.trim() || undefined,
        budget_max: budgetMax.trim() || undefined,
      })
      if (data.warnings?.length) setWarnings(data.warnings)
      setMsg('Зустріч створено!')
      setShowForm(false)
      load()
    } catch (err: unknown) {
      setMsg(apiErrorMessage(err, 'Не вдалося створити зустріч.'))
    }
  }

  const cancelHangout = async (id: number) => {
    try {
      await hangoutApi.cancel(id)
      load()
    } catch {
      setMsg('Не вдалося скасувати.')
    }
  }

  const openHangoutChat = async (hangoutId: number) => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    setMsg('')
    setChatBusyId(hangoutId)
    try {
      const { data } = await messagingApi.create({
        kind: 'hangout',
        hangout_id: hangoutId,
      })
      navigate(`/messages/${data.id}`)
    } catch (err) {
      setMsg(apiErrorMessage(err, 'Не вдалося відкрити чат.'))
    } finally {
      setChatBusyId(null)
    }
  }

  const renderCard = (h: Hangout, showCancel = false) => (
    <article key={h.id} className="card">
      <h2>
        <Link to={`/venues/${h.venue}`}>{h.venue_name}</Link>
      </h2>
      <p>{h.goal_description}</p>
      <p className="muted">
        {new Date(h.meeting_date).toLocaleString('uk-UA')} · {h.people_count} осіб · {h.status}
        {h.budget_min && ` · бюджет від ${h.budget_min} грн`}
        {h.budget_max && ` до ${h.budget_max} грн`}
      </p>
      <p className="muted">Автор: {h.author}</p>
      {h.contact_me && (
        <EmailContactActions
          contact={h.contact_me}
          subject={`Пиячок: ${h.venue_name}`}
          body={`Привіт! Пишу щодо зустрічі в «${h.venue_name}» (${new Date(h.meeting_date).toLocaleString('uk-UA')}).`}
        />
      )}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
        {isAuthenticated && user?.username !== h.author && h.status === 'open' && (
          <button
            type="button"
            className="btn btn-primary"
            disabled={chatBusyId === h.id}
            onClick={() => void openHangoutChat(h.id)}
          >
            Написати в чат
          </button>
        )}
        {!isAuthenticated && h.status === 'open' && (
          <Link to="/login" className="btn btn-ghost">
            Увійти, щоб написати
          </Link>
        )}
        {showCancel && h.status === 'open' && (
          <button type="button" className="btn btn-ghost" onClick={() => cancelHangout(h.id)}>
            Скасувати
          </button>
        )}
      </div>
    </article>
  )

  return (
    <div>
      <h1>Пиячок</h1>
      <div className="safety-banner">
        <strong>Безпека:</strong> зустрічайтесь у перевірених закладах, не йдіть у незнайомі місця з
        незнайомцями. Повідомте близьких про плани.
      </div>
      <p className="muted">Знайди компанію для походу в заклад або створи свою зустріч.</p>

      {isAuthenticated ? (
        <button type="button" className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Закрити форму' : '+ Створити зустріч'}
        </button>
      ) : (
        <p className="muted">
          <Link to="/login">Увійди</Link>, щоб створити зустріч.
        </p>
      )}

      {showForm && isAuthenticated && (
        <form className="form section" onSubmit={createHangout}>
          <label>
            Заклад *
            <select value={venueId} onChange={(e) => setVenueId(e.target.value)} required>
              <option value="">Оберіть заклад</option>
              {venues.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name}
                </option>
              ))}
            </select>
          </label>
          <MeetingDateTimePicker
            date={date}
            time={time}
            onDateChange={setDate}
            onTimeChange={setTime}
          />
          <label>
            Мета зустрічі *
            <textarea rows={3} value={goal} onChange={(e) => setGoal(e.target.value)} required />
          </label>
          <label>
            Як зв&apos;язатись *
            <input value={contact} onChange={(e) => setContact(e.target.value)} required />
          </label>
          <label>
            Кого шукаєш
            <input value={gender} onChange={(e) => setGender(e.target.value)} />
          </label>
          <label>
            Кількість людей
            <input
              type="number"
              min={1}
              max={30}
              value={people}
              onChange={(e) => setPeople(Number(e.target.value))}
            />
          </label>
          <label>
            Хто платить
            <select value={payer} onChange={(e) => setPayer(e.target.value)}>
              <option value="me">Я</option>
              <option value="split">Навпіл</option>
              <option value="other">Інше</option>
            </select>
          </label>
          <label>
            Бюджет від (грн)
            <input
              type="number"
              min={0}
              value={budgetMin}
              onChange={(e) => setBudgetMin(e.target.value)}
              placeholder="необовʼязково"
            />
          </label>
          <label>
            Бюджет до (грн)
            <input
              type="number"
              min={0}
              value={budgetMax}
              onChange={(e) => setBudgetMax(e.target.value)}
              placeholder="необовʼязково"
            />
          </label>
          <button type="submit" className="btn btn-primary">
            Опублікувати
          </button>
        </form>
      )}

      {msg && <p className="muted">{msg}</p>}
      {warnings.length > 0 && (
        <ul className="warnings">
          {warnings.map((w) => (
            <li key={w}>{w}</li>
          ))}
        </ul>
      )}

      {loading && <p className="muted">Завантаження...</p>}

      <section className="section">
        <h2>Відкриті зустрічі</h2>
        <div className="card-grid">{open.map((h) => renderCard(h))}</div>
        {!loading && open.length === 0 && <p className="muted">Немає відкритих зустрічей.</p>}
      </section>

      {isAuthenticated && (
        <section className="section">
          <h2>Мої зустрічі</h2>
          <div className="card-grid">{mine.map((h) => renderCard(h, true))}</div>
          {mine.length === 0 && !loading && <p className="muted">Ти ще не створював зустрічей.</p>}
        </section>
      )}
    </div>
  )
}
