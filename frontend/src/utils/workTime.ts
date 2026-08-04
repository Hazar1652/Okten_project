export function formatWorkTime(workTime: Record<string, unknown> | null | undefined): string | null {
  if (!workTime || Object.keys(workTime).length === 0) return null
  if (typeof workTime.display === 'string' && workTime.display.trim()) {
    return workTime.display.trim()
  }
  if (typeof workTime.schedule === 'string' && workTime.schedule.trim()) {
    return workTime.schedule.trim()
  }
  return Object.entries(workTime)
    .map(([key, value]) => `${key}: ${String(value)}`)
    .join(' · ')
}

export function workTimeToDisplay(workTime: Record<string, unknown> | null | undefined): string {
  return formatWorkTime(workTime) ?? ''
}

export function displayToWorkTime(display: string): Record<string, string> {
  const trimmed = display.trim()
  return trimmed ? { display: trimmed } : {}
}
