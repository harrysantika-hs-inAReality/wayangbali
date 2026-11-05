import { defineConfig } from 'vite';

// `npm run serve-all` starts PHP on PHP_PORT; forward the PHP endpoints to it.
// changeOrigin stays false so tutor.php's same-origin check sees the Vite host.
const php = `http://127.0.0.1:${process.env.PHP_PORT ?? '8124'}`;

export default defineConfig({
  server: {
    proxy: {
      '/tutor.php': php,
      '/queue.php': php,
    },
  },
});
