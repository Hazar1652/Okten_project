import { useEffect, useRef, useState } from 'react'
import { messagingApi } from '../api/messaging.api'
import { useAuth } from '../store/authContext'
import type { ChatMessage } from '../types/api'
import { apiErrorMessage } from '../utils/apiError'

const POLL_MS = 4000

interface Props {
  conversationId: number
}

export default function ChatThread({ conversationId }: Props) {
  const { user } = useAuth()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [body, setBody] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef<HTMLDivElement | null>(null)
  const lastIdRef = useRef<number | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')
    setMessages([])
    lastIdRef.current = null

    messagingApi
      .messages(conversationId)
      .then(({ data }) => {
        if (cancelled) return
        setMessages(data)
        lastIdRef.current = data.length ? data[data.length - 1].id : null
        void messagingApi.markRead(conversationId)
      })
      .catch((err) => {
        if (!cancelled) setError(apiErrorMessage(err, 'Не вдалося завантажити чат.'))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [conversationId])

  useEffect(() => {
    const timer = window.setInterval(() => {
      const afterId = lastIdRef.current ?? undefined
      messagingApi
        .messages(conversationId, afterId)
        .then(({ data }) => {
          if (!data.length) return
          setMessages((prev) => {
            const known = new Set(prev.map((m) => m.id))
            const fresh = data.filter((m) => !known.has(m.id))
            if (!fresh.length) return prev
            return [...prev, ...fresh]
          })
          lastIdRef.current = data[data.length - 1].id
          void messagingApi.markRead(conversationId)
        })
        .catch(() => {
          /* ignore poll errors */
        })
    }, POLL_MS)
    return () => window.clearInterval(timer)
  }, [conversationId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const doSend = async () => {
    const text = body.trim()
    if (!text || sending) return
    setSending(true)
    setError('')
    try {
      const { data } = await messagingApi.send(conversationId, text)
      setMessages((prev) => (prev.some((m) => m.id === data.id) ? prev : [...prev, data]))
      lastIdRef.current = data.id
      setBody('')
    } catch (err) {
      setError(apiErrorMessage(err, 'Не вдалося надіслати.'))
    } finally {
      setSending(false)
    }
  }

  const send = async (e: React.FormEvent) => {
    e.preventDefault()
    await doSend()
  }

  return (
    <div className="chat-thread">
      <div className="chat-messages">
        {loading && <p className="muted">Завантаження...</p>}
        {!loading && messages.length === 0 && (
          <p className="muted">Поки що немає повідомлень. Напишіть першим.</p>
        )}
        {messages.map((m) => {
          const mine = user?.id === m.sender_id || user?.username === m.sender
          return (
            <div key={m.id} className={`chat-bubble ${mine ? 'chat-bubble-mine' : ''}`}>
              <div className="chat-bubble-meta">
                {m.sender} · {new Date(m.created_at).toLocaleString('uk-UA')}
              </div>
              <div className="chat-bubble-body">{m.body}</div>
            </div>
          )
        })}
        <div ref={bottomRef} />
      </div>
      {error && <p className="error">{error}</p>}
      <form
        className="chat-compose"
        onSubmit={send}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            void doSend()
          }
        }}
      >
        <label className="chat-compose-field">
          <span className="visually-hidden">Текст повідомлення</span>
          <textarea
            className="chat-compose-input"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Напишіть повідомлення…"
            maxLength={2000}
            rows={2}
            required
          />
        </label>
        <button type="submit" className="btn btn-primary chat-compose-send" disabled={sending || !body.trim()}>
          {sending ? '…' : 'Надіслати'}
        </button>
      </form>
    </div>
  )
}
