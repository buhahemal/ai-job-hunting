# Dashboard

React + Vite app deployed to GitHub Pages (`apps/dashboard`).

## Commands

From repo root:

```bash
npm run dev
npm run dev:full    # proxy to Flask API
npm run typecheck
npm run lint
npm run test
npm run build
```

From this directory:

```bash
npm run dev
```

## Configuration

| Variable           | Default | Description                       |
| ------------------ | ------- | --------------------------------- |
| `VITE_BASE_PATH`   | `/`     | Asset base path for GitHub Pages  |
| `VITE_USE_BACKEND` | unset   | Set to `true` for local Flask API |

Paths are centralized in `@ai-job-hunter/config`.

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).
