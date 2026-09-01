import type { User } from '../types/api'

export function displayName(user: Pick<User, 'username' | 'email' | 'first_name' | 'last_name'> | null | undefined): string {
  if (!user) return ''
  const full = [user.first_name, user.last_name].filter(Boolean).join(' ').trim()
  if (full) return full
  if (user.username && !/^\d+$/.test(user.username) && !/^fb_\d+$/.test(user.username)) {
    return user.username
  }
  if (user.email?.includes('@')) return user.email.split('@')[0]
  return user.username || user.email || 'Профіль'
}
