import api from './axiosInstance'
import type { PaginatedResponse } from '../types/api'

export interface SitePage {
  id: number
  slug: string
  title: string
  content: string
  updated_at?: string
}

export interface TopCategory {
  id: number
  name: string
  tag_id: number | null
  tag_name: string | null
  order: number
  is_active: boolean
}

export const cmsApi = {
  listPages: () => api.get<PaginatedResponse<SitePage>>('/pages/'),
  getPage: (slug: string) => api.get<SitePage>(`/pages/${slug}/`),
  updatePage: (slug: string, data: Partial<SitePage>) =>
    api.patch<SitePage>(`/pages/${slug}/`, data),
  listTopCategories: () => api.get<PaginatedResponse<TopCategory>>('/top-categories/'),
  createTopCategory: (data: Partial<TopCategory>) =>
    api.post<TopCategory>('/top-categories/', data),
  updateTopCategory: (id: number, data: Partial<TopCategory>) =>
    api.patch<TopCategory>(`/top-categories/${id}/`, data),
  deleteTopCategory: (id: number) => api.delete(`/top-categories/${id}/`),
}
