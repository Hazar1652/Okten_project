import type { Venue } from '../types/api'

export function buildMapsDirectionsUrl(venue: Pick<Venue, 'name' | 'address' | 'latitude' | 'longitude'>): string {
  const label = `${venue.name}, ${venue.address}`.trim()
  if (label.replace(/,/g, '').length > 0) {
    return `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(label)}`
  }
  return `https://www.google.com/maps/dir/?api=1&destination=${venue.latitude},${venue.longitude}`
}
