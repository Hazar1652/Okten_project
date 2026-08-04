/** Extract first email-like address from free-form contact text. */
export function extractEmail(contact: string): string | null {
  const match = contact.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i)
  return match ? match[0] : null
}

export function isLikelyTelegram(contact: string): boolean {
  const c = contact.trim().toLowerCase()
  return c.startsWith('@') || c.includes('telegram') || c.includes('t.me/')
}

export function telegramUsername(contact: string): string | null {
  const fromUrl = contact.match(/t\.me\/([A-Za-z0-9_]+)/i)
  if (fromUrl) return fromUrl[1]
  const at = contact.match(/@([A-Za-z0-9_]{3,})/)
  if (at) return at[1]
  return null
}

export function buildGmailComposeUrl(email: string, subject?: string, body?: string): string {
  const params = new URLSearchParams({ view: 'cm', fs: '1', to: email })
  if (subject) params.set('su', subject)
  if (body) params.set('body', body)
  return `https://mail.google.com/mail/?${params.toString()}`
}

export function buildOutlookComposeUrl(email: string, subject?: string, body?: string): string {
  const params = new URLSearchParams({ to: email })
  if (subject) params.set('subject', subject)
  if (body) params.set('body', body)
  return `https://outlook.live.com/mail/0/deeplink/compose?${params.toString()}`
}

export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    try {
      const el = document.createElement('textarea')
      el.value = text
      el.setAttribute('readonly', '')
      el.style.position = 'fixed'
      el.style.left = '-9999px'
      document.body.appendChild(el)
      el.select()
      const ok = document.execCommand('copy')
      document.body.removeChild(el)
      return ok
    } catch {
      return false
    }
  }
}
