import api from './axiosInstance'
import type { Hangout, PaginatedResponse } from '../types/api'

export interface CreateHangoutPayload {
  venue: number
  meeting_date: string
  meeting_time: string
  goal_description: string
  contact_me: string
  gender_preferences: string
  people_count: number
  payer_type: string
  budget_min?: string
  budget_max?: string
}

export const hangoutApi = {
  listOpen: (params?: Record<string, string | number>) =>
    api.get<PaginatedResponse<Hangout>>('/hangouts/', { params: { scope: 'open', ...params } }),
  listMine: () => api.get<PaginatedResponse<Hangout>>('/hangouts/', { params: { scope: 'mine' } }),
  create: (data: CreateHangoutPayload) => api.post<Hangout>('/hangouts/', data),
  cancel: (id: number) => api.post<Hangout>(`/hangouts/${id}/cancel/`),
}
