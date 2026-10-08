import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // The FastAPI backend (backend/main.py) runs on port 8000; same-origin /api keeps the login cookie simple.
    // API_PORT overrides the port (e.g. if 8000 is busy); the assignment's default is 8000.
    proxy: { '/api': `http://127.0.0.1:${process.env.API_PORT ?? '8000'}` },
  },
})
