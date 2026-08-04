const STATUS_LABELS: Record<string, string> = {
  pending: 'На модерації',
  published: 'Опубліковано',
  rejected: 'Відхилено',
  archived: 'В архіві',
}

export function venueStatusLabel(status: string): string {
  return STATUS_LABELS[status] ?? status
}

export function venueStatusBadgeClass(status: string): string {
  if (status === 'published') return 'badge-published'
  if (status === 'rejected') return 'badge-rejected'
  if (status === 'archived') return 'badge'
  return 'badge-pending'
}

export function canSubmitVenueForModeration(status: string): boolean {
  return status === 'rejected' || status === 'archived'
}
