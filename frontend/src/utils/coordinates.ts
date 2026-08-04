/** 6 знаків після коми — як у БД (max 9 digits). */
export function formatCoordinate(value: string | number): string {
  const n = typeof value === 'number' ? value : Number.parseFloat(value)
  if (Number.isNaN(n)) return ''
  return n.toFixed(6)
}
