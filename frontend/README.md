# Frontend (Dashboard)

React + Vite dashboard deployed to GitHub Pages.

## Commands

```bash
npm install
npm run dev          # static mode (reads data/data.json)
VITE_USE_BACKEND=true npm run dev   # proxy to Flask
npm run typecheck
npm run lint
npm run test
npm run build
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_BASE_PATH` | `/` | Asset base path for GitHub Pages |
| `VITE_USE_BACKEND` | unset | Set to `true` for local Flask API |

## Known Limitations

- Profile and job status changes on GitHub Pages persist in `localStorage` only.

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).
