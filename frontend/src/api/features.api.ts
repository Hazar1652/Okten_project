import api from './axiosInstance'
import type { PaginatedResponse, VenueFeature } from '../types/api'

export const featuresApi = {
  list: () => api.get<PaginatedResponse<VenueFeature>>('/venue-features/'),
}
