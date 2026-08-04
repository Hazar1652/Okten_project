import api from './axiosInstance'
import type { PaginatedResponse, Tag } from '../types/api'

export const tagsApi = {
  list: () => api.get<PaginatedResponse<Tag>>('/tags/'),
}
