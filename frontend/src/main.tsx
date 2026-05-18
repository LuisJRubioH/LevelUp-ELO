import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './i18n'
import App from './App.tsx'
import {
  isStaleChunkError,
  recoverFromStaleChunk,
  startStaleChunkFlagCleanup,
} from './lib/staleChunk'

// Recuperación automática ante chunks viejos tras un deploy de Vercel.
// Ver lib/staleChunk.ts para la estrategia escalonada (reload → SW+caches → giveup).
window.addEventListener('unhandledrejection', (event) => {
  if (isStaleChunkError(event.reason)) {
    if (recoverFromStaleChunk()) event.preventDefault()
  }
})
window.addEventListener('error', (event) => {
  if (isStaleChunkError(event.error ?? event.message)) {
    if (recoverFromStaleChunk()) event.preventDefault()
  }
})
startStaleChunkFlagCleanup()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
