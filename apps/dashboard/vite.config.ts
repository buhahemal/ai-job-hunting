import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { defineConfig, loadEnv } from 'vite';

/** GitHub Pages project-site base path; CI defaults match deploy-pages.yml. */
function resolveBasePath(env: Record<string, string>): string {
  if (env.VITE_BASE_PATH) {
    return env.VITE_BASE_PATH;
  }
  if (process.env.CI === 'true' && process.env.GITHUB_REPOSITORY) {
    const [, repo] = process.env.GITHUB_REPOSITORY.split('/');
    return `/${repo}/`;
  }
  return '/';
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const base = resolveBasePath(env);

  return {
    base,
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: 5173,
      proxy:
        env.VITE_USE_BACKEND === 'true'
          ? {
              '/api': {
                target: 'http://localhost:3000',
                changeOrigin: true,
              },
            }
          : undefined,
      hmr: process.env.DISABLE_HMR !== 'true',
      watch: process.env.DISABLE_HMR === 'true' ? null : {},
    },
  };
});
