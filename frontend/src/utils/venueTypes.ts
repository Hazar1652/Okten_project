export const VENUE_TYPES = [
  { value: 'bar', label: 'Бар' },
  { value: 'pub', label: 'Паб' },
  { value: 'restaurant', label: 'Ресторан' },
  { value: 'cafe', label: 'Кафе' },
  { value: 'coffee', label: "Кав'ярня" },
  { value: 'club', label: 'Нічний клуб' },
  { value: 'other', label: 'Інше' },
] as const

export function venueTypeLabel(value?: string | null): string {
  return VENUE_TYPES.find((t) => t.value === value)?.label ?? ''
}
