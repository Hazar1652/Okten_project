export function resolveMediaUrl(url: string | null | undefined): string | null {
  if (!url) return null
  if (url.startsWith('http://') || url.startsWith('https://')) {
    try {
      const parsed = new URL(url)
      if (import.meta.env.DEV && parsed.hostname === '127.0.0.1') {
        return `${parsed.pathname}${parsed.search}`
      }
    } catch {
      return url
    }
    return url
  }
  return url.startsWith('/') ? url : `/${url}`
}
