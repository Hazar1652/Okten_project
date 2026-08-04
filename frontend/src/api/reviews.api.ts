import api from './axiosInstance'
import type { PaginatedResponse, Review } from '../types/api'

export interface CreateReviewPayload {
  venue: number
  rating: number
  text: string
  check_amount?: string
}

export const reviewsApi = {
  list: (params?: Record<string, string | number>) =>
    api.get<PaginatedResponse<Review>>('/reviews/', { params }),
  listMine: () => api.get<PaginatedResponse<Review>>('/reviews/', { params: { mine: 1 } }),
  create: (data: CreateReviewPayload) => api.post<Review>('/reviews/', data),
  update: (id: number, data: Partial<Omit<CreateReviewPayload, 'venue'> & { venue?: number }>) =>
    api.patch<Review>(`/reviews/${id}/`, data),
  delete: (id: number) => api.delete(`/reviews/${id}/`),
}
