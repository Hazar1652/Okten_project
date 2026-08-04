import { useEffect, useState } from 'react'
import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google'
import { authApi } from '../api/auth.api'
import { useAuth } from '../store/authContext'
import type { OAuthConfig } from '../types/oauth'
import { facebookLogin, loadFacebookSdk } from '../utils/facebookSdk'

type Props = {
  onSuccess: () => void
  onError: (message: string) => void
  disabled?: boolean
}

function OAuthButtonsInner({ config, onSuccess, onError, disabled }: Props & { config: OAuthConfig }) {
  const { oauthLogin } = useAuth()
  const [fbReady, setFbReady] = useState(false)

  const [fbError, setFbError] = useState('')

  useEffect(() => {
    if (!config.facebook_enabled || !config.facebook_app_id) return
    setFbError('')
    loadFacebookSdk(config.facebook_app_id)
      .then(() => setFbReady(true))
      .catch((err: unknown) => {
        setFbReady(false)
        setFbError(err instanceof Error ? err.message : 'Facebook SDK не завантажився.')
      })
  }, [config.facebook_app_id, config.facebook_enabled])

  const handleGoogle = async (idToken: string) => {
    try {
      await oauthLogin('google', idToken)
      onSuccess()
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      onError(detail ?? 'Не вдалося увійти через Google.')
    }
  }

  const handleFacebook = async () => {
    try {
      const token = await facebookLogin()
      await oauthLogin('facebook', token)
      onSuccess()
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      onError(
        detail ?? (err instanceof Error ? err.message : 'Не вдалося увійти через Facebook.'),
      )
    }
  }

  if (!config.google_enabled && !config.facebook_enabled) {
    return (
      <p className="muted oauth-hint">
        OAuth не налаштовано. Додайте <code>GOOGLE_OAUTH_CLIENT_ID</code> та/або{' '}
        <code>FACEBOOK_APP_ID</code> у <code>backend/.env</code>.
      </p>
    )
  }

  return (
    <div className="oauth-block">
      <p className="oauth-divider">
        <span>або</span>
      </p>
      <div className="oauth-buttons">
        {config.google_enabled && config.google_client_id && (
          <GoogleLogin
            onSuccess={(res) => {
              if (res.credential) void handleGoogle(res.credential)
              else onError('Google не повернув токен.')
            }}
            onError={() => onError('Помилка Google OAuth.')}
            theme="outline"
            size="large"
            width={400}
            text="continue_with"
            useOneTap={false}
          />
        )}
        {config.facebook_enabled && config.facebook_app_id && (
          <>
            <button
              type="button"
              className="btn btn-oauth btn-oauth-facebook"
              disabled={disabled || !fbReady}
              onClick={() => void handleFacebook()}
            >
              {fbReady ? 'Продовжити з Facebook' : 'Facebook…'}
            </button>
            {fbError && <p className="error">{fbError}</p>}
          </>
        )}
      </div>
    </div>
  )
}

export default function OAuthButtons(props: Props) {
  const [config, setConfig] = useState<OAuthConfig | null>(null)

  useEffect(() => {
    authApi
      .oauthConfig()
      .then((res) => setConfig(res.data))
      .catch(() =>
        setConfig({
          google_enabled: false,
          facebook_enabled: false,
          google_client_id: '',
          facebook_app_id: '',
        }),
      )
  }, [])

  if (!config) {
    return <p className="muted oauth-hint">Завантаження OAuth…</p>
  }

  if (config.google_enabled && config.google_client_id) {
    return (
      <GoogleOAuthProvider clientId={config.google_client_id}>
        <OAuthButtonsInner {...props} config={config} />
      </GoogleOAuthProvider>
    )
  }

  return <OAuthButtonsInner {...props} config={config} />
}
