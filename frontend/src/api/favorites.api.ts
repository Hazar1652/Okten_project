import api from './axiosInstance'
import type { PaginatedResponse, Venue } from '../types/api'

export interface Favorite {
  id: number
  venue: Venue
  created_at: string
}

export const favoritesApi = {
  list: () => api.get<PaginatedResponse<Favorite>>('/favorites/'),
  add: (venue_id: number) => api.post<Favorite>('/favorites/', { venue_id }),
  remove: (id: number) => api.delete(`/favorites/${id}/`),
}
