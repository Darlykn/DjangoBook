import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  base: '/static/dist/',
  server: {
    host: 'localhost',
    port: 5173,
    origin: 'http://localhost:5173',
  },
  build: {
    outDir: resolve(__dirname, '../django_shop/django_shop/static/dist'),
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: resolve(__dirname, 'src/main.js'),
    },
  },
});

