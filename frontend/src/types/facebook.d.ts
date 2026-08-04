export type FacebookLoginStatus = 'connected' | 'not_authorized' | 'unknown'

export type FacebookAuthResponse = {
  status: FacebookLoginStatus
  authResponse?: {
    accessToken: string
    expiresIn: number
    signedRequest: string
    userID: string
  }
}

type FacebookStatic = {
  init: (params: { appId: string; cookie: boolean; xfbml: boolean; version: string }) => void
  login: (
    callback: (response: FacebookAuthResponse) => void,
    options?: { scope?: string; return_scopes?: boolean },
  ) => void
}

declare global {
  interface Window {
    FB?: FacebookStatic
    fbAsyncInit?: () => void
  }
}

export {}
