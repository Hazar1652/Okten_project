import api from './axiosInstance'

export interface VenueStats {
  venue_id: number
  venue_name: string
  total_views: number
  views_last_7_days: number
  views_in_range?: number
  date_from?: string | null
  date_to?: string | null
  views_by_day: { date: string; count: number }[]
}

export const analyticsApi = {
  venueStats: (venueId: number, params?: { from?: string; to?: string }) =>
    api.get<VenueStats>(`/analytics/venues/${venueId}/stats/`, { params }),
}
