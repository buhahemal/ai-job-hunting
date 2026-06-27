import path from 'node:path';
import { fileURLToPath } from 'node:url';

const configDir = path.dirname(fileURLToPath(import.meta.url));
const packageRoot = path.resolve(configDir, '..');
const repoRoot = path.resolve(packageRoot, '../..');

/** Canonical paths relative to the repository root. */
export const PATHS = {
  repoRoot,
  dataDir: path.join(repoRoot, 'apps', 'api', 'data'),
  dataFile: path.join(repoRoot, 'apps', 'api', 'data', 'data.json'),
  dashboardDist: path.join(repoRoot, 'apps', 'dashboard', 'dist'),
} as const;
