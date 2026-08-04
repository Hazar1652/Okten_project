import api, { tokenStorage } from './axiosInstance'
import type { OAuthConfig, OAuthLoginResponse } from '../types/oauth'
import type { RegisterResponse, TokenPair } from '../types/api'

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  username: string
  email: string
  password: string
  password_confirm: string
  first_name?: string
  last_name?: string
}

export const authApi = {
  oauthConfig: () => api.get<OAuthConfig>('/auth/oauth-config/'),
  login: (data: LoginPayload) => api.post<TokenPair>('/auth/token/', data),
  register: (data: RegisterPayload) => api.post<RegisterResponse>('/auth/register/', data),
  loginWithGoogle: async (id_token: string) => {
    const { data } = await api.post<OAuthLoginResponse>('/auth/google/', { id_token })
    tokenStorage.setTokens(data.access, data.refresh)
    return data
  },
  loginWithFacebook: async (access_token: string) => {
    const { data } = await api.post<OAuthLoginResponse>('/auth/facebook/', { access_token })
    tokenStorage.setTokens(data.access, data.refresh)
    return data
  },
}
