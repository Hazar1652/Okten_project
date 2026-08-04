import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { messagingApi } from '../api/messaging.api'
import ChatThread from '../components/ChatThread'
import type { Conversation } from '../types/api'
import { apiErrorMessage } from '../utils/apiError'

export default function MessagesPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const selectedId = id ? Number(id) : null
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(() => {
    setLoading(true)
    messagingApi
      .list()
      .then(({ data }) => setConversations(data))
      .catch((err) => setError(apiErrorMessage(err, 'Не вдалося завантажити діалоги.')))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    const timer = window.setInterval(() => {
      messagingApi
        .list()
        .then(({ data }) => setConversations(data))
        .catch(() => {
          /* ignore */
        })
    }, 8000)
    return () => window.clearInterval(timer)
  }, [])

  const selected =
    selectedId && !Number.isNaN(selectedId)
      ? conversations.find((c) => c.id === selectedId)
      : undefined

  return (
    <div className="messages-page">
      <h1>Повідомлення</h1>
      <p className="muted">Чат із менеджерами закладів і авторами зустрічей «Пиячок».</p>
      {error && <p className="error">{error}</p>}

      <div className="messages-layout">
        <aside className="messages-list">
          {loading && <p className="muted">Завантаження...</p>}
          {!loading && conversations.length === 0 && (
            <p className="muted">Немає діалогів. Напишіть зі сторінки закладу або пиячка.</p>
          )}
          {conversations.map((c) => (
            <button
              key={c.id}
              type="button"
              className={`messages-item ${selectedId === c.id ? 'active' : ''}`}
              onClick={() => navigate(`/messages/${c.id}`)}
            >
              <div className="messages-item-title">
                {c.title}
                {c.unread_count > 0 && <span className="nav-unread">{c.unread_count}</span>}
              </div>
              <div className="muted messages-item-preview">
                {c.peer ? `з ${c.peer.username}` : ''}
                {c.last_message ? ` · ${c.last_message.body.slice(0, 60)}` : ' · немає повідомлень'}
              </div>
            </button>
          ))}
        </aside>

        <section className="messages-thread">
          {selectedId && !Number.isNaN(selectedId) ? (
            <>
              <div className="messages-thread-header">
                <h2>{selected?.title ?? `Діалог #${selectedId}`}</h2>
                {selected?.peer && <p className="muted">Співрозмовник: {selected.peer.username}</p>}
                {selected?.venue && (
                  <p className="muted">
                    <Link to={`/venues/${selected.venue}`}>Відкрити заклад</Link>
                  </p>
                )}
                {selected?.hangout && (
                  <p className="muted">
                    <Link to="/hangout">До пиячка</Link>
                  </p>
                )}
              </div>
              <ChatThread conversationId={selectedId} />
            </>
          ) : (
            <p className="muted">Оберіть діалог зліва або почніть новий зі сторінки закладу.</p>
          )}
        </section>
      </div>
    </div>
  )
}
