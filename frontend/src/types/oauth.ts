export interface OAuthConfig {
  google_enabled: boolean
  facebook_enabled: boolean
  google_client_id: string
  facebook_app_id: string
}

export interface OAuthLoginResponse {
  access: string
  refresh: string
  user: import('./api').User
  is_new: boolean
}
