import api from './axiosInstance'
import type { PaginatedResponse } from '../types/api'

export interface Complaint {
  id: number
  review: number
  author: string
  reason: string
  status: string
  created_at: string
  updated_at: string
}

export const complaintsApi = {
  list: () => api.get<PaginatedResponse<Complaint>>('/complaints/'),
  create: (review: number, reason: string) =>
    api.post<Complaint>('/complaints/', { review, reason }),
  updateStatus: (id: number, status: string) =>
    api.patch<Complaint>(`/complaints/${id}/`, { status }),
}
