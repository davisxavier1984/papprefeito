import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Isso faz o Vite ouvir em todas as interfaces de rede, não apenas localhost
    host: true, 
    // Aqui você informa quais hosts são permitidos
    allowedHosts: [
      'maispap.dasix.site'
    ]
  }
})
