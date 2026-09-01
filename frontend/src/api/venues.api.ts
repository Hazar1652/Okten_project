import api from './axiosInstance'
import type { PaginatedResponse, Venue, VenueListParams } from '../types/api'

export interface CreateVenuePayload {
  name: string
  venue_type?: string
  description?: string
  address: string
  latitude: string
  longitude: string
  phone_number?: string
  email?: string
  website?: string
  avg_check?: string
  work_time?: Record<string, unknown>
  tag_ids?: number[]
  feature_ids?: number[]
  owner_id?: number
  status?: string
}

export function sanitizeVenuePayload<T extends Partial<CreateVenuePayload>>(data: T): T {
  const out = { ...data }
  for (const key of ['email', 'phone_number', 'avg_check', 'description'] as const) {
    if (out[key] === '') {
      delete out[key]
    }
  }
  return out
}

function buildListQuery(params?: VenueListParams): string {
  const sp = new URLSearchParams()
  if (!params) return ''
  if (params.search) sp.set('search', params.search)
  if (params.min_rating != null) sp.set('min_rating', String(params.min_rating))
  if (params.min_avg_check != null) sp.set('min_avg_check', String(params.min_avg_check))
  if (params.max_avg_check != null) sp.set('max_avg_check', String(params.max_avg_check))
  if (params.ordering) sp.set('ordering', params.ordering)
  if (params.venue_type) sp.set('venue_type', params.venue_type)
  if (params.status) sp.set('status', params.status)
  if (params.mine) sp.set('mine', '1')
  if (params.ref_lat != null) sp.set('ref_lat', String(params.ref_lat))
  if (params.ref_lng != null) sp.set('ref_lng', String(params.ref_lng))
  if (params.page != null) sp.set('page', String(params.page))
  params.tags?.forEach((id) => sp.append('tags', String(id)))
  params.features?.forEach((id) => sp.append('features', String(id)))
  const q = sp.toString()
  return q ? `?${q}` : ''
}

function appendFormFields(fd: FormData, data: Partial<CreateVenuePayload>) {
  const clean = sanitizeVenuePayload(data)
  Object.entries(clean).forEach(([key, value]) => {
    if (value === undefined || value === null) return
    if (key === 'tag_ids' || key === 'feature_ids') {
      ;(value as number[]).forEach((id) => fd.append(key, String(id)))
      return
    }
    if (key === 'work_time') {
      fd.append(key, JSON.stringify(value))
      return
    }
    fd.append(key, String(value))
  })
}

function jsonVenuePayload(data: Partial<CreateVenuePayload>) {
  const clean = sanitizeVenuePayload(data)
  const out: Record<string, unknown> = { ...clean }
  if (clean.tag_ids) out.tag_ids = clean.tag_ids
  if (clean.feature_ids) out.feature_ids = clean.feature_ids
  return out
}

export const venuesApi = {
  list: (params?: VenueListParams) =>
    api.get<PaginatedResponse<Venue>>(`/venues/${buildListQuery(params)}`),
  listMine: () => api.get<PaginatedResponse<Venue>>('/venues/?mine=1'),
  get: (id: number) => api.get<Venue>(`/venues/${id}/`),
  create: (data: CreateVenuePayload, image?: File) => {
    if (!image) {
      return api.post<Venue>('/venues/', jsonVenuePayload(data))
    }
    const fd = new FormData()
    appendFormFields(fd, data)
    fd.append('main_image', image)
    return api.post<Venue>('/venues/', fd)
  },
  update: (id: number, data: Partial<CreateVenuePayload>, image?: File) => {
    if (!image) {
      return api.patch<Venue>(`/venues/${id}/`, jsonVenuePayload(data))
    }
    const fd = new FormData()
    appendFormFields(fd, data)
    fd.append('main_image', image)
    return api.patch<Venue>(`/venues/${id}/`, fd)
  },
  submit: (id: number) => api.post<Venue>(`/venues/${id}/submit/`),
  approve: (id: number) => api.post<Venue>(`/venues/${id}/approve/`, {}),
  reject: (id: number) => api.post<Venue>(`/venues/${id}/reject/`, {}),
  delete: (id: number) => api.delete(`/venues/${id}/`),
}
