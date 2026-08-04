const FB_SDK_URL = 'https://connect.facebook.net/en_US/sdk.js'
const FB_API_VERSION = 'v21.0'

let fbLoadPromise: Promise<void> | null = null
let fbAppId: string | null = null

export function loadFacebookSdk(appId: string): Promise<void> {
  if (typeof window === 'undefined') return Promise.resolve()

  if (window.FB && fbAppId === appId) {
    return Promise.resolve()
  }

  if (fbLoadPromise && fbAppId === appId) {
    return fbLoadPromise
  }

  fbAppId = appId
  fbLoadPromise = new Promise((resolve, reject) => {
    const timeout = window.setTimeout(() => {
      reject(
        new Error(
          'Facebook SDK не завантажився. Вимкніть AdBlock або додайте localhost у Meta App → Settings.',
        ),
      )
    }, 15000)

    const finishOk = () => {
      window.clearTimeout(timeout)
      resolve()
    }

    const finishErr = (message: string) => {
      window.clearTimeout(timeout)
      fbLoadPromise = null
      reject(new Error(message))
    }

    window.fbAsyncInit = () => {
      try {
        window.FB?.init({
          appId,
          cookie: true,
          xfbml: false,
          version: FB_API_VERSION,
        })
        finishOk()
      } catch {
        finishErr('Помилка ініціалізації Facebook SDK.')
      }
    }

    const existing = document.getElementById('facebook-jssdk')
    if (existing) {
      if (window.FB) {
        window.fbAsyncInit()
        return
      }
      existing.addEventListener('load', () => {
        if (window.FB) finishOk()
      })
      existing.addEventListener('error', () =>
        finishErr('Не вдалося завантажити Facebook SDK (блокувальник реклами?).'),
      )
      return
    }

    const script = document.createElement('script')
    script.id = 'facebook-jssdk'
    script.async = true
    script.defer = true
    script.crossOrigin = 'anonymous'
    script.src = FB_SDK_URL
    script.onerror = () =>
      finishErr('Не вдалося завантажити Facebook SDK. Перевірте інтернет і AdBlock.')
    document.body.appendChild(script)
  })

  return fbLoadPromise
}

function loginErrorMessage(status?: string): string {
  switch (status) {
    case 'not_authorized':
      return 'Дозвольте доступ додатку у вікні Facebook.'
    case 'unknown':
      return (
        'Facebook не авторизував. У Meta App додайте себе як Admin/Developer і вкажіть Site URL http://localhost'
      )
    default:
      return 'Вхід через Facebook скасовано.'
  }
}

export function facebookLogin(): Promise<string> {
  return new Promise((resolve, reject) => {
    if (!window.FB) {
      reject(new Error('Facebook SDK не готовий. Оновіть сторінку.'))
      return
    }

    window.FB.login(
      (response) => {
        if (response.status === 'connected' && response.authResponse?.accessToken) {
          resolve(response.authResponse.accessToken)
          return
        }
        reject(new Error(loginErrorMessage(response.status)))
      },
      { scope: 'public_profile,email', return_scopes: true },
    )
  })
}
