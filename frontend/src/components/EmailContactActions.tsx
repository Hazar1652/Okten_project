import { useState } from 'react'
import {
  buildGmailComposeUrl,
  buildOutlookComposeUrl,
  copyToClipboard,
  extractEmail,
  isLikelyTelegram,
  telegramUsername,
} from '../utils/emailContact'

interface Props {
  contact: string
  subject?: string
  body?: string
}

export default function EmailContactActions({ contact, subject, body }: Props) {
  const [copied, setCopied] = useState(false)
  const email = extractEmail(contact)
  const tg = isLikelyTelegram(contact) ? telegramUsername(contact) : null

  if (!email && !tg) {
    return <span className="muted">Контакт: {contact}</span>
  }

  const onCopy = async () => {
    if (!email) return
    const ok = await copyToClipboard(email)
    if (ok) {
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="contact-actions">
      <span className="muted">Контакт: {contact}</span>
      <span className="contact-actions-btns">
        {email && (
          <>
            <button type="button" className="btn btn-ghost" onClick={onCopy}>
              {copied ? 'Скопійовано' : 'Копіювати email'}
            </button>
            <a
              className="btn btn-ghost"
              href={buildGmailComposeUrl(email, subject, body)}
              target="_blank"
              rel="noreferrer"
            >
              Gmail
            </a>
            <a
              className="btn btn-ghost"
              href={buildOutlookComposeUrl(email, subject, body)}
              target="_blank"
              rel="noreferrer"
            >
              Outlook
            </a>
          </>
        )}
        {tg && (
          <a
            className="btn btn-ghost"
            href={`https://t.me/${tg}`}
            target="_blank"
            rel="noreferrer"
          >
            Telegram
          </a>
        )}
      </span>
    </div>
  )
}
