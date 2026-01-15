import path from 'path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Icons from 'unplugin-icons/vite'

export default defineConfig({
  plugins: [
    vue(),
    Icons({
      autoInstall: true,
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  base: '/assets/personal_blog/frontend/',
  build: {
    outDir: '../personal_blog/public/frontend',
    emptyOutDir: true,
    target: 'es2015',
    modulePreload: {
      resolveDependencies: (filename, deps, { hostId, hostType }) => {
        return deps
      }
    },
    rollupOptions: {
      output: {
        entryFileNames: 'assets/index.js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name].[ext]',
      },
    },
  },
  experimental: {
    renderBuiltUrl(filename, { hostType }) {
      return '/assets/personal_blog/frontend/' + filename
    }
  },
  optimizeDeps: {
    include: ['frappe-ui', 'feather-icons', 'vue-router'],
  },
})
