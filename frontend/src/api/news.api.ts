import api from './axiosInstance'
import type { NewsItem, PaginatedResponse } from '../types/api'

export interface CreateNewsPayload {
  venue: number
  title: string
  content: string
  category: string
  is_paid?: boolean
  published_at?: string | null
}

function appendNewsFields(fd: FormData, data: Partial<CreateNewsPayload>) {
  Object.entries(data).forEach(([key, value]) => {
    if (value === undefined || value === null) return
    if (typeof value === 'boolean') {
      fd.append(key, value ? 'true' : 'false')
      return
    }
    fd.append(key, String(value))
  })
}

export const newsApi = {
  list: (params?: Record<string, string | number>) =>
    api.get<PaginatedResponse<NewsItem>>('/news/', { params }),
  get: (id: number) => api.get<NewsItem>(`/news/${id}/`),
  create: (data: CreateNewsPayload, image?: File) => {
    if (!image) return api.post<NewsItem>('/news/', data)
    const fd = new FormData()
    appendNewsFields(fd, data)
    fd.append('image', image)
    return api.post<NewsItem>('/news/', fd)
  },
  update: (id: number, data: Partial<CreateNewsPayload>, image?: File) => {
    if (!image) return api.patch<NewsItem>(`/news/${id}/`, data)
    const fd = new FormData()
    appendNewsFields(fd, data)
    fd.append('image', image)
    return api.patch<NewsItem>(`/news/${id}/`, fd)
  },
  delete: (id: number) => api.delete(`/news/${id}/`),
}
