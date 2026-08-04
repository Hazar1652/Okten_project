// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import basicSsl from '@vitejs/plugin-basic-ssl'

// Facebook Login забороняє FB.login з http-сторінок, тому для тесту OAuth
// запускайте дев-сервер по HTTPS: `VITE_HTTPS=1 npm run dev` (самопідписаний сертифікат).
const useHttps = process.env.VITE_HTTPS === '1'

export default defineConfig({
  plugins: [react(), ...(useHttps ? [basicSsl()] : [])],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
