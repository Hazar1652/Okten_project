import api from './axiosInstance'
import type { PaginatedResponse, User } from '../types/api'

export type AdminUser = User & { is_active: boolean }

export const usersApi = {
  me: () => api.get<User>('/users/me/'),
  updateMe: (data: FormData | Partial<User>) => {
    if (data instanceof FormData) {
      return api.patch<User>('/users/me/', data)
    }
    return api.patch<User>('/users/me/', data)
  },
  adminList: (params?: { search?: string; role?: string; is_active?: boolean }) =>
    api.get<PaginatedResponse<AdminUser>>('/users/admin/', { params }),
  adminUpdate: (id: number, data: Partial<AdminUser>) =>
    api.patch<AdminUser>(`/users/admin/${id}/`, data),
  adminDeactivate: (id: number) => api.delete(`/users/admin/${id}/`),
  adminDelete: (id: number) => api.delete(`/users/admin/${id}/hard-delete/`),
}
