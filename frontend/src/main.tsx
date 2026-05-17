import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './i18n'
import App from './App.tsx'

// Auto-recarga una vez por sesión si Vite/Vercel sirvió un chunk que ya no existe
// (típico tras un deploy nuevo con cliente que tenía la versión anterior cacheada).
const STALE_CHUNK_FLAG = 'levelup-chunk-reload'
window.addEventListener('unhandledrejection', (event) => {
  const msg = String(event.reason?.message ?? event.reason ?? '')
  if (
    (msg.includes('Failed to fetch dynamically imported module') ||
      msg.includes('Importing a module script failed') ||
      msg.includes('Loading chunk') ||
      msg.includes('Loading CSS chunk')) &&
    !sessionStorage.getItem(STALE_CHUNK_FLAG)
  ) {
    sessionStorage.setItem(STALE_CHUNK_FLAG, '1')
    window.location.reload()
  }
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
